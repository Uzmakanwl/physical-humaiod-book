#!/usr/bin/env python3
"""
Basic Publisher Example

This example demonstrates how to create a simple ROS 2 publisher node
that publishes messages to a topic.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BasicPublisher(Node):
    """
    A simple publisher node that publishes messages to a topic
    """

    def __init__(self):
        super().__init__('basic_publisher')

        # Create a publisher
        self.publisher = self.create_publisher(String, 'chatter', 10)

        # Create a timer to publish messages periodically
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter to track message number
        self.i = 0

        self.get_logger().info('Basic Publisher node initialized')

    def timer_callback(self):
        """Callback function that publishes messages"""
        msg = String()
        msg.data = f'Hello World: {self.i}'

        # Publish the message
        self.publisher.publish(msg)

        # Log the message
        self.get_logger().info(f'Publishing: "{msg.data}"')

        # Increment the counter
        self.i += 1


def main(args=None):
    """Main function to initialize and run the node"""
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the publisher node
    basic_publisher = BasicPublisher()

    try:
        # Keep the node running
        rclpy.spin(basic_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        basic_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()