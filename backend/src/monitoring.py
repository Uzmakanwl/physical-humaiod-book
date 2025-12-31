"""
Monitoring and metrics collection module for the embedding pipeline.

This module provides performance monitoring, metrics collection,
and system health tracking for the pipeline components.
"""

import time
import threading
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
from collections import deque

from src.logger import get_logger


@dataclass
class PerformanceMetric:
    """Data class for performance metrics."""
    operation: str
    duration: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class MetricsCollector:
    """Collects and manages performance metrics for the pipeline."""

    def __init__(self, max_metrics: int = 1000):
        """
        Initialize the metrics collector.

        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_metrics = max_metrics
        self.metrics = deque(maxlen=max_metrics)
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)

    def record_metric(self, operation: str, duration: float, success: bool = True, error_message: Optional[str] = None):
        """
        Record a performance metric.

        Args:
            operation: Name of the operation being measured
            duration: Duration of the operation in seconds
            success: Whether the operation was successful
            error_message: Error message if operation failed
        """
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message
        )

        with self.lock:
            self.metrics.append(metric)

        self.logger.debug(f"Recorded metric: {operation}, duration: {duration:.3f}s, success: {success}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected metrics.

        Returns:
            Dictionary with metrics summary
        """
        with self.lock:
            if not self.metrics:
                return {
                    'total_operations': 0,
                    'success_rate': 0.0,
                    'avg_duration': 0.0,
                    'min_duration': 0.0,
                    'max_duration': 0.0,
                    'operations_by_type': {}
                }

            total_ops = len(self.metrics)
            successful_ops = sum(1 for m in self.metrics if m.success)
            durations = [m.duration for m in self.metrics]

            # Group metrics by operation type
            ops_by_type = {}
            for metric in self.metrics:
                op_type = metric.operation
                if op_type not in ops_by_type:
                    ops_by_type[op_type] = []
                ops_by_type[op_type].append(metric)

            # Calculate stats for each operation type
            ops_stats = {}
            for op_type, metrics_list in ops_by_type.items():
                durations = [m.duration for m in metrics_list]
                successful = sum(1 for m in metrics_list if m.success)
                ops_stats[op_type] = {
                    'count': len(metrics_list),
                    'success_rate': successful / len(metrics_list) if metrics_list else 0,
                    'avg_duration': statistics.mean(durations) if durations else 0,
                    'min_duration': min(durations) if durations else 0,
                    'max_duration': max(durations) if durations else 0
                }

            return {
                'total_operations': total_ops,
                'success_rate': successful_ops / total_ops if total_ops > 0 else 0,
                'avg_duration': statistics.mean(durations) if durations else 0,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'operations_by_type': ops_stats
            }

    def get_recent_metrics(self, minutes: int = 10) -> list:
        """
        Get metrics from the last specified number of minutes.

        Args:
            minutes: Number of minutes to look back

        Returns:
            List of recent metrics
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            recent = [m for m in self.metrics if m.timestamp >= cutoff_time]
            return recent

    def clear_metrics(self):
        """Clear all collected metrics."""
        with self.lock:
            self.metrics.clear()
        self.logger.info("Cleared all performance metrics")


class PerformanceMonitor:
    """Monitors performance of pipeline operations."""

    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(__name__)

    def time_function(self, operation_name: str) -> Callable:
        """
        Decorator to time function execution and record metrics.

        Args:
            operation_name: Name to use for the operation in metrics

        Returns:
            Decorated function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.metrics_collector.record_metric(operation_name, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.metrics_collector.record_metric(operation_name, duration, success=False, error_message=str(e))
                    raise
            return wrapper
        return decorator

    def measure_operation(self, operation_name: str, operation_func: Callable, *args, **kwargs) -> Any:
        """
        Measure the execution of an operation.

        Args:
            operation_name: Name of the operation for metrics
            operation_func: Function to execute and measure
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the operation
        """
        start_time = time.time()
        try:
            result = operation_func(*args, **kwargs)
            duration = time.time() - start_time
            self.metrics_collector.record_metric(operation_name, duration, success=True)
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Operation {operation_name} failed: {str(e)}")
            self.metrics_collector.record_metric(operation_name, duration, success=False, error_message=str(e))
            raise

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health metrics.

        Returns:
            Dictionary with system health information
        """
        metrics_summary = self.metrics_collector.get_metrics_summary()

        # Calculate additional health indicators
        recent_metrics = self.metrics_collector.get_recent_metrics(minutes=5)
        recent_error_rate = 1 - (sum(1 for m in recent_metrics if m.success) / len(recent_metrics) if recent_metrics else 0)

        return {
            'timestamp': datetime.now(),
            'metrics_summary': metrics_summary,
            'recent_error_rate': recent_error_rate,
            'recent_operation_count': len(recent_metrics),
            'system_status': 'healthy' if recent_error_rate < 0.1 else 'degraded' if recent_error_rate < 0.3 else 'unhealthy'
        }

    def get_operation_performance(self, operation_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific operation.

        Args:
            operation_name: Name of the operation to analyze

        Returns:
            Dictionary with operation performance metrics
        """
        with self.metrics_collector.lock:
            ops = [m for m in self.metrics_collector.metrics if m.operation == operation_name]

            if not ops:
                return {
                    'operation': operation_name,
                    'count': 0,
                    'success_rate': 0.0,
                    'avg_duration': 0.0,
                    'min_duration': 0.0,
                    'max_duration': 0.0
                }

            successful_ops = [m for m in ops if m.success]
            durations = [m.duration for m in successful_ops]

            return {
                'operation': operation_name,
                'count': len(ops),
                'success_rate': len(successful_ops) / len(ops) if ops else 0,
                'avg_duration': statistics.mean(durations) if durations else 0,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'error_count': len(ops) - len(successful_ops)
            }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance.

    Returns:
        PerformanceMonitor instance
    """
    return performance_monitor


def monitor_operation(operation_name: str):
    """
    Context manager to monitor an operation.

    Args:
        operation_name: Name of the operation to monitor
    """
    class MonitorOperation:
        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            success = exc_type is None
            error_message = str(exc_val) if exc_type else None

            performance_monitor.metrics_collector.record_metric(
                operation_name, duration, success, error_message
            )

    return MonitorOperation()