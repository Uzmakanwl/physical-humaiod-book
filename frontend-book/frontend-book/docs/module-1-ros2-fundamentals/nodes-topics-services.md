---
sidebar_position: 3
title: 'ROS 2 Communication Model: Nodes, Topics, Services, and Actions'
---

# ROS 2 Communication Model: Nodes, Topics, Services, and Actions

## Introduction

The communication model in ROS 2 is fundamental to how different parts of a robotic system interact. Understanding these communication patterns is crucial for building effective Physical AI systems.

## Nodes

A **node** is an executable that uses ROS 2 to communicate with other nodes. Nodes are the basic building blocks of a ROS 2 system, and they can be thought of as individual processes that perform specific tasks.

### Characteristics of Nodes:
- Each node runs a specific task
- Nodes communicate with other nodes through messages
- Multiple nodes can run simultaneously
- Nodes can be written in different programming languages

### Creating a Node Example:
```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node_name')
        # Initialize node-specific functionality here
        self.get_logger().info('MyNode has been started')

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## Topics and Publish/Subscribe Model

**Topics** enable asynchronous communication between nodes using a publish/subscribe pattern. One or more nodes publish messages to a topic, and other nodes subscribe to that topic to receive the messages.

### Key Features:
- **Asynchronous**: Publishers and subscribers don't need to be synchronized
- **Loose Coupling**: Publishers don't need to know about subscribers and vice versa
- **Data Flow**: Information flows from publishers to subscribers

### Publisher Example:
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1
```

### Subscriber Example:
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')
```

## Services and Request/Response Model

**Services** provide synchronous communication between nodes using a request/response pattern. A client node sends a request to a service, and the service node processes the request and returns a response.

### Key Features:
- **Synchronous**: The client waits for a response from the service
- **Tight Coupling**: Client and service must be aware of each other
- **One-to-One**: One client request results in one service response

### Service Example:
```python
# Service definition in .srv file (AddTwoInts.srv):
# int64 a
# int64 b
# ---
# int64 sum

# Service Server
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning: {request.a} + {request.b} = {response.sum}')
        return response

# Service Client
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts
import sys

class MinimalClient(Node):
    def __init__(self):
        super().__init__('minimal_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()
```

## Actions

**Actions** are used for long-running tasks that may need feedback and the ability to cancel. They combine the features of services and topics, providing request/response functionality with continuous feedback.

### Key Features:
- **Long-running**: Suitable for tasks that take time to complete
- **Feedback**: Provides ongoing status updates
- **Cancelability**: Tasks can be cancelled before completion

### Action Example:
```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

            goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        return result
```

## Publish/Subscribe Data Flow and Basic Reply-Based Agents

The publish/subscribe model enables distributed systems where nodes can broadcast information without knowing who will receive it. This pattern is particularly useful for:

- Sensor data distribution
- Status updates
- Event notifications
- Broadcasting commands to multiple recipients

### Example of a Reply-Based Agent:
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ReplyAgent(Node):
    def __init__(self):
        super().__init__('reply_agent')
        self.subscription = self.create_subscription(
            String,
            'input_topic',
            self.listener_callback,
            10)
        self.publisher = self.create_publisher(String, 'output_topic', 10)

    def listener_callback(self, msg):
        # Process the incoming message
        response = f"Processed: {msg.data}"

        # Publish the response
        response_msg = String()
        response_msg.data = response
        self.publisher.publish(response_msg)
        self.get_logger().info(f'Replied with: "{response_msg.data}"')
```

## Sensor-to-Controller Communication Examples

In Physical AI systems, sensors and controllers communicate through various patterns:

1. **Direct Communication**: Sensors publish directly to controllers
2. **Processing Nodes**: Sensor data is processed before reaching controllers
3. **Feedback Loops**: Controllers send status back to sensors or processing nodes

### Example: Camera Sensor to Motion Controller
```python
# Camera sensor node
class CameraSensor(Node):
    def __init__(self):
        super().__init__('camera_sensor')
        self.publisher = self.create_publisher(Image, 'camera/image_raw', 10)

# Object detection node
class ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector')
        self.subscription = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(Detection, 'detected_objects', 10)

# Motion controller node
class MotionController(Node):
    def __init__(self):
        super().__init__('motion_controller')
        self.subscription = self.create_subscription(
            Detection, 'detected_objects', self.detection_callback, 10)
```

## Summary

ROS 2 provides multiple communication patterns to suit different needs:
- **Topics** for asynchronous, broadcast communication
- **Services** for synchronous request/response interactions
- **Actions** for long-running tasks with feedback

Understanding these patterns is essential for designing effective Physical AI systems that can coordinate complex behaviors.

## Practical Exercises

1. Create a publisher that sends temperature readings every second
2. Create a subscriber that receives and processes the temperature data
3. Implement a service that converts temperature units (Celsius to Fahrenheit)
4. Build a simple action server that simulates a robot moving to a goal position