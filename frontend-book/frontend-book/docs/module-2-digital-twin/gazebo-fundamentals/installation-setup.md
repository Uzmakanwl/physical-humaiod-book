# Gazebo Installation and Setup Guide

Setting up Gazebo for robotics simulation requires careful attention to system requirements and dependencies. This guide will walk you through the installation process and initial configuration for humanoid robot simulation.

## System Requirements

Before installing Gazebo, ensure your system meets the following requirements:

### Minimum Requirements
- **Operating System**: Ubuntu 18.04+ (recommended), macOS 10.14+, Windows 10+ (via WSL2 or Docker)
- **CPU**: Multi-core processor (Intel i5 or equivalent recommended)
- **RAM**: 8GB minimum, 16GB recommended for complex simulations
- **GPU**: OpenGL 2.1+ compatible graphics card with dedicated VRAM
- **Storage**: 2GB available space for basic installation, more for models and plugins

### Recommended Specifications for Humanoid Robot Simulation
- **CPU**: Multi-core processor (Intel i7 or equivalent)
- **RAM**: 16GB or more
- **GPU**: Dedicated graphics card with 4GB+ VRAM
- **Storage**: 10GB+ available space for models and environments

## Installation Methods

### Ubuntu/Linux Installation

#### Method 1: Package Manager (Recommended)
```bash
sudo apt update
sudo apt install gazebo11 libgazebo11-dev
```

For the latest version:
```bash
sudo apt install gazebo libgazebo-dev
```

#### Method 2: Using ROS Repository (Recommended for ROS users)
If you're using ROS, install Gazebo through the ROS repository for better integration:

```bash
# For ROS Noetic
sudo apt install ros-noetic-gazebo-ros-pkgs ros-noetic-gazebo-ros-control

# For ROS 2 Foxy
sudo apt install ros-foxy-gazebo-ros-pkgs ros-foxy-gazebo-ros-control

# For ROS 2 Humble
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros-control
```

### macOS Installation

#### Using Homebrew
```bash
brew install osrf/simulation/gazebo11
```

For the latest version:
```bash
brew install osrf/simulation/gazebo
```

### Windows Installation

#### Option 1: Windows Subsystem for Linux (WSL2) - Recommended
1. Install WSL2 with Ubuntu
2. Follow the Ubuntu installation instructions within WSL2
3. Configure X11 forwarding for GUI applications

#### Option 2: Docker
Use Docker to run Gazebo in a containerized environment:
```bash
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix osrf/gazebo:gz-xenial
```

## Post-Installation Setup

### Environment Variables
Add Gazebo paths to your environment:

For Ubuntu/Linux:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/.gazebo/models
export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:~/.gazebo
export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:~/.gazebo/plugins
```

### Initial Configuration
1. Create the Gazebo configuration directory:
```bash
mkdir -p ~/.gazebo
```

2. Set up the models directory:
```bash
mkdir -p ~/.gazebo/models
```

## Testing the Installation

### Launch Gazebo GUI
```bash
gazebo
```

If successful, the Gazebo GUI should launch with a default empty world.

### Basic Commands
```bash
# Launch with default world
gazebo

# Launch with specific world file
gazebo /path/to/world_file.world

# Launch in headless mode (no GUI)
gzserver /path/to/world_file.world

# Launch GUI client only (connects to running server)
gzclient
```

## ROS Integration Setup

### For ROS 1
1. Install ROS-Gazebo plugins:
```bash
sudo apt install ros-<distro>-gazebo-ros-pkgs ros-<distro>-gazebo-ros-control
```

2. Source ROS environment:
```bash
source /opt/ros/<distro>/setup.bash
```

### For ROS 2
1. Install ROS 2-Gazebo plugins:
```bash
sudo apt install ros-<distro>-gazebo-ros-pkgs ros-<distro>-gazebo-ros-control
```

2. Source ROS 2 environment:
```bash
source /opt/ros/<distro>/setup.bash
```

## Common Setup Issues and Solutions

### Graphics Issues
- **Problem**: Gazebo crashes or displays rendering errors
- **Solution**: Update graphics drivers and ensure OpenGL support
- **Alternative**: Run with software rendering:
```bash
export LIBGL_ALWAYS_SOFTWARE=1
gazebo
```

### Performance Issues
- **Problem**: Slow simulation or low frame rates
- **Solution**:
  - Reduce visual quality in Gazebo preferences
  - Close other applications to free up resources
  - Ensure GPU acceleration is enabled

### Plugin Loading Errors
- **Problem**: Plugins fail to load with "Library not found" errors
- **Solution**: Check plugin paths and ensure proper installation of dependencies

## Humanoid Robot Specific Setup

### Installing Humanoid Models
For humanoid robot simulation, you may want to install additional models:

```bash
# Download common humanoid robot models
git clone https://github.com/roboticsgroup/gazebo_models.git ~/.gazebo/models
git clone https://github.com/ros-simulation/gazebo_ros_demos.git
```

### Physics Engine Configuration
For humanoid robots, consider these physics settings:
- **ODE (Open Dynamics Engine)**: Default, good balance of speed and accuracy
- **Bullet**: Better for complex collision scenarios
- **Simbody**: More accurate but slower

## Verification Steps

1. Launch Gazebo:
```bash
gazebo
```

2. Verify you can:
   - Open the GUI without errors
   - Spawn basic objects (cubes, spheres)
   - Move objects with the GUI tools
   - Adjust physics parameters

3. Test with a simple world file:
```bash
gazebo worlds/empty.world
```

## Troubleshooting Tips

### If Gazebo won't start:
1. Check if another instance is running: `ps aux | grep gazebo`
2. Clear Gazebo cache: `rm -rf ~/.gazebo`
3. Update graphics drivers

### If simulation is slow:
1. Reduce the number of objects in the scene
2. Lower visual quality settings
3. Check system resources (CPU, RAM, GPU)

### If plugins don't load:
1. Verify installation with: `ldd /usr/lib/x86_64-linux-gnu/libgazebo.so`
2. Check plugin paths in your model files
3. Ensure ROS environment is properly sourced (if using ROS)

## Next Steps

Once Gazebo is successfully installed and configured, you're ready to explore the physics simulation capabilities that make it ideal for humanoid robot development. The next section will cover the fundamental physics concepts that govern how objects behave in Gazebo simulations.