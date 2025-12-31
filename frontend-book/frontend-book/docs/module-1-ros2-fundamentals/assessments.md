---
sidebar_position: 5
title: 'Assessments and Quizzes'
---

# Assessments and Quizzes for Module 1

## Chapter 1: ROS 2 Basics Assessment

### Quiz: ROS 2 Fundamentals

1. What does ROS 2 stand for?
   - A) Robot Operating System 2
   - B) Robotic Operations Suite 2
   - C) Robot Operating Software 2
   - D) Remote Operating System 2

   **Answer: A**

2. What underlying communication middleware does ROS 2 use?
   - A) XML-RPC
   - B) DDS (Data Distribution Service)
   - C) HTTP
   - D) MQTT

   **Answer: B**

3. Which of the following is NOT a communication pattern in ROS 2?
   - A) Topics
   - B) Services
   - C) Actions
   - D) Databases

   **Answer: D**

### Practical Exercise: Basic Publisher/Subscriber

Create a simple publisher that publishes the current time every second and a subscriber that logs the received time to the console.

**Solution:**
```python
# publisher
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class TimePublisher(Node):
    def __init__(self):
        super().__init__('time_publisher')
        self.publisher = self.create_publisher(String, 'time_topic', 10)
        timer_period = 1.0
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f'Current time: {time.time()}'
        self.publisher.publish(msg)

# subscriber
class TimeSubscriber(Node):
    def __init__(self):
        super().__init__('time_subscriber')
        self.subscription = self.create_subscription(
            String, 'time_topic', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info(f'Received time: {msg.data}')
```

## Chapter 2: Communication Model Assessment

### Quiz: Communication Patterns

1. What is the main difference between topics and services in ROS 2?
   - A) Topics are synchronous, services are asynchronous
   - B) Topics are asynchronous, services are synchronous
   - C) There is no difference
   - D) Topics use TCP, services use UDP

   **Answer: B**

2. Which communication pattern is best suited for long-running tasks that require feedback?
   - A) Topics
   - B) Services
   - C) Actions
   - D) Parameters

   **Answer: C**

3. What does DDS stand for in the context of ROS 2?
   - A) Distributed Data System
   - B) Data Distribution Service
   - C) Dynamic Discovery System
   - D) Decentralized Data Service

   **Answer: B**

### Practical Exercise: Service Implementation

Create a service that takes two integers as input and returns their sum.

## Chapter 3: Python Integration Assessment

### Quiz: Python and ROS 2

1. What is the Python client library for ROS 2 called?
   - A) rospy
   - B) rclpy
   - C) roslibpy
   - D) pyros

   **Answer: B**

2. In URDF, what defines the connection between two links?
   - A) Links
   - B) Joints
   - C) Materials
   - D) Transforms

   **Answer: B**

3. Which URDF joint type allows continuous rotation?
   - A) Fixed
   - B) Revolute
   - C) Continuous
   - D) Prismatic

   **Answer: C**

### Practical Exercise: URDF Robot Model

Create a URDF model for a simple wheeled robot with a rectangular base and two wheels.

## Hands-On Projects

### Project 1: Obstacle Avoiding Robot

Create a Python node that:
1. Subscribes to laser scan data
2. Implements a simple obstacle avoidance algorithm
3. Publishes velocity commands to control the robot

### Project 2: Multi-Agent System

Create two Python nodes that:
1. One node publishes sensor data (simulated)
2. Another node subscribes to the data and responds with control commands
3. Implement proper error handling and logging

### Project 3: AI-ROS Integration

Create a node that:
1. Receives camera images
2. Applies a simple image processing algorithm (e.g., edge detection)
3. Publishes the processed image to another topic

## Answer Key

### Chapter 1 Answers:
1. A - Robot Operating System 2
2. B - DDS (Data Distribution Service)
3. D - Databases

### Chapter 2 Answers:
1. B - Topics are asynchronous, services are synchronous
2. C - Actions
3. B - Data Distribution Service

### Chapter 3 Answers:
1. B - rclpy
2. B - Joints
3. C - Continuous

## Grading Rubric

- Quiz Questions: 2 points each (6 points total per chapter)
- Practical Exercises: 5 points each (based on functionality, code quality, and documentation)
- Hands-on Projects: 10 points each (based on complexity, implementation, and innovation)

**Passing Score**: 80% or higher