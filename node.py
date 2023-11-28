import socket


class RingNode:
    def __init__(self, node_id, ip_address):
        self.node_id = node_id
        self.ip_address = ip_address
        self.send_port = 5555
        self.accept_port = 6666
        self.verify_port = 3333
        self.known_node = {}  # {neighbor_ip: neighbor_port}
        self.known_ip = list(self.known_node.keys())[0]
        self.send_socket = socket.socket()
        self.accept_socket = socket.socket()
        self.verify_socket = socket.socket()
        # self.send_socket.bind((self.ip_address, self.send_port))  # send port = 5555
        self.accept_socket.bind((self.ip_address, self.accept_port))  # accept port = 6666
        self.verify_socket.bind((self.ip_address,self.verify_port))
        self.accept_socket.listen(10)
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
            else:
                print("Not verified!")

    def request_verification(self, target_id, target_ip):
        while True:
            verification_message = f"VERIFY ID {target_id} {target_ip}"
            for neighbor_ip, neighbor_port in self.known_node.items():
                neighbor_address_accept = (neighbor_ip, 6666)
                neighbor_address_verify = (neighbor_ip, 3333)
                self.send_socket.connect(neighbor_address_accept)
                self.send_socket.sendall(verification_message.encode())
                self.send_socket.close()
                self.accept_socket.connect(neighbor_address_verify)
                response = self.accept_socket.recv(1024)
                response = response.decode('utf-8')
                return response

    def handle_messages(self):

        while True:
            message = self.accept_socket.recv(1024)
            message_parts = message.decode().split()
            print(message)

            if message_parts[0] == "VERIFIED":
                # VERIFIED ID 4 127.43.56.21 node_list{}

                return True, int(message_parts[2]), message_parts[3], message_parts[4]

            if message_parts[0] == "VERIFY":
                target_ip = message_parts[3]
                target_id = message_parts[2]
                verifier_ip = self.known_ip
                # finding index of my IP address in the list
                index = self.node_list["ipADDR"].index(self.ip_address)
                successor_index = index + 1
                self.successor_ip = self.node_list["ipADDR"][successor_index]

                # below condition shows that this request came second time as it is in
                # exists in the node_list
                # this condition may not work in very exclusive cases; may be will be updated
                if target_id != self.ip_address:
                    if any(target_ip in values for values in self.node_list.values()):
                        # adding new node as a next node to me
                        self.node_list["id"].insert(successor_index, target_id)
                        self.node_list["ipADDR"].insert(successor_index, target_ip)
                        verification_message = f"VERIFIED {message_parts[2]} {self.successor_ip} {self.node_list}"
                        self.socket.sendto(verification_message.encode(), (target_ip, 5555))

                    else:
                        # forward the request to next node
                        self.socket.sendto(message.encode(), (self.successor_ip, 5555))
                        self.node_list["id"].append(target_id)
                        self.node_list["ipADDR"].append(target_ip)
                else:
                    message = "Not Verified!"
                    self.socket.sendto(message.encode(), (self.successor_ip, 5555))

        pass


if __name__ == "__main__":
    # Assuming first node starts with ID 1 and on localhost
    node1 = RingNode(node_id=1, ip_address="127.0.0.1", port=5555)
    node1.start()
