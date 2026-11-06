import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Empty

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        self.sub_joy = self.create_subscription(Joy, 'joy', self.joy_cb, 10)
        self.pub_vel = self.create_publisher(Twist, 'controller/cmd_vel', 10)
        self.pub_enable = self.create_publisher(Bool, 'controller/enable', 10)
        self.pub_hb = self.create_publisher(Empty, 'heartbeat/laptop1', 10)
        
        # FIX: Publish heartbeat at 10 Hz (every 0.1 seconds) so it beats the 0.5s watchdog
        self.timer_hb = self.create_timer(0.1, self.publish_heartbeat)
        self.timer_timeout = self.create_timer(0.1, self.check_timeout)
        self.last_joy_time = self.get_clock().now()
        self.deadzone = 0.05

    def joy_cb(self, msg):
        self.last_joy_time = self.get_clock().now()
        
        rb_pressed = bool(msg.buttons[7]) 
        self.pub_enable.publish(Bool(data=rb_pressed))
        
        twist = Twist()
        if rb_pressed:
            # FIX: Removed the negative sign on msg.axes[1]
            x_val = msg.axes[1] if abs(msg.axes[1]) > self.deadzone else 0.0
            z_val = msg.axes[0] if abs(msg.axes[0]) > self.deadzone else 0.0
            
            twist.linear.x = x_val * 2.0
            twist.angular.z = z_val * 2.0
            
        self.pub_vel.publish(twist)

    def check_timeout(self):
        elapsed = (self.get_clock().now() - self.last_joy_time).nanoseconds / 1e9
        if elapsed > 0.5:
            self.pub_enable.publish(Bool(data=False))
            self.pub_vel.publish(Twist())

    def publish_heartbeat(self):
        self.pub_hb.publish(Empty())

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
