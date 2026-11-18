import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.clock import Clock
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion
import math


class Odom(Node):
    def __init__(self):
        super().__init__('odom_node')
        
        # 1. Definimos el perfil de QoS compatible con el LiDAR del TB3
        qos_profile_b = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=10)
        qos_profile_r = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, depth=10)
        # Publicador para mover el robot
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', qos_profile_r)
        # Subscriptor a la Odometria
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, qos_profile_b)
        
        self.linear_speed = 0.4 # m/s
        self.angular_speed = 0.8 # m/s

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_rot = 0.0

        self.start_x = 0.0
        self.start_y = 0.0
        self.start_rot = 0.0

        self.iteration = 1
        self.state = "forward"
        self.timer = self.create_timer(0.1, self.control_loop)

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        quaternion = [q.x, q.y, q.z, q.w]
        (_,_,rot) = euler_from_quaternion(quaternion)

        self.current_rot = rot
        
    def publish_velocity(self, linear=0.0, angular=0.0):
        msg = TwistStamped()
        msg.header.stamp = Clock().now().to_msg()
        msg.twist.linear.x = linear
        msg.twist.angular.z = angular
        self.publisher.publish(msg)

    def control_loop(self):
        if (self.iteration > 4):
            self.publish_velocity()
            return

        if self.state == "forward":
            self.move_forward(1.0)
        elif self.state == "turn":
            self.turn_90()

    def move_forward(self, distance):
        dx = self.current_x - self.start_x
        dy = self.current_y - self.start_y

        traveled = math.sqrt(dx*dx + dy*dy)
        print(f"traveled = {traveled}")
        print(f"distance = {distance}")
        if traveled < distance:
            self.publish_velocity(linear=self.linear_speed)
        else:
            self.publish_velocity()

            self.start_rot = self.current_rot
            self.state = "turn"

    def turn_90(self):
        target = self.start_rot + math.pi/2
        # error = target - self.current_rot
        error = target - self.current_rot
        error = math.atan2(math.sin(error), math.cos(error))

        print(f"self.current_rot = {self.current_rot}")
        print(f"target = {target}")
        # if self.current_rot < target:
        if abs(error) > 0.05:
            self.publish_velocity(angular=self.angular_speed)
        else:
            self.publish_velocity()

            self.start_x = self.current_x
            self.start_y = self.current_y
            self.state = "forward"

            self.iteration += 1

def main(args=None):
    rclpy.init(args=args)
    node = Odom()
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
