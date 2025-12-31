#!/usr/bin/env python3
"""
Basic Subscriber Example

This example demonstrates how to create a simple ROS 2 subscriber node
that listens to messages on a topic.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BasicSubscriber(Node):
    """
    A simple subscriber node that listens to messages on a topic
    """

    def __init__(self):
        super().__init__('basic_subscriber')

        # Create a subscription to the 'chatter' topic
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)

        # Prevent unused variable warning
        self.subscription  # type: ignore[attr-defined]

        self.get_logger().info('Basic Subscriber node initialized')

    def listener_callback(self, msg):
        """Callback function that processes incoming messages"""
        # Log the received message
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    """Main function to initialize and run the node"""
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the subscriber node
    basic_subscriber = BasicSubscriber()

    try:
        # Keep the node running to listen for messages
        rclpy.spin(basic_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        basic_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()