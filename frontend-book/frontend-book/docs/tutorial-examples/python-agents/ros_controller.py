#!/usr/bin/env python3
"""
ROS Controller Example

This example demonstrates how to create a ROS 2 controller node
that bridges AI logic with ROS controllers for robot control.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import math


class ROSController(Node):
    """
    A controller node that implements basic robot control logic
    combining sensor input with control commands
    """

    def __init__(self):
        super().__init__('ros_controller')

        # Publisher for velocity commands
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Subscriber for laser scan data (simulating sensor input)
        self.scan_subscriber = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)

        # Subscriber for high-level commands
        self.command_subscriber = self.create_subscription(
            String, 'controller_commands', self.command_callback, 10)

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Robot state variables
        self.scan_data = None
        self.current_behavior = 'idle'  # idle, exploring, avoiding, following
        self.cmd_vel_msg = Twist()
        self.last_obstacle_distance = float('inf')

        self.get_logger().info('ROS Controller node initialized')

    def scan_callback(self, msg):
        """Callback function that processes incoming laser scan data"""
        self.scan_data = msg.ranges

    def command_callback(self, msg):
        """Callback function that processes high-level commands"""
        command = msg.data.lower().strip()

        if command == 'start_exploring':
            self.current_behavior = 'exploring'
            self.get_logger().info('Switched to exploring behavior')
        elif command == 'start_avoiding':
            self.current_behavior = 'avoiding'
            self.get_logger().info('Switched to obstacle avoidance behavior')
        elif command == 'stop':
            self.current_behavior = 'idle'
            self.stop_robot()
            self.get_logger().info('Switched to idle behavior')
        else:
            self.get_logger().info(f'Unknown command: {command}')

    def control_loop(self):
        """Main control loop that processes sensor data and generates commands"""
        if self.scan_data is None:
            return

        # Process the control logic based on current behavior
        if self.current_behavior == 'idle':
            self.stop_robot()
        elif self.current_behavior == 'exploring':
            self.exploring_behavior()
        elif self.current_behavior == 'avoiding':
            self.obstacle_avoidance_behavior()

        # Publish the velocity command
        self.cmd_vel_publisher.publish(self.cmd_vel_msg)

    def exploring_behavior(self):
        """Simple exploration behavior - move forward with obstacle avoidance"""
        # Get front distance (simplified - just get the middle range)
        front_ranges = self.scan_data[330:30] + self.scan_data[330:]  # Front 60 degrees
        valid_ranges = [d for d in front_ranges if not math.isnan(d) and d > 0.1]

        if valid_ranges:
            min_front_dist = min(valid_ranges)
            self.last_obstacle_distance = min_front_dist
        else:
            min_front_dist = float('inf')

        # Simple exploration with obstacle avoidance
        if min_front_dist > 0.5:  # Safe to move forward
            self.cmd_vel_msg.linear.x = 0.2  # Move forward
            self.cmd_vel_msg.angular.z = 0.0  # No turn
        else:  # Obstacle detected
            self.cmd_vel_msg.linear.x = 0.0  # Stop moving forward
            self.cmd_vel_msg.angular.z = 0.5  # Turn right

    def obstacle_avoidance_behavior(self):
        """More sophisticated obstacle avoidance"""
        if self.scan_data:
            # Get ranges for different directions
            front_ranges = self.scan_data[330:30] + self.scan_data[330:]  # Front 60 degrees
            left_ranges = self.scan_data[60:120]  # Left side
            right_ranges = self.scan_data[240:300]  # Right side

            # Filter valid ranges
            front_valid = [d for d in front_ranges if not math.isnan(d) and d > 0.1]
            left_valid = [d for d in left_ranges if not math.isnan(d) and d > 0.1]
            right_valid = [d for d in right_ranges if not math.isnan(d) and d > 0.1]

            min_front = min(front_valid) if front_valid else float('inf')
            min_left = min(left_valid) if left_valid else float('inf')
            min_right = min(right_valid) if right_valid else float('inf')

            # Obstacle avoidance logic
            if min_front > 0.6:  # Clear path ahead
                self.cmd_vel_msg.linear.x = 0.2
                self.cmd_vel_msg.angular.z = 0.0
            elif min_right > min_left:  # More space on the right
                self.cmd_vel_msg.linear.x = 0.1
                self.cmd_vel_msg.angular.z = -0.3  # Turn right
            else:  # More space on the left
                self.cmd_vel_msg.linear.x = 0.1
                self.cmd_vel_msg.angular.z = 0.3  # Turn left

    def stop_robot(self):
        """Stop the robot by setting velocities to zero"""
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.angular.z = 0.0

    def get_logger_info(self):
        """Get current status information for logging"""
        return f"Behavior: {self.current_behavior}, Front dist: {self.last_obstacle_distance:.2f}"


def main(args=None):
    """Main function to initialize and run the controller node"""
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the controller node
    ros_controller = ROSController()

    try:
        # Keep the node running
        rclpy.spin(ros_controller)
    except KeyboardInterrupt:
        ros_controller.get_logger().info('Shutting down ROS Controller')
    finally:
        # Clean up
        ros_controller.stop_robot()
        ros_controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()