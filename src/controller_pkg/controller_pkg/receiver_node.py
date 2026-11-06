import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty

class ReceiverNode(Node):
    def __init__(self):
        super().__init__('receiver_node')
        self.sub_vel = self.create_subscription(Twist, 'controller/cmd_vel', self.vel_cb, 10)
        self.sub_hb = self.create_subscription(Empty, 'heartbeat/laptop1', self.hb_cb, 10)
        self.pub_turtle = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.last_hb_time = self.get_clock().now()
        self.latest_vel = Twist()
        self.connection_lost = False
        self.timer_watchdog = self.create_timer(0.1, self.check_watchdog)

    def vel_cb(self, msg):
        self.latest_vel = msg

    def hb_cb(self, msg):
        self.last_hb_time = self.get_clock().now()
        if self.connection_lost:
            self.get_logger().info("CONNECTION RESTORED: Heartbeat detected.")
            self.connection_lost = False

    def check_watchdog(self):
        elapsed = (self.get_clock().now() - self.last_hb_time).nanoseconds / 1e9
        if elapsed > 0.5:
            if not self.connection_lost:
                self.get_logger().error("CONNECTION LOST: No heartbeat for 500ms. Stopping turtle.")
                self.connection_lost = True
            self.pub_turtle.publish(Twist())
        else:
            self.pub_turtle.publish(self.latest_vel)

def main():
    rclpy.init()
    rclpy.spin(ReceiverNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
