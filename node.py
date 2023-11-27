import socket
import threading
import time


class RingNode:
    def __init__(self, node_id, ip_address, port):
        self.node_id = node_id
        self.ip_address = ip_address
        self.port = port
        self.known_node = {}  # {neighbor_ip: neighbor_port}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip_address, port))
        self.successor_id = None
        self.successor_ip = None
        self.predecessor_id = None
        self.predecessor_ip = None
        self.node_list = {"id": [], "ipADDR": []}

    def start(self):
        self.verify_id()

    def verify_id(self):
        while True:
            # Incrementally try to get a unique ID
            verified, self.node_id, self.successor_ip, self.node_list = (
                self.request_verification(self.node_id + 1, self.ip_address))

            if verified:
                # self.node_id = next_node_id
                # self.neighbors[next_node_id] = next_node_ip
                print(f"Node {self.node_id} verified.")
                self.handle_messages()
                break

    def request_verification(self, target_id, target_ip):
        while True:
            verification_message = f"VERIFY ID {target_id} {target_ip}"
            for neighbor_ip, neighbor_port in self.known_node.items():
                self.socket.sendto(verification_message.encode(), (neighbor_ip, 5555))

            response, _ = self.socket.recvfrom(1024)  # response equals only "VERIFIED" or whole message?
            response_parts = response.decode().split()

            if response_parts[0] == "VERIFIED":
                # VERIFIED ID 4 127.43.56.21 node_list{}
                return True, int(response_parts[2]), response_parts[3], response_parts[4]
            else:
                return False, 0, ""

    def handle_messages(self):
        while True:
            message, _ = self.socket.recvfrom(1024)
            message_parts = message.decode().split()
            print(message)
            if message_parts[0] == "VERIFY":
                target_ip = message_parts[3]
                target_id = message_parts[2]
                # finding index of my IP address in the list
                index = self.node_list["ipADDR"].index(self.ip_address)
                successor_index = index + 1
                self.successor_ip = self.node_list["ipADDR"][successor_index]
                verification_message = f"VERIFIED {message_parts[2]} {self.successor_ip}"
                # below condition shows that this request came second time as it is in
                # exists in the node_list
                # this condition may not work in very exclusive cases; may be will be updated
                if any(message_parts[3] in values for values in self.node_list.values()):
                    self.socket.sendto(verification_message.encode(), (target_ip, 5555))
                else:
                    # forward the request to next node
                    self.socket.sendto(message.encode(), (self.successor_ip, 5555))
                    self.node_list["id"].append(target_id)
                    self.node_list["ipADDR"].append(target_ip)

        pass


if __name__ == "__main__":
    # Assuming first node starts with ID 1 and on localhost
    node1 = RingNode(node_id=1, ip_address="127.0.0.1", port=5555)
    node1.start()
