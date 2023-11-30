import ast
import socket
import random
import threading
import re


class RingNode:
    def __init__(self, node_id, ip_address):
        self.client_socket = None
        self.send_socket = None
        self.neighbor_address = None
        self.my_node_id = 1
        self.my_ip_address = ip_address
        self.send_port = 6660
        self.accept_port = 6650
        self.my_address = (ip_address, 6650)
        self.known_node = {}  # {neighbor_ip: neighbor_port}
        self.node_list = ["10.0.138.121", "10.0.161.151"]
        # my index in the node list
        self.index = self.node_list.index(self.my_ip_address)
        # creating accept socket
        self.accept_socket = socket.socket()
        self.accept_socket.bind((self.my_ip_address, self.accept_port))  # accept port = 6666
        self.accept_socket.listen(10)
        self.client_address = None

    # This function updates neighbor address whenever it is called
    def get_neighbor_address(self):

        if self.index == len(self.node_list) - 1:
            self.neighbor_address = (self.node_list[0], 6650)
        else:
            self.neighbor_address = self.node_list[self.index + 1], 6650

        # self.neighbor_address = ("10.0.161.151",6650)

    def start(self):
        print(f"My process id: {self.my_node_id}\n")
        thread = threading.Thread(target=self.send_messages)
        thread.start()
        # self.verify_id()
        self.handle_messages()
        # self.initiate()

    # this function works in separate thread to not block the process
    def send_messages(self):
        # print(self.neighbor_address)
        while True:
            msg = input("Add node id and your message:\n")
            msg_parts = msg.split()
            target_id = int(msg_parts[0])
            text = msg_parts[1]
            full_msg = f"MSG ID={target_id} TEXT={text} ORGANIZATOR={self.my_node_id}"

            while True:
                self.send_socket = socket.socket()
                self.get_neighbor_address()
                if self.neighbor_address[0] == self.my_ip_address:
                    print("There is only one node in the ring!")
                    break
                try:
                    self.send_socket.connect(self.neighbor_address)
                    self.send_socket.sendall(full_msg.encode())
                    break
                except ConnectionRefusedError as e:
                    print("The neighbor node is down. Forwarding it to node next to neighbor.")
                    self.node_list.remove(self.neighbor_address[0])
                    print(self.node_list)
                    self.send_socket.close()
                    print(e)

            self.send_socket.close()

    def verify_id(self):
        # initiate()
        # def initiate(self):

        while True:
            self.get_neighbor_address()
            print(self.neighbor_address)
            self.send_socket = socket.socket()
            verification_msg = f"VERIFY ID={self.my_node_id} ORGANIZATOR={0}"
            try:
                self.send_socket.connect(self.neighbor_address)
                self.send_socket.sendall(verification_msg.encode())
                self.send_socket.close()
                client_socket, client_address = self.accept_socket.accept()
                respond = self.accept_socket.recv(1024).decode()
                if respond.startswith("VERIFIED"):
                    # respond_parts = respond.split()
                    # list_part = respond_parts[3].split('=')[1]
                    pattern = r"LIST=\[(.*?)\]"
                    match = re.search(pattern, respond)
                    list_value_with_brackets = f"[{match.group(1)}]"
                    self.node_list = ast.literal_eval(list_value_with_brackets)
                    print("\n")
                    print(self.node_list)

                    print(self.node_list)
                    self.get_neighbor_address()
                    update_msg = f"UPDATE ORGANIZATOR={self.my_node_id} LIST={self.node_list}"
                    self.send_socket = socket.socket()
                    self.send_socket.connect(self.neighbor_address)
                    self.send_socket.sendall(update_msg.encode())
                    self.send_socket.close()
                    self.accept_socket.accept()
                    update_respond = self.accept_socket.recv(1024)
                    update_parts = update_respond.split()
                    organizator_id = int(update_parts[2].split('=')[1])
                    if organizator_id == self.my_node_id:
                        pass

                    self.handle_messages()
                    break
                if respond.startswith("NOT-VERIFIED"):
                    self.my_node_id += 1
                    self.send_socket.close()

            except ConnectionRefusedError:
                print("The node you are trying to connect is not reachable.")
                self.send_socket.close()
                break

    def handle_messages(self):
        while True:
            client_socket, client_address = self.accept_socket.accept()
            message = client_socket.recv(1024).decode()
            message_parts = message.split()
            print(message)
            message_type = message_parts[0]
            self.get_neighbor_address()

            if message_type == "MSG":
                id_string = message_parts[1]
                pattern = r"TEXT='(.*?)'"
                match = re.search(pattern, message)
                text_value = match.group(1)
                print(text_value)
                organizator = message_parts[3]
                # print(organizator)
                organizator_id = int(organizator.split('=')[1])

                target_id = int(id_string.split('=')[1])
                if target_id == self.my_node_id:
                    print("This message is for me! /n")
                    print(message)

                else:
                    print("not for me")
                    if organizator_id == self.my_node_id:
                        print("Destination node isn't found in the ring")
                    else:
                        while True:
                            send_socket = socket.socket()
                            self.get_neighbor_address()
                            try:
                                send_socket.connect(self.neighbor_address)
                                send_socket.sendall(message.encode())
                                send_socket.close()
                                break
                            except ConnectionRefusedError:
                                print("The neighbor node is down. Forwarding MSG request to the node next to "
                                      "neighbor.\n")
                                self.node_list.remove(self.neighbor_address[0])
                                print(self.node_list)
                                send_socket.close()

            # if message_type == "VERIFIED":
            #     # VERIFIED ID 4 127.43.56.21 node_list{}
            #
            #     return True, int(message_parts[2]), message_parts[3], message_parts[4]
            #
            elif message_type == "VERIFY":
                organizator = message_parts[2]
                organizator_id = int(organizator.split('=')[1])
                target = message_parts[1]
                target_id = int(target.split('=')[1])
                unverified_msg = f'NOT-VERIFIED ID={target_id} ORGANIZATOR={organizator_id}'
                if organizator_id == 0:
                    self.client_address = client_address

                    if target_id == self.my_node_id:
                        self.send_socket = socket.socket()
                        client_tuple = (client_address, 6650)
                        self.send_socket.connect(client_tuple)
                        self.send_socket.sendall(unverified_msg.encode())
                        self.send_socket.close()

                    else:
                        while True:
                            organizator_id = self.my_node_id
                            updated_message = f"VERIFY ID={target_id} ORGANIZATOR={organizator_id}"
                            print(updated_message)
                            self.get_neighbor_address()
                            self.send_socket = socket.socket()
                            try:
                                self.send_socket.connect(self.neighbor_address)
                                self.send_socket.sendall(updated_message.encode())
                                self.send_socket.close()
                                break
                            except ConnectionRefusedError as e:
                                print(
                                    "The neighbor node is down. Forwarding VERIFY request to the node next to neighbor.")
                                self.node_list.remove(self.neighbor_address[0])
                                print(self.node_list)
                                self.send_socket.close()
                                print(e)

                elif organizator_id == self.my_node_id:
                    self.get_neighbor_address()
                    self.node_list.insert(self.index + 1, self.client_address)
                    verified_msg = f"VERIFIED ID={target_id} IP-ADD={self.neighbor_address[0]} LIST={self.node_list}"
                    self.send_socket = socket.socket()
                    client_tuple = (self.client_socket, 6650)
                    self.send_socket.connect(client_tuple)
                    self.send_socket.sendall()

                elif organizator_id != 0:
                    if target_id == self.my_node_id:
                        self.get_neighbor_address()
                        self.send_socket = socket.socket()
                        self.send_socket.connect(self.neighbor_address)
                        self.send_socket.sendall(unverified_msg.encode())

                    else:
                        while True:
                            self.get_neighbor_address()
                            self.send_socket = socket.socket()
                            try:
                                self.send_socket.connect(self.neighbor_address)
                                self.send_socket.sendall(message.encode())
                                self.send_socket.close()
                                break
                            except ConnectionRefusedError:
                                print(
                                    "The neighbor node is down. Forwarding VERIFY request to the node next to neighbor.")
                                self.node_list.remove(self.neighbor_address[0])
                                print(self.node_list)
                                self.send_socket.close()

            # elif message_type == "VERIFIED":

            elif message_type == "UPDATE":
                pattern = r"LIST=\[(.*?)\]"
                match = re.search(pattern, message)
                list_value_with_brackets = f"[{match.group(1)}]"
                list_new = ast.literal_eval(list_value_with_brackets)

                organizator = message_parts[1]
                organizator_id = int(organizator.split('=')[1])
                if organizator_id == self.my_node_id:
                    print("Update finished")
                else:
                    while True:
                        try:
                            self.node_list = list_new
                            print(list_new)
                            print(type(list_new))
                            updated_message = f"UPDATE ORGANIZATOR={organizator_id} LIST={self.node_list}"
                            self.get_neighbor_address()
                            self.send_socket = socket.socket()
                            self.send_socket.connect(self.neighbor_address)
                            self.send_socket.sendall(updated_message)
                            self.send_socket.close()
                            break
                        except ConnectionRefusedError:
                            print(
                                "The neighbor node is down. Forwarding UPDATE request to the node next to neighbor.\n")
                            self.node_list.remove(self.neighbor_address[0])
                            print(self.node_list)
                            self.send_socket.close()

            elif message_type == "NOT-VERIFIED":
                organizator = message_parts[2]
                organizator_id = int(organizator.split('=')[1])
                target = message_parts[1]
                target_id = int(target.split('=')[1])
                unverified_msg = f'NOT-VERIFIED ID={target_id} ORGANIZATOR={organizator_id}'
                if organizator_id == self.my_node_id:
                    client_tuple = (self.client_address, 6650)
                    self.send_socket = socket.socket()
                    self.send_socket.connect(client_tuple)
                    self.send_socket.sendall(unverified_msg.encode())
                    self.send_socket.close()

                else:
                    while True:
                        try:
                            self.get_neighbor_address()
                            self.send_socket = socket.socket()
                            self.send_socket.connect(self.neighbor_address)
                            self.send_socket.sendall(unverified_msg.encode())
                            self.send_socket.close()
                            break
                        except ConnectionRefusedError:
                            print(
                                "The neighbor node is down. Forwarding NOT-VERIFIED request to the node next to neighbor.")
                            self.node_list.remove(self.neighbor_address[0])
                            print(self.node_list)
                            self.send_socket.close()


if __name__ == "__main__":
    # Assuming first node starts with ID 1 and on localhost
    node1 = RingNode(node_id=0, ip_address="10.0.138.121")
    node1.start()
