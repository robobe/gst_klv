#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, qos_profile_system_default
from cv_bridge import CvBridge
from sensor_msgs.msg import CameraInfo, Image
import cv2

CAMERA_TOPIC = "/camera"

class MyNode(Node):
    def __init__(self):
        node_name="player"
        super().__init__(node_name)
        self.cv_br = CvBridge()
        self.img_sub = self.create_subscription(
            Image,
            CAMERA_TOPIC,
            self.image_handler,
            qos_profile=qos_profile_sensor_data,
        )

        self.get_logger().info("Hello ROS2")

    def image_handler(self, msg: Image):
        """_summary_
        https://docs.ros2.org/latest/api/sensor_msgs/msg/Image.html

        """
        frame = self.cv_br.imgmsg_to_cv2(msg)
        cv2.imshow("debug", frame)
        cv2.waitKey(10)

        

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()