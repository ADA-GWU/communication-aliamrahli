[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/XUudKV-B)

## Design and Implementation of a Ring System in Python

Our distributed system will use a synchronous communication model, where nodes interact with each other in a **request-response** fashion. Protocol will be 
**Socket**

---

## Protocols

1. VERIFY ID=? ORGANIZATOR=?
2. VERIFIED ID=? IP-ADD=? LIST=?
3. NOT-VERIFIED ID=? ORGANIZATOR=?
4. UPDATE ORGANIZATOR=? LIST=? 
5. MSG ID=? ORGANIZATOR TEXT=?

##### note: list should be in LIST=["item1", "item2"] format, ? is placeholder
---

## Exucution flow examples

ring: A1->B2->C3->D4->A1

### Verified cycle

1. E5 sends "VERIFY ID=5 ORGANIZATOR=0" (if node wants to join ring then it shoudl set organizator to 0) request to A1
2. A1 first sets organizator its own id (0 indicates A1 that it should be the organizator) then validates (in our case 1 != 5) then forwards the same request to B2 (note: to forward request create new socket connect it to listener socket of next node at port 6650, after sending close the socket)
3. repeat step 3 for C3 and D4
4. after D4 forwards request to A1 it will check that organizator is equal to its own id and instead of forwarding request to next node, it will create new request with "VERIFIED ID=5 IP-ADD=B2_ip LIST = [A1, E5, B2, C3, D4]". A1 should also change its own list and pointer to the next node
5. When E5 Receives response it will set its own next pointer and list and will start update method. It will send "UPDATE LIST=[A1, E5, B2, C3, D4] ORGANIZATOR=5".
6. UPDATE will go through all nodes in the ring and if their id is not equal to organizator then they will update their list.
7. When finally update reaches E5 it will stop forwarding request and will stop (because id is equal to organizator) 

### MESSAGE CYCLE

1. Send message with request "MSG ID=? TEXT=?" message will iterate the ring until it reaches node with requested id. (Potential case to be discussed what if id is not in the ring)

### NOT VERIFIED CYCLE

1. Lets look at first example but instead of E5 now we have E3. When request reaches C3 it will froward "NOT-VERIFIED ID=3 ORGANIZATOR=1"  
2. D4 will not check id and will just forward response to A1
3. A1 then will forward it to E3
4. Because of the the id field E3 will understand that it should try again and send another request  