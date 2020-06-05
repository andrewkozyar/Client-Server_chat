from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import datetime


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    try:
        while True:
            client, client_address = SERVER.accept()
            print("%s:%s has connected." % client_address)
            currentDT = datetime.datetime.now() #current time for message
            current_time = currentDT.strftime("%H:%M:%S")
            try:
                client.send(bytes(f"[{current_time}]  Welcome! Type your name and we start:", "utf8"))
                addresses[client] = client_address
                Thread(target=handle_client, args=(client,)).start() #redirection to another method
            except BaseException:
                print("Wrong connection.")
    except KeyboardInterrupt:
        exit(0)

def handle_client(client, ):  # Takes client socket as argument.
    """Handles a single client connection."""
    try:
        currentDT = datetime.datetime.now() #current time for message
        current_time = currentDT.strftime("%H:%M:%S")
        while True: #loop for entering correct name
            name = ""
            if name == "quit" or name == "exit": #exit or disconnect of user without login
                break
            try: #try receive name of user
                name = client.recv(BUFSIZ).decode("utf8")
            except OSError:
                pass
            try:
                if name[0] != "%": #name cannot begin with #, it's for command
                    if name != "exit" and name != "quit": #name cannot be exit or quit
                        clients[client] = name #save client socket
                        welcome = f"[{current_time}]  Hi, {name}! It\'s a simple chat."
                        client.send(bytes(welcome, "utf8"))
                        time.sleep(0.1)
                        to_exit = f"[{current_time}]  Enjoy communicating with other users (type %help to show commands):"
                        client.send(bytes(to_exit, "utf8"))
                        to_send = f"{name} has joined the chat! Say hello to {name}."
                        broadcast(to_send)

                        while True: #loop for messages
                            msg = client.recv(BUFSIZ).decode("utf8") #receive message
                            if msg == "exit": #user send exit
                                #client.send(bytes("exit", "utf8"))
                                client.close()
                                print("%s:%s has disconnected." % addresses[client])
                                del clients[client]
                                broadcast("%s has left the chat." % name)
                                name = "exit"
                                break
                            elif msg == "quit": #user send quit
                                #client.send(bytes("quit", "utf8"))
                                client.close()
                                print("%s:%s has disconnected." % addresses[client])
                                del clients[client]
                                broadcast("%s has left the chat." % name)
                                name = "quit"
                                break
                            elif msg[0] == "%": #user send some command
                                if msg[1:7] == "ping:;": #handle ping
                                    to_send = f"[{current_time}]  Successfully ping to server."
                                    client.send(bytes(to_send, "utf8"))
                                elif msg[1:5] == "echo" and msg[-1] == ";":  #handle echo
                                    to_send = f"[{current_time}]  ECHO{msg[5:-1]}"
                                    client.send(bytes(to_send, "utf8"))
                                elif msg[1:9] == "process:": #handle process
                                    output_file = ""
                                    i = 16
                                    while (msg[i] != " "):
                                        output_file +=msg[i]
                                        i+=1
                                    str_array = msg[i+1:]
                                    str_array = str_array[:-1]
                                    int_array = [int(k) for k in str_array.split(' ')]
                                    int_array.sort()
                                    to_send = f"[{current_time}]  Sorted array: file2-{output_file} {int_array}"
                                    client.send(bytes(to_send, "utf8"))
                                elif msg[1:5] == "help": #handle help
                                    client.send(bytes(f"[{current_time}]  List of available command:", "utf8"))
                                    time.sleep(0.1)
                                    client.send(bytes(f"[{current_time}]     %ping:; - ping to server.", "utf8"))
                                    time.sleep(0.1)
                                    client.send(bytes(f"[{current_time}]     %echo:<YOUR_TEXT>; - echo request.", "utf8"))
                                    time.sleep(0.1)
                                    client.send(bytes(f"[{current_time}]     %process: file1-<YOUR_INPUT_FILE> file2-<YOUR_OUTPUT_FILE> ", "utf8"))
                                    time.sleep(0.1)
                                    client.send(bytes(f"[{current_time}]                - sorting file with an array of numbers.", "utf8"))
                                    time.sleep(0.1)
                                    client.send(bytes(f"[{current_time}]     exit - close program.", "utf8"))
                                else:
                                    broadcast(msg, name+": ") #broadcast messages for all user if wrong format of command
                            else:
                                broadcast(msg, name+": ") #broadcast messages for all user, it's usual message
                    else:
                        client.close()
                        print("%s:%s has disconnected." % addresses[client])
                else:
                    to_send_name = "[" + currentDT.strftime("%H:%M:%S") + "]  " + "Enter your name at first."
                    client.send(bytes(to_send_name, "utf8"))
            except IndexError:
                pass
    except KeyboardInterrupt:
        exit(0)


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    if msg == "shutdown": #send shutdown for all user if server shutdown
        for sock in clients:
            sock.send(bytes(msg, "utf8"))
    else: #send usual broadcast message
        currentDT = datetime.datetime.now()
        current_time = "[" + currentDT.strftime("%H:%M:%S") + "]  "
        for sock in clients:
            sock.send(bytes(current_time, "utf8")+bytes(prefix, "utf8")+bytes(msg, "utf8"))


clients = {}
addresses = {}

HOST = '127.0.0.1' #ip address of server
PORT = 33000 #port of server
BUFSIZ = 1024 #buffer size
ADDR = (HOST, PORT) #address of server

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR) #bind address to server


if __name__ == "__main__":
    SERVER.listen(50) #listen to 50 connection
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections, daemon=True) #intialize thread for connection user
    ACCEPT_THREAD.start() #run thread

    catch_exit = input("To shutdown server type something.\n") #shutdown server by enter something
    SERVER.close()
    broadcast("shutdown")
    exit(0)