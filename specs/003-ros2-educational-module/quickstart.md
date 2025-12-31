# Quickstart Guide: ROS 2 Educational Module

## Prerequisites

Before starting this module, ensure you have:

- Basic Python programming knowledge
- Understanding of fundamental programming concepts (variables, functions, classes)
- Access to a computer with internet connection
- Administrative rights to install software (if installing locally)

## Environment Setup

### Option 1: Using ROS 2 Development Container (Recommended for beginners)

1. Install Docker Desktop for your platform
2. Clone the course repository:
   ```bash
   git clone https://github.com/[your-repo]/ros2-educational-module.git
   cd ros2-educational-module
   ```
3. Start the development container:
   ```bash
   docker compose up -d
   ```
4. Connect to the container:
   ```bash
   docker exec -it ros2-dev-container bash
   ```

### Option 2: Local ROS 2 Installation

1. Install ROS 2 Humble Hawksbill following the official installation guide
2. Verify installation:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 --version
   ```

## Docusaurus Documentation Setup

1. Install Node.js 18+ and npm
2. Clone the documentation repository:
   ```bash
   git clone https://github.com/[your-repo]/ros2-docs.git
   cd ros2-docs
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm start
   ```

## Running Examples

### Basic Publisher/Subscriber Example

1. Navigate to the examples directory:
   ```bash
   cd tutorial-examples/python-agents
   ```
2. Source ROS 2 environment:
   ```bash
   source /opt/ros/humble/setup.bash
   ```
3. Run the publisher:
   ```bash
   python3 basic_publisher.py
   ```
4. In a new terminal, run the subscriber:
   ```bash
   python3 basic_subscriber.py
   ```

### URDF Robot Model Example

1. Navigate to URDF examples:
   ```bash
   cd tutorial-examples/urdf-examples
   ```
2. View the robot model in RViz:
   ```bash
   ros2 run rviz2 rviz2 -d simple_robot.urdf
   ```

## Module Navigation

The module is organized into three main chapters:

1. **ROS 2 Basics** - Core concepts and architecture
2. **Communication Model** - Nodes, topics, services, and actions
3. **Python Integration** - Creating ROS 2 agents with Python

Each chapter includes:
- Theoretical concepts
- Practical code examples
- Hands-on exercises
- Knowledge checks

## Getting Help

- Check the FAQ section in the documentation
- Use the embedded chatbot for specific questions
- Review the troubleshooting guide for common issues
- Join the student community forum