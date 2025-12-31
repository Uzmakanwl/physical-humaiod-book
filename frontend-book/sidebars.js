// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
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
  ],
};

module.exports = sidebars;