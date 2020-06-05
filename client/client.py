from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import os
import time
import sys
import random
import platform


def receive(my_msg, msg_list, top, ip_field, port_field, bottom_frame):
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8") #receive message from server
            if msg == "shutdown": #server send shutdown
                disconnect(my_msg, msg_list, top, ip_field, port_field, bottom_frame) #disconnect user, hide message frame
                msg_list.insert(tkinter.END, "The server has shutdown.") #display that server shuydown
                msg_list.yview(tkinter.END) #move to the last message
            #elif msg == "exit": #server replied to exit
               # client_socket.close() #close connection
                #top.quit() #close tab
            elif msg.find("Sorted array: file2-") != -1: #server replied to process command
                output_file = ""
                _len = len(msg)
                i = 32
                while(msg[i] != " "):
                    output_file+= msg[i]
                    i+=1
                str_array = msg[i+2:-1]
                int_array = [int(k) for k in str_array.split(', ')]
                msg = msg[0:12] + f"Successfully sorted to file {output_file}."
                with open(output_file, 'w') as fw: #write array to output file
                    for i in int_array:
                        fw.write(str(i) + " ")
                msg_list.insert(tkinter.END, msg) #display reply
                msg_list.yview(tkinter.END) #move to the last message
            else:
                msg_list.insert(tkinter.END, msg) #display reply
                msg_list.yview(tkinter.END) #move to the last message
        except OSError:  # Possibly client has left the chat.
            break


def send(my_msg, top, msg_list):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get() #get text from message field
    my_msg.set("")  # Clears input field.
    if msg == "exit": #user send exit
        client_socket.send(bytes(msg, "utf8")) #sent exit to server
        client_socket.close() #close connection
        top.quit() #close tab
    elif msg == "quit": #user disconnect from server but no close tab
        client_socket.send(bytes(msg, "utf8")) #sent quit to server
        client_socket.close() #close connection
    elif msg[0:9] == "%process:" and msg.find("file1") != -1 and msg.find("file2") != -1: #user send process file to server
        input_list = []
        for i in range(100): #generate 100 random numbers
            input_list.append(random.randrange(1, 1000))
        input_file = ""
        _len = len(msg)
        i = 16
        while(msg[i] != " "): #hander input file
            input_file+= msg[i]
            i+=1
        j = msg.find("file2")
        output_file = msg[j+6:] #hander output file
        with open(input_file, 'w') as fw: #write to input file
            for i in input_list:
                fw.write(str(i) + " ")
            msg_list.insert(tkinter.END, f"Input file {input_file} generated.") #display that file generated
            msg_list.yview(tkinter.END) #move to the last message
        msg = "%process: file2-" + output_file + " "
        _len = len(input_list)
        while (_len != 0):
            msg+= str(input_list[_len-1]) + " "
            _len-=1
        client_socket.send(bytes(msg, "utf8")) #send to server file
    else:
        client_socket.send(bytes(msg, "utf8")) #send usual message


def on_closing(my_msg, top, msg_list):
    """This function is to be called when the window is closed."""
    my_msg.set("exit")
    try:
        send(my_msg, top, msg_list) #send to server exit
    except:
        top.quit() #close tab


def connect(ip_field_value, port_field_value, msg_list, ip_field, port_field, text_below_message, entry_field, send_button, bottom_frame, my_msg, top):
    """This function is to be called when the user press to button connect."""
    ip_server =  ip_field_value.get() #get entered address
    port_server =  port_field_value.get() #get entered port

    try:
        address_server = (ip_server, int(port_server))
    except: #something wrong with address of server
        msg_list.insert(tkinter.END, "Wrong IP address and port or server is shutdown.")
        msg_list.yview(tkinter.END) #move to the last message
        return

    global client_socket
    client_socket = socket(AF_INET, SOCK_STREAM)

    try: #try connect and show message frame
        client_socket.connect(address_server)
        msg_list.insert(tkinter.END, f"Successfully connected to server {ip_server}:{port_server}") #display successfully connection
        msg_list.yview(tkinter.END) #move to the last message
        ip_field.set("") #clean field with ip
        port_field.set("") #clean field with port
        #show message frame
        text_below_message.pack(pady=(5, 0))
        entry_field.pack()
        send_button.pack(pady=(5, 15))
        bottom_frame.pack()
    except: #wrond connection
        msg_list.insert(tkinter.END, "Wrong IP address and port or server is shutdown.")
        msg_list.yview(tkinter.END) #move to the last message

    receive_thread = Thread(target=lambda: receive(my_msg, msg_list, top, ip_field, port_field, bottom_frame) , daemon=True) #initialize thread for receiving message from server
    receive_thread.start() #start thread


def disconnect(my_msg, msg_list, top, ip_field, port_field, bottom_frame):
    """This function is to be called when the user press to button disconnect."""
    my_msg.set("quit")
    try:
        send(my_msg, top, msg_list) #send quit to server
        msg_list.insert(tkinter.END, "Disconnect from server.") #display disconnect
        msg_list.yview(tkinter.END) #move to the last message
        ip_field.set("127.0.0.1") #fill ip field with default address
        port_field.set("33000") #fill port field with default port
        bottom_frame.pack_forget() #hide message frame
        return
    except:
        msg_list.insert(tkinter.END, "You have not connected to the server yet.")
        msg_list.yview(tkinter.END) #move to the last message


def main():
    top = tkinter.Tk() #initialize tkinter object
    top.title("Messenger") #set title

    top_frame = tkinter.Frame(top) #initialize frame for displaying message
    center_frame = tkinter.Frame(top) #initialize frame for connecting
    bottom_frame = tkinter.Frame(top) #initialize frame for sending message

    scrollbar = tkinter.Scrollbar(top_frame, width=18) #vertical scrollbar
    scrollbar_hor = tkinter.Scrollbar(center_frame, width=18, orient='horizontal') #horizontal scrollbar
    if platform.system() == "Windows":
        msg_list = tkinter.Listbox(top_frame, height=18, width=70, yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_hor.set) #initialize list box for message
        msg_list.config(bd=3, bg="#0e1621", selectbackground="#f5f5f5", fg="#f5f5f5", highlightcolor="#f5f5f5", highlightthickness=2, relief=tkinter.GROOVE, font=12, activestyle='none') #config list box
    else:
        msg_list = tkinter.Listbox(top_frame, height=25, width=75, yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_hor.set) #initialize list box for message
        msg_list.config(bd=3, bg="#0e1621", selectbackground="#f5f5f5", fg="#f5f5f5", highlightcolor="#f5f5f5", highlightthickness=2, relief=tkinter.GROOVE, font=20, activestyle='none') #config list box

    scrollbar.config(command=msg_list.yview)  #vertical scrollbar config
    scrollbar_hor.config(command=msg_list.xview) #horizontal scrollbar config

    #show widgets on frame for displaying message
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y, pady=(0, 1))
    if platform.system() == "Windows":
        scrollbar_hor.pack(side=tkinter.TOP, fill=tkinter.X, ipadx=310, padx=(0, 20), pady=(0, 15))
    else:
        scrollbar_hor.pack(side=tkinter.TOP, fill=tkinter.X, ipadx=355, padx=(0, 20), pady=(0, 15))
    top_frame.pack(side=tkinter.TOP)

    #initialize widget on frame for sending message
    text_below_message = tkinter.Label(bottom_frame, width=20, height=1, text="Your message:", font=25)
    text_ip = tkinter.Label(center_frame, width=3, height=1, text="IP:", font=25)
    text_port = tkinter.Label(center_frame, width=5, height=1, text="PORT:", font=25)
    my_msg = tkinter.StringVar()  # For the messages to be sent.
    entry_field = tkinter.Entry(bottom_frame, textvariable=my_msg, width=55, font=22)
    entry_field.bind("<Return>", lambda x: send(my_msg, top, msg_list))
    send_button = tkinter.Button(bottom_frame, text="Send", command= lambda: send(my_msg, top, msg_list), width=10, font=20)

    #initialize widget on frame for connecting
    ip_field = tkinter.StringVar()
    ip_field.set("127.0.0.1")
    port_field = tkinter.StringVar()
    port_field.set("33000")
    if platform.system() == "Windows":
        ip_field_value = tkinter.Entry(center_frame, textvariable=ip_field, width=15, font=16)
        port_field_value = tkinter.Entry(center_frame, textvariable=port_field, width=15, font=16)
    else:
        ip_field_value = tkinter.Entry(center_frame, textvariable=ip_field, width=18, font=16)
        port_field_value = tkinter.Entry(center_frame, textvariable=port_field, width=18, font=16)
    connect_button = tkinter.Button(center_frame, text="Connect", command= lambda: connect(ip_field_value, port_field_value, msg_list, ip_field, port_field, text_below_message, entry_field, send_button, bottom_frame, my_msg, top), width=10, font=20)
    disconnect_button = tkinter.Button(center_frame, text="Disconnect", command= lambda: disconnect(my_msg, msg_list, top, ip_field, port_field, bottom_frame), width=10, font=20)

    #show widget on frame for connecting
    text_ip.pack(side=tkinter.LEFT, padx=(15, 0))
    ip_field_value.pack(side=tkinter.LEFT)
    text_port.pack(side=tkinter.LEFT, padx=(20, 0))
    port_field_value.pack(side=tkinter.LEFT)

    connect_button.pack(side=tkinter.LEFT, padx=(15, 0))
    disconnect_button.pack(side=tkinter.LEFT, padx=(15, 0))
    center_frame.pack(side=tkinter.TOP, pady=(0, 15))

    top.protocol("WM_DELETE_WINDOW", lambda x=my_msg, y=top, z=msg_list: on_closing(x, y, z)) #call function if user close tab

    top.mainloop()  # Starts GUI execution.

BUFSIZ = 1024 #buffer size
main()