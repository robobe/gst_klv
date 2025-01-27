import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import gi
import numpy as np

HEIGHT = 480
WIDTH = 640
CAMERA_TOPIC = "/camera"

class ImagePublisherNode(Node):
    def __init__(self):
        super().__init__('gstreamer_publisher')
        self.counter = 0
        # ROS 2 Publisher
        self.publisher_ = self.create_publisher(Image, CAMERA_TOPIC, 10)
        self.bridge = CvBridge()

        # Timer
        self.timer = self.create_timer(1/10, self.timer_callback)

    def timer_callback(self):
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        cv2.putText(frame, f"Appsrc Video {self.counter}", (50, HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        # Convert the frame to a GStreamer buffer
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher_.publish(msg)
        self.counter += 1
        self.get_logger().info(f"Published frame {self.counter}")

        

def main(args=None):
    rclpy.init(args=args)

    # Create the node
    image_publisher_node = ImagePublisherNode()

    # Use a SingleThreadedExecutor
    executor = SingleThreadedExecutor()
    executor.add_node(image_publisher_node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        image_publisher_node.get_logger().info('Shutting down...')
    finally:
        executor.shutdown()
        image_publisher_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    import numpy as np
    main()