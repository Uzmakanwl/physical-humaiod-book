---
sidebar_position: 6
title: 'Troubleshooting Common Issues'
---

# Troubleshooting Common Issues

This section covers common problems students may encounter when learning ROS 2 and provides solutions to help you continue your learning journey.

## Environment and Setup Issues

### ROS 2 Not Found
**Problem**: When running `ros2` commands, you get "command not found" or "ros2 is not recognized".

**Solutions**:
1. Make sure ROS 2 is installed properly. Follow the official installation guide for your OS.
2. Source the ROS 2 setup file in your terminal:
   ```bash
   source /opt/ros/humble/setup.bash  # For Linux
   # Or add it to your .bashrc/.zshrc:
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   ```
3. For Windows users, use the ROS 2 Developer Command Prompt or source the setup file manually.

### Python Package Import Errors
**Problem**: Getting import errors when trying to use `rclpy` or other ROS 2 packages.

**Solutions**:
1. Make sure you're using the correct Python environment where ROS 2 packages are installed.
2. Check that your Python version is compatible with your ROS 2 distribution.
3. Verify that the ROS 2 environment is sourced before running Python scripts.

## Node Communication Issues

### Nodes Cannot Communicate
**Problem**: Nodes are running but not communicating with each other.

**Solutions**:
1. Check that both nodes are on the same ROS domain ID:
   ```bash
   echo $ROS_DOMAIN_ID  # Should be the same for both terminals
   ```
2. Verify that the topic/service names match exactly between publisher/subscriber or client/service.
3. Check that the message types match between publisher and subscriber.
4. Ensure Quality of Service (QoS) settings are compatible.

### Topic Not Found
**Problem**: Publisher is running but subscriber doesn't receive messages.

**Solutions**:
1. Use `ros2 topic list` to verify the topic exists.
2. Use `ros2 topic echo <topic_name>` to check if messages are being published.
3. Check that the topic names match exactly (including case sensitivity).
4. Verify that both nodes are using compatible QoS profiles.

## Code-Specific Issues

### Node Not Spinning
**Problem**: Node runs but doesn't process callbacks.

**Solution**:
Make sure to call `rclpy.spin(node)` in your main function:
```python
def main(args=None):
    rclpy.init(args=args)
    my_node = MyNode()
    rclpy.spin(my_node)  # This is essential!
    my_node.destroy_node()
    rclpy.shutdown()
```

### Timer Not Working
**Problem**: Timer callbacks are not being executed.

**Solution**:
Ensure your timer is properly created and that the node continues to spin:
```python
def __init__(self):
    super().__init__('my_node')
    # Create timer
    self.timer = self.create_timer(0.1, self.timer_callback)

def timer_callback(self):
    self.get_logger().info('Timer called!')
```

### Parameter Issues
**Problem**: Parameters are not being set or retrieved correctly.

**Solution**:
```python
# Declaring a parameter
self.declare_parameter('my_param', 'default_value')

# Getting a parameter
my_param = self.get_parameter('my_param').value

# Setting a parameter
self.set_parameters([Parameter('my_param', Parameter.Type.STRING, 'new_value')])
```

## URDF Issues

### URDF Not Loading
**Problem**: Robot model not displaying correctly in RViz.

**Solutions**:
1. Check for XML syntax errors in your URDF file.
2. Verify all links have unique names.
3. Ensure all joints have proper parent-child relationships.
4. Make sure visual and collision geometries are properly defined.

### Joint Limits Not Working
**Problem**: Joints are moving beyond their specified limits.

**Solution**:
Make sure to specify limits in revolute joints:
```xml
<joint name="joint_name" type="revolute">
  <parent link="parent_link"/>
  <child link="child_link"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

## Development Environment Issues

### IDE Not Recognizing ROS 2 Types
**Problem**: Your IDE shows errors for ROS 2 imports and types.

**Solutions**:
1. Configure your IDE to use the ROS 2 Python environment.
2. Install the ROS extension for VS Code if using VS Code.
3. Add ROS 2 Python packages to your IDE's Python path.

### Build Issues
**Problem**: `colcon build` fails with errors.

**Solutions**:
1. Check that all dependencies are properly listed in `package.xml`.
2. Verify that CMakeLists.txt is properly configured.
3. Ensure all source files are in the correct directories.
4. Clean build directory if needed: `rm -rf build/ install/ log/`

## Network and Multi-Machine Issues

### Nodes on Different Machines Cannot Communicate
**Problem**: ROS 2 nodes on different machines cannot see each other.

**Solutions**:
1. Ensure both machines are on the same network.
2. Set the same `ROS_DOMAIN_ID` on both machines.
3. Check firewall settings to allow DDS traffic (usually UDP ports).
4. Verify that `ROS_LOCALHOST_ONLY` is not set to 1 if using multiple machines.

## Performance Issues

### High CPU Usage
**Problem**: ROS 2 nodes using excessive CPU.

**Solutions**:
1. Reduce the frequency of timers and publishers.
2. Use appropriate QoS settings (e.g., reduce history depth).
3. Check for infinite loops in callbacks.
4. Use `rclpy` timers instead of Python `time.sleep()` in callbacks.

### Memory Leaks
**Problem**: Memory usage increases over time.

**Solutions**:
1. Properly destroy nodes and clean up resources in shutdown.
2. Be careful with message storage and processing.
3. Monitor memory usage with tools like `htop` or `ros2 topic hz`.

## Debugging Tips

### Using ROS 2 Command Line Tools
```bash
# List all nodes
ros2 node list

# List all topics
ros2 topic list

# Echo a topic to see messages
ros2 topic echo /topic_name std_msgs/msg/String

# Check node information
ros2 node info /node_name

# Get service information
ros2 service list
```

### Adding Debug Output
```python
# Use logging instead of print statements
self.get_logger().info('Debug message')
self.get_logger().warn('Warning message')
self.get_logger().error('Error message')
```

### Using RViz for Visualization
- Check TF frames to ensure transforms are being published
- Visualize sensor data like laser scans and images
- Monitor robot state with RobotModel display

## Getting Help

### Useful Resources
1. **ROS Answers**: https://answers.ros.org/questions/
2. **Official Documentation**: https://docs.ros.org/
3. **ROS Discourse**: https://discourse.ros.org/
4. **GitHub Issues**: Check the specific package's repository

### Creating Good Bug Reports
When asking for help, include:
1. ROS 2 distribution and OS version
2. Complete error messages
3. Minimal reproducible example
4. What you've tried so far

### Common Debugging Steps
1. Check if the node is actually running: `ros2 run pkg_name node_name`
2. Verify topic/service connections: `ros2 node info /node_name`
3. Test with simple examples first
4. Use `ros2 doctor` to check system health
5. Restart `ros2 daemon` if needed: `ros2 daemon stop && ros2 daemon start`

## Quick Fixes Checklist

- [ ] Source ROS 2 environment: `source /opt/ros/<distro>/setup.bash`
- [ ] Check ROS_DOMAIN_ID: `echo $ROS_DOMAIN_ID`
- [ ] Verify Python environment and packages
- [ ] Confirm topic/service names match exactly
- [ ] Check QoS profile compatibility
- [ ] Ensure nodes are spinning with `rclpy.spin()`
- [ ] Verify network connectivity for multi-machine setups
- [ ] Restart the ROS 2 daemon if needed