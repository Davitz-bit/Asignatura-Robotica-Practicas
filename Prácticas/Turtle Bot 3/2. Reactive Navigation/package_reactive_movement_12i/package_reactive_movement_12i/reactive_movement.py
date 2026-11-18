import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.clock import Clock

# Set velocity
from geometry_msgs.msg import TwistStamped

# Get LIDAR data
from sensor_msgs.msg import LaserScan

# Get odometry data
from nav_msgs.msg import Odometry

# Transform orientation data type from Odometry
from tf_transformations import euler_from_quaternion

# Auxiliary
import math
from dataclasses import dataclass
import time

@dataclass
class Velocity:
    linear: float
    angular: float

@dataclass
class Position:
    x: float
    y: float
    rotZ: float

@dataclass
class LidarScan:
    angle: float
    distance: float
    intensity: float

class ReactiveNavigation(Node):
    def __init__(self):
        super().__init__("reactive_navigation_node")
        
        # Definition of QoS profile compatible with LiDAR from TB3
        qos_profile_b = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=10) 	# Get message (sensor data)
        qos_profile_r = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, depth=10)		# Send message (actuators)

        # Velocity and rotation publisher
        self.vel_publisher = self.create_publisher(TwistStamped, '/cmd_vel', qos_profile_r)
        # LIDAR subscription
        self.lidar_subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile_b)

        # Initialize velocity object
        self.velocity = Velocity(0.25, 0.2)
        # Initialize odometry object
         self.max_distance = 2 # m
       self.position = Position(0.0, 0.0, 0.0)

        self.safe_distance = 0.5 # 20 cm
        self.angle_factor = 3
        self.target = None

    def scan_callback(self, msg):
        data = zip(range(len(msg.ranges)), msg.ranges, msg.intensities)
        data = [LidarScan(a,r,i) for a,r,i in data]
        valid_ranges = [ls for ls in data if ls.distance > msg.range_min and ls.distance < self.max_distance]
        max_intensity = -float('inf')
        self.target = None
        for ls in valid_ranges:
            if ls.intensity > max_intensity:
                self.target = ls
                max_intensity = ls.intensity

        if self.target != None:
            self.velocity.linear = self.target.distance - self.safe_distance

            radians = math.radians(self.target.angle)
            if radians > math.pi: # Normalization for correct angle values
                radians -= 2 * math.pi
            self.velocity.angular = self.angle_factor * radians

            if (self.velocity.linear < 0):
                self.velocity.angular = -self.velocity.angular

            self.velocity.linear = max(min(self.velocity.linear, 0.3), -0.3)
            self.velocity.angular = max(min(self.velocity.angular, 1.0), -1.0)
            self.publish_velocity(self.velocity.linear, self.velocity.angular)
        else:
            self.publish_velocity()

        if (self.target != None):
            print(self.target)
        else:
            print("No target")

    def publish_velocity(self, linear=0.0, angular=0.0):
    	# Create message object of type TwistStamped
        msg = TwistStamped()
        # Configure message object
        msg.header.stamp = Clock().now().to_msg()
        msg.twist.linear.x = float(linear)
        msg.twist.angular.z = float(angular)
        # Send message object to topic /cmd_vel
        self.vel_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ReactiveNavigation()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.vel_publisher.publish(TwistStamped())
        time.sleep(0.1)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()






