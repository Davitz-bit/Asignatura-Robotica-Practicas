import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
import numpy as np

class Lidar(Node):
    def __init__(self):
        super().__init__('lidar_node')
        
        qos_profile_b = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=10)
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile_b)

        self.N = 10
        self.scans = []
        self.done = False

    def scan_callback(self, msg):
        if len(self.scans) < self.N:
            self.scans.append(msg.ranges)
            print(f"Scan {len(self.scans)} done")

        if len(self.scans) == self.N and not self.done:
            self.analyze_scans()
            self.done = True

    def analyze_scans(self):
        for i in range(self.N):
            data = np.array(self.scans[i])
            min_data = np.min(data)
            max_data = np.max(data)
            mean_data = np.mean(data)
            print(f"N: {i+1} | Min: {min_data} | Max: {max_data} | Mean: {mean_data}")

def main(args=None):
    rclpy.init(args=args)
    node = Lidar()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()