---
sidebar_position: 7
title: 'Glossary of ROS 2 Terms and Concepts'
---

# Glossary of ROS 2 Terms and Concepts

This glossary provides definitions for key terms and concepts used throughout the ROS 2 educational module.

## A

**Action**: A communication pattern in ROS 2 for long-running tasks that provides feedback and the ability to cancel. Actions combine features of services and topics.

**Action Client**: A node that sends goals to an action server and receives feedback and results.

**Action Server**: A node that accepts goals from action clients, processes them, and sends back feedback and results.

## B

**Bag File**: A file format used in ROS to store recorded data from topics. In ROS 2, this functionality is provided by the `ros2 bag` command.

**Bridge**: Software that connects ROS/ROS 2 with other communication frameworks or networks.

## C

**Client Library**: Software libraries that allow nodes to be written in different programming languages (e.g., rclpy for Python, rclcpp for C++).

**Composition**: The practice of combining multiple nodes into a single process to reduce communication overhead.

**Context**: An object in ROS 2 that encapsulates the state of a single ROS client library instance, allowing multiple isolated ROS graphs within one process.

## D

**DDS (Data Distribution Service)**: The middleware layer that ROS 2 uses for communication between nodes. It provides Quality of Service (QoS) policies and discovery mechanisms.

**Deadline**: A QoS policy in ROS 2 that ensures messages are delivered within a specified time period.

**Dependency Injection**: A design pattern used in ROS 2 for managing dependencies between components.

## E

**Executor**: An object that controls how callbacks are invoked in ROS 2. It manages the spinning of nodes and callback execution.

## F

**Future**: An object used in ROS 2 for asynchronous programming, representing a value that will be available at some point in the future.

## G

**Graph**: The network of nodes, topics, services, and actions in a ROS system. The ROS graph can be visualized using tools like `rqt_graph`.

## H

**History Policy**: A QoS policy that determines how many messages are stored for late-joining subscribers.

## L

**Lifecycle Node**: A special type of node in ROS 2 that has a well-defined state machine for managing its lifecycle (unconfigured, inactive, active, finalized).

**Liveliness**: A QoS policy in ROS 2 that ensures participants remain active and responsive.

## M

**Message**: The data structure used for communication in ROS 2. Messages are defined in `.msg` files and are used with topics.

**Middleware**: Software that provides common services and capabilities to applications beyond what's offered by the operating system. In ROS 2, DDS serves as the middleware.

## N

**Node**: A process that performs computation in ROS. Nodes are the fundamental building blocks of a ROS system and communicate with each other using messages.

**Node Name**: A unique identifier for a node within a ROS graph.

## P

**Package**: The basic building unit of software in ROS. A package contains libraries, executables, scripts, or other artifacts.

**Parameter**: A way to configure nodes at runtime in ROS 2. Parameters can be set at launch time or changed while the node is running.

**Publisher**: A component of a node that sends messages to a topic.

## Q

**QoS (Quality of Service)**: A set of policies that define how messages are delivered in terms of reliability, durability, liveliness, and history.

**Quality of Service (QoS)**: See QoS.

## R

**Reliability Policy**: A QoS policy that determines whether messages are delivered reliably or best-effort.

**Resource Manager**: Component that manages resources in a ROS 2 system.

**rclpy**: The Python client library for ROS 2. It provides the standard interface for Python programs to interface with ROS 2.

**rclcpp**: The C++ client library for ROS 2.

**ROS Domain ID**: An identifier that separates different ROS 2 networks. Nodes must be on the same domain to communicate.

## S

**Service**: A synchronous communication pattern in ROS 2 where a client sends a request to a server and waits for a response.

**Service Client**: A node that sends requests to a service server.

**Service Server**: A node that receives requests from service clients and sends back responses.

**Subscriber**: A component of a node that receives messages from a topic.

## T

**Topic**: A named bus over which nodes exchange messages. Topics enable asynchronous communication in a publish/subscribe pattern.

**TF (Transform)**: The system for tracking coordinate frame transformations over time in ROS.

**TF2**: The second generation transform library in ROS, providing improved performance and features over the original TF.

## U

**URDF (Unified Robot Description Format)**: An XML format for representing a robot model including links, joints, and other properties.

## W

**Workspace**: A directory containing ROS packages and build artifacts. A typical workspace has `src`, `build`, `install`, and `log` subdirectories.

## Y

**YAML (YAML Ain't Markup Language)**: A human-readable data serialization format used in ROS 2 for configuration files.

## Z

**Zero-Copy**: A feature in DDS that allows data to be shared between processes without copying, improving performance.

---

## Acronyms and Abbreviations

- **DDS**: Data Distribution Service
- **QoS**: Quality of Service
- **RCL**: ROS Client Library
- **RCLPY**: ROS Client Library for Python
- **RCLCPP**: ROS Client Library for C++
- **TF**: Transform
- **URDF**: Unified Robot Description Format
- **XML**: eXtensible Markup Language
- **YAML**: YAML Ain't Markup Language
- **API**: Application Programming Interface
- **CLI**: Command Line Interface
- **GUI**: Graphical User Interface
- **IDE**: Integrated Development Environment
- **OS**: Operating System
- **TCP**: Transmission Control Protocol
- **UDP**: User Datagram Protocol

## Concepts

**Middleware Agnostic Client Library (MCL)**: The architecture pattern that allows ROS 2 to work with different middleware implementations.

**ROS 2 Client Library (RCL)**: The layer that provides the ROS 2 API and abstracts the underlying middleware.

**RMW (ROS Middleware)**: The interface that allows ROS 2 to work with different DDS implementations.

**ROS Graph**: The representation of all nodes, topics, services, and actions in a running ROS system.

**ROS Namespace**: A way to organize nodes and topics hierarchically, similar to directories in a filesystem.

**ROS Time**: The time system used in ROS 2, which can use system time, simulation time, or other time sources.

This glossary will continue to expand as you progress through more advanced ROS 2 topics.