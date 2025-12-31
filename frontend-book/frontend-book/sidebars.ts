import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Manual sidebar for ROS 2 Educational Module
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1 - ROS 2 Fundamentals',
      items: [
        'module-1-ros2-fundamentals/index',
        'module-1-ros2-fundamentals/ros2-basics',
        'module-1-ros2-fundamentals/nodes-topics-services',
        'module-1-ros2-fundamentals/python-ros-integration',
      ],
    },
    {
      type: 'category',
      label: 'Module 2 - Digital Twin (Gazebo & Unity)',
      items: [
        'module-2-digital-twin/index',
        {
          type: 'category',
          label: 'Introduction',
          items: [
            'module-2-digital-twin/introduction/index',
            'module-2-digital-twin/introduction/what-are-digital-twins',
            'module-2-digital-twin/introduction/digital-twin-role',
            'module-2-digital-twin/introduction/gazebo-unity-comparison',
            'module-2-digital-twin/introduction/applications',
          ],
        },
        {
          type: 'category',
          label: 'Gazebo Fundamentals',
          items: [
            'module-2-digital-twin/gazebo-fundamentals/index',
            'module-2-digital-twin/gazebo-fundamentals/installation-setup',
            'module-2-digital-twin/gazebo-fundamentals/gravity-simulation',
            'module-2-digital-twin/gazebo-fundamentals/collision-detection',
            'module-2-digital-twin/gazebo-fundamentals/dynamics-simulation',
            'module-2-digital-twin/gazebo-fundamentals/humanoid-movement',
            'module-2-digital-twin/gazebo-fundamentals/joint-constraints',
            'module-2-digital-twin/gazebo-fundamentals/sensor-simulation-overview',
          ],
        },
        {
          type: 'category',
          label: 'Unity Integration',
          items: [
            'module-2-digital-twin/unity-integration/index',
            'module-2-digital-twin/unity-integration/visual-realism',
            'module-2-digital-twin/unity-integration/human-robot-interaction',
            'module-2-digital-twin/unity-integration/unity-gazebo-role',
            'module-2-digital-twin/unity-integration/unity-ros-bridge',
            'module-2-digital-twin/unity-integration/visualization-techniques',
          ],
        },
        {
          type: 'category',
          label: 'Environment Modeling',
          items: [
            'module-2-digital-twin/environment-modeling/index',
            'module-2-digital-twin/environment-modeling/indoor-environments',
            'module-2-digital-twin/environment-modeling/outdoor-environments',
            'module-2-digital-twin/environment-modeling/interactive-objects',
          ],
        },
        {
          type: 'category',
          label: 'Sensor Simulation',
          items: [
            'module-2-digital-twin/sensor-simulation/index',
            'module-2-digital-twin/sensor-simulation/camera-sensors',
            'module-2-digital-twin/sensor-simulation/lidar-sensors',
            'module-2-digital-twin/sensor-simulation/imu-sensors',
            'module-2-digital-twin/sensor-simulation/force-torque-sensors',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Module 3 - The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'module-3-nvidia-isaac/index',
        {
          type: 'category',
          label: 'NVIDIA Isaac Fundamentals',
          items: [
            'module-3-nvidia-isaac/isaac-fundamentals/index',
            'module-3-nvidia-isaac/isaac-fundamentals/what-is-isaac',
            'module-3-nvidia-isaac/isaac-fundamentals/role-in-robotics',
            'module-3-nvidia-isaac/isaac-fundamentals/isaac-sim-vs-ros',
            'module-3-nvidia-isaac/isaac-fundamentals/getting-started',
          ],
        },
        {
          type: 'category',
          label: 'Perception & Localization with Isaac ROS',
          items: [
            'module-3-nvidia-isaac/perception-localization/index',
            'module-3-nvidia-isaac/perception-localization/vslam-concepts',
            'module-3-nvidia-isaac/perception-localization/hardware-acceleration',
            'module-3-nvidia-isaac/perception-localization/sensor-data-flow',
            'module-3-nvidia-isaac/perception-localization/perception-pipelines',
          ],
        },
        {
          type: 'category',
          label: 'Navigation & Training for Humanoids',
          items: [
            'module-3-nvidia-isaac/navigation-training/index',
            'module-3-nvidia-isaac/navigation-training/nav2-overview',
            'module-3-nvidia-isaac/navigation-training/humanoid-navigation',
            'module-3-nvidia-isaac/navigation-training/simulation-to-real',
            'module-3-nvidia-isaac/navigation-training/training-methodologies',
            'module-3-nvidia-isaac/navigation-training/performance-optimization',
          ],
        },
      ],
    },
  ],
};

export default sidebars;
