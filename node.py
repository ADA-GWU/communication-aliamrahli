import socket
import random
import threading


class RingNode:
    def __init__(self, node_id, ip_address):
        self.neighbor_address = None
        self.node_id = random.randint(0, 100)
        self.ip_address = ip_address
        self.send_port = 6660
        self.accept_port = 6650
        self.known_node = {}  # {neighbor_ip: neighbor_port}
        self.node_list = ["127.0.0.1", "a", "b"]
        self.index = self.node_list.index(self.ip_address)
        # creating sockets
        self.send_socket = socket.socket()
        self.accept_socket = socket.socket()
        self.accept_socket.bind((self.ip_address, self.accept_port))  # accept port = 6666
        self.accept_socket.listen(10)

    # This function updates neighbor address whenever it is called
    def get_neighbor_address(self):
        self.neighbor_address = (self.node_list[0], 6650) if self.index == len(self.node_list) - 1 \
            else (self.node_list[self.index + 1], 6650)

    def start(self):
        # self.verify_id()
        self.initiate()

    def initiate(self):
        thread = threading.Thread(target=self.get_messages)
        thread.start()
        # self.get_messages()
        self.handle_messages()

    # this function works in separate thread to not block the process
    def get_messages(self):

        self.get_neighbor_address()
        while True:
            msg = input("Add node id and your message:")
            msg_parts = msg.split()
            target_id = msg_parts[0]
            text = msg_parts[1]
            full_msg = f"MSG ID={target_id} TEXT={text}"
            self.send_socket = socket.socket()
            self.send_socket.connect(self.neighbor_address)
            self.send_socket.sendall(full_msg.encode())
            self.send_socket.close()

    # def verify_id(self):
    #     while True:
    #         Incrementally try to get a unique ID
    #         verified, self.node_id, self.successor_ip, self.node_list = (
    #             self.request_verification(self.node_id + 1, self.ip_address))
    #
    #         if verified:
    #             print(f"Node {self.node_id} verified.")
    #             self.handle_messages()
    #             break
    #         else:
    #             print("Not verified!")
    #
    # def request_verification(self, target_id, target_ip):
    #     while True:
    #         verification_message = f"VERIFY ID {target_id} {target_ip}"
    #         for neighbor_ip, neighbor_port in self.known_node.items():
    #             neighbor_address_accept = (neighbor_ip, 6666)
    #             neighbor_address_verify = (neighbor_ip, 3333)
    #             self.send_socket.connect(neighbor_address_accept)
    #             self.send_socket.sendall(verification_message.encode())
    #             self.send_socket.close()
    #             self.accept_socket.connect(neighbor_address_verify)
    #             response = self.accept_socket.recv(1024)
    #             response = response.decode('utf-8')
    #             return response

    def handle_messages(self):

        while True:
            pass
            message = self.accept_socket.recv(1024).decode()
            message_parts = message.split()
            print(message)
            message_type = message_parts[0]
            self.get_neighbor_address()

            if message_type == "MSG":
                if message_parts[1] == f"ID={self.node_id}":
                    print("This message is for me! /n")
                    print(message)
                else:
                    if message_parts[3] == f"ORGANIZATOR={self.node_id}":
                        print("Destination node isn't found in the ring")
                    else:
                        send_socket = socket.socket()
                        send_socket.connect(self.neighbor_address)
                        send_socket.sendall(message.encode())
                        send_socket.close()

            # if message_type == "VERIFIED":
            #     # VERIFIED ID 4 127.43.56.21 node_list{}
            #
            #     return True, int(message_parts[2]), message_parts[3], message_parts[4]
            #
            # if message_type == "VERIFY":
            #     target_ip = message_parts[3]
            #     target_id = message_parts[2]
            #     verifier_ip = self.known_ip
            #     # finding index of my IP address in the list
            #     index = self.node_list["ipADDR"].index(self.ip_address)
            #     successor_index = index + 1
            #     self.successor_ip = self.node_list["ipADDR"][successor_index]
            #
            #     # below condition shows that this request came second time as it is in
            #     # exists in the node_list
            #     # this condition may not work in very exclusive cases; may be will be updated
            #     if target_id != self.ip_address:
            #         if any(target_ip in values for values in self.node_list.values()):
            #             # adding new node as a next node to me
            #             self.node_list["id"].insert(successor_index, target_id)
            #             self.node_list["ipADDR"].insert(successor_index, target_ip)
            #             verification_message = f"VERIFIED {message_parts[2]} {self.successor_ip} {self.node_list}"
            #             self.socket.sendto(verification_message.encode(), (target_ip, 5555))
            #
            #         else:
            #             # forward the request to next node
            #             self.socket.sendto(message.encode(), (self.successor_ip, 5555))
            #             self.node_list["id"].append(target_id)
            #             self.node_list["ipADDR"].append(target_ip)
            #     else:
            #         message = "Not Verified!"
            #         self.socket.sendto(message.encode(), (self.successor_ip, 5555))

        pass


if __name__ == "__main__":
    # Assuming first node starts with ID 1 and on localhost
    node1 = RingNode(node_id=1, ip_address="127.0.0.1")
    node1.start()
