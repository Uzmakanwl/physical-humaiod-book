---
sidebar_position: 4
title: 'Python Agents & ROS Integration with URDF Basics'
---

# Python Agents & ROS Integration with URDF Basics

## Introduction

Python is one of the most popular languages for robotics and AI development. With the `rclpy` library, Python developers can create ROS 2 nodes and integrate AI logic with ROS controllers. This chapter covers how to create Python agents and work with URDF (Unified Robot Description Format) for robot structure definition.

## rclpy-based Python Agents

`rclpy` is the Python client library for ROS 2. It provides the standard interface for Python programs to interact with ROS 2.

### Basic Node Structure

```python
import rclpy
from rclpy.node import Node

class MyPythonAgent(Node):
    def __init__(self):
        super().__init__('my_python_agent')

        # Create publishers, subscribers, services, etc.
        self.publisher = self.create_publisher(String, 'agent_output', 10)
        self.subscription = self.create_subscription(
            String, 'agent_input', self.input_callback, 10)

        self.get_logger().info('Python agent initialized')

    def input_callback(self, msg):
        # Process input message
        self.get_logger().info(f'Received: {msg.data}')

        # Process with AI logic
        result = self.ai_processing_function(msg.data)

        # Publish result
        output_msg = String()
        output_msg.data = result
        self.publisher.publish(output_msg)

    def ai_processing_function(self, input_data):
        # Your AI logic here
        return f"Processed: {input_data}"

def main(args=None):
    rclpy.init(args=args)
    agent = MyPythonAgent()

    try:
        rclpy.spin(agent)
    except KeyboardInterrupt:
        pass
    finally:
        agent.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Advanced Python Agent Example with Multiple Components

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class AdvancedPythonAgent(Node):
    def __init__(self):
        super().__init__('advanced_python_agent')

        # Publishers
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Subscribers
        self.laser_subscriber = self.create_subscription(
            LaserScan, 'scan', self.laser_callback, 10)
        self.command_subscriber = self.create_subscription(
            String, 'agent_commands', self.command_callback, 10)

        # Timer for periodic processing
        self.timer = self.create_timer(0.1, self.process_callback)

        # Agent state
        self.laser_data = None
        self.current_behavior = 'idle'
        self.cmd_vel_msg = Twist()

    def laser_callback(self, msg):
        self.laser_data = msg.ranges

    def command_callback(self, msg):
        if msg.data == 'start_navigation':
            self.current_behavior = 'navigation'
        elif msg.data == 'stop':
            self.current_behavior = 'idle'
            self.stop_robot()

    def process_callback(self):
        if self.current_behavior == 'navigation' and self.laser_data:
            self.navigation_behavior()

    def navigation_behavior(self):
        # Simple obstacle avoidance using laser data
        if self.laser_data:
            min_distance = min([d for d in self.laser_data if d > 0.1])  # Filter invalid readings

            if min_distance < 0.5:  # Obstacle detected within 0.5m
                # Stop and turn
                self.cmd_vel_msg.linear.x = 0.0
                self.cmd_vel_msg.angular.z = 0.5
            else:
                # Move forward
                self.cmd_vel_msg.linear.x = 0.2
                self.cmd_vel_msg.angular.z = 0.0

            self.cmd_vel_publisher.publish(self.cmd_vel_msg)

    def stop_robot(self):
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_publisher.publish(self.cmd_vel_msg)
```

## Bridging AI Logic to ROS Controllers

The integration of AI logic with ROS controllers enables intelligent robot behavior. Here's how to structure this integration:

### 1. Perception Pipeline
- Sensor data → AI processing → World understanding

### 2. Decision Making
- World understanding → AI algorithms → Action selection

### 3. Actuation
- Action selection → ROS controllers → Robot execution

### Example: AI-Based Object Recognition and Navigation

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist, Point
from std_msgs.msg import String
import cv2
from cv_bridge import CvBridge
import numpy as np

class AIBridgeNode(Node):
    def __init__(self):
        super().__init__('ai_bridge_node')

        # Initialize bridge for image conversion
        self.bridge = CvBridge()

        # Publishers
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_publisher = self.create_publisher(String, 'ai_status', 10)

        # Subscribers
        self.image_subscriber = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)
        self.scan_subscriber = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)

        # AI components
        self.object_detector = self.initialize_object_detector()
        self.path_planner = self.initialize_path_planner()

        # State variables
        self.detected_objects = []
        self.scan_data = None
        self.robot_pose = Point(0, 0, 0)

    def initialize_object_detector(self):
        # Initialize your AI object detection model
        # This could be a TensorFlow, PyTorch, or OpenCV model
        return None

    def initialize_path_planner(self):
        # Initialize your path planning algorithm
        return None

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.detected_objects = self.run_object_detection(cv_image)

            # Publish status
            status_msg = String()
            status_msg.data = f"Detected {len(self.detected_objects)} objects"
            self.status_publisher.publish(status_msg)

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

    def scan_callback(self, msg):
        self.scan_data = msg.ranges

    def run_object_detection(self, image):
        # Run your AI model to detect objects
        # This is where your AI logic connects to ROS
        detected_objects = []
        # ... AI processing code ...
        return detected_objects

    def make_navigation_decision(self):
        # Based on detected objects and scan data, decide on movement
        cmd_vel = Twist()

        # Example: Move toward detected objects while avoiding obstacles
        if self.detected_objects and self.scan_data:
            # Check for obstacles
            min_scan = min([d for d in self.scan_data if d > 0.1])

            if min_scan > 0.5:  # No immediate obstacles
                cmd_vel.linear.x = 0.2  # Move forward
                # Add logic to turn toward detected objects
            else:
                cmd_vel.linear.x = 0.0  # Stop
                cmd_vel.angular.z = 0.3  # Turn to avoid obstacle

        return cmd_vel

    def publish_navigation_command(self):
        cmd_vel = self.make_navigation_decision()
        self.cmd_vel_publisher.publish(cmd_vel)
```

## URDF Basics: Links, Joints, Robot Structure

URDF (Unified Robot Description Format) is an XML format for representing a robot model. It defines the physical and visual properties of a robot.

### Key URDF Concepts:

1. **Links**: Rigid parts of the robot (e.g., chassis, arms, wheels)
2. **Joints**: Connections between links that allow relative motion
3. **Materials**: Visual appearance of robot parts
4. **Gazebo Plugins**: Simulation-specific properties

### Basic URDF Structure:

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Wheel links -->
  <link name="wheel_front_left">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
  </link>

  <!-- Joints connecting links -->
  <joint name="wheel_front_left_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_front_left"/>
    <origin xyz="0.2 0.2 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>
</robot>
```

### URDF Joint Types:

1. **Fixed**: No movement between links
2. **Revolute**: Rotational movement with limits
3. **Continuous**: Rotational movement without limits
4. **Prismatic**: Linear sliding movement with limits
5. **Planar**: Movement on a plane
6. **Floating**: 6DOF movement

### Example: Humanoid Robot Structure

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="skin">
        <color rgba="1 0.8 0.6 1"/>
      </material>
    </visual>
  </link>

  <!-- Neck joint -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.3"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="100" velocity="1"/>
  </joint>

  <!-- Arms -->
  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
    </visual>
  </link>

  <joint name="left_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.2 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>
</robot>
```

## Working with URDF in Python

You can load and manipulate URDF files in Python using various libraries:

```python
# Using urdf_parser_py to read URDF files
from urdf_parser_py.urdf import URDF
import os

def load_robot_urdf(urdf_path):
    """Load a robot model from URDF file"""
    robot = URDF.from_xml_string(open(urdf_path).read())
    return robot

def analyze_robot_structure(robot):
    """Analyze the structure of a robot model"""
    print(f"Robot name: {robot.name}")
    print(f"Links: {len(robot.links)}")
    print(f"Joints: {len(robot.joints)}")

    for joint in robot.joints:
        print(f"Joint: {joint.name}, Type: {joint.type}, "
              f"Parent: {joint.parent}, Child: {joint.child}")

def get_link_info(robot, link_name):
    """Get information about a specific link"""
    link = robot.link_map.get(link_name)
    if link:
        print(f"Link: {link.name}")
        if link.visual:
            print(f"Visual geometry: {link.visual.geometry.type}")
        if link.collision:
            print(f"Collision geometry: {link.collision.geometry.type}")
        if link.inertial:
            print(f"Mass: {link.inertial.mass}")
    else:
        print(f"Link {link_name} not found")
```

## Practical Exercise: Creating a Simple Robot

Let's create a complete example that combines Python agents with URDF:

1. First, create the URDF file:

```xml
<!-- simple_mobile_robot.urdf -->
<?xml version="1.0"?>
<robot name="simple_mobile_robot">
  <material name="blue">
    <color rgba="0 0 1 1"/>
  </material>
  <material name="black">
    <color rgba="0 0 0 1"/>
  </material>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0" ixz="0" iyy="1.0" iyz="0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Wheels -->
  <link name="wheel_left">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
  </link>

  <link name="wheel_right">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
  </link>

  <!-- Wheel joints -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <origin xyz="0 0.25 0" rpy="-1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_right"/>
    <origin xyz="0 -0.25 0" rpy="-1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Camera -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </visual>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.25 0 0.1"/>
  </joint>
</robot>
```

2. Create a Python agent that controls this robot:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class MobileRobotController(Node):
    def __init__(self):
        super().__init__('mobile_robot_controller')

        # Publisher for velocity commands
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Subscriber for laser scan data
        self.scan_subscriber = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Robot state
        self.scan_data = None
        self.robot_state = "exploring"  # exploring, avoiding, stopped

    def scan_callback(self, msg):
        self.scan_data = msg.ranges

    def control_loop(self):
        if self.scan_data is None:
            return

        cmd_vel = Twist()

        # Simple obstacle avoidance
        front_distances = self.scan_data[330:30] + self.scan_data[330:]  # Front 60 degrees
        min_front_dist = min([d for d in front_distances if not math.isnan(d) and d > 0.1], default=float('inf'))

        if min_front_dist < 0.5:  # Obstacle detected
            # Stop and turn
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.5
            self.robot_state = "avoiding"
        else:
            # Move forward
            cmd_vel.linear.x = 0.2
            cmd_vel.angular.z = 0.0
            self.robot_state = "exploring"

        self.cmd_vel_publisher.publish(cmd_vel)
        self.get_logger().info(f"State: {self.robot_state}, Front dist: {min_front_dist:.2f}")

def main(args=None):
    rclpy.init(args=args)
    controller = MobileRobotController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

This chapter covered:
- Creating Python agents using rclpy
- Integrating AI logic with ROS controllers
- Understanding URDF basics for robot structure
- Working with links and joints in robot models
- Practical examples combining Python agents with URDF

The integration of Python-based AI agents with ROS controllers enables sophisticated robot behaviors, while URDF provides the foundation for representing robot structure in both simulation and real-world applications.

## Key Takeaways

1. Python agents can bridge AI logic to ROS controllers using rclpy
2. URDF defines the physical structure of robots using links and joints
3. The combination enables intelligent robot behaviors in Physical AI systems
4. Proper integration requires understanding both AI algorithms and ROS communication patterns