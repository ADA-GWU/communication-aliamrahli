import socket
import threading
import time


class RingNode:
    def __init__(self, node_id, ip_address, port):
        self.node_id = node_id
        self.ip_address = ip_address
        self.port = port
        self.neighbors = {}  # {node_id: ip_address}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip_address, port))
        self.successor_id = None
        self.successor_ip = None
        self.predecessor_id = None
        self.predecessor_ip = None

    def start(self):
        self.verify_id()

    def verify_id(self):
        while True:
            # Incrementally try to get a unique ID
            verified, self.node_id, self.successor_id, self.successor_ip = self.request_verification(self.node_id + 1)

            if verified:
                # self.node_id = next_node_id
                # self.neighbors[next_node_id] = next_node_ip
                print(f"Node {self.node_id} verified.")
                break

    def request_verification(self, target_id):
        while True:
            verification_message = f"VERIFY ID {target_id}"
            for neighbor_id, neighbor_ip in self.neighbors.items():
                self.socket.sendto(verification_message.encode(), (neighbor_ip, self.port))

            response, _ = self.socket.recvfrom(1024)
            response_parts = response.decode().split()

            if response_parts[0] == "VERIFIED":
                # VERIFIED ID 4 3 127.43.56.21
                return True, int(response_parts[2]), int(response_parts[3]), response_parts[4]
            else:
                return False, 0, ""

    # def handle_messages:


if __name__ == "__main__":
    # Assuming first node starts with ID 1 and on localhost
    node1 = RingNode(node_id=1, ip_address="127.0.0.1", port=5555)
    node1.start()