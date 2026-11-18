import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.clock import Clock
from geometry_msgs.msg import TwistStamped
import math

class Square(Node):
    def __init__(self):
        super().__init__('square_node')
        
        # 1. Definimos el perfil de QoS compatible con el LiDAR del TB3
        qos_profile_r = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, depth=10)
        # Publicador para mover el robot
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', qos_profile_r)
        
        self.linear_speed = 0.4 # m/s
        self.angular_speed = 0.8 # m/s
        self.move_square()

    def publish_velocity(self, linear=0.0, angular=0.0):
        msg = TwistStamped()
        msg.header.stamp = Clock().now().to_msg()
        msg.twist.linear.x = linear
        msg.twist.angular.z = angular
        self.publisher.publish(msg)

    def move_forward(self, distance):
        duration = distance / self.linear_speed
        start_time = self.get_clock().now()

        while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
            self.publish_velocity(linear=self.linear_speed)
            rclpy.spin_once(self, timeout_sec=0.01)

        self.publish_velocity()

    def turn_90(self):
        angle = math.pi / 2
        duration = angle /self.angular_speed
        start_time = self.get_clock().now()

        while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
            self.publish_velocity(angular=self.angular_speed)
            rclpy.spin_once(self, timeout_sec=0.01)

        self.publish_velocity()

    def move_square(self):
        for _ in range(4):
            self.move_forward(1.0)
            self.turn_90()

def main(args=None):
    print('Hi from package_square.')
    rclpy.init(args=args)
    node = Square()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Siempre es bueno mandar un último mensaje de parada
        node.publisher.publish(TwistStamped())
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()