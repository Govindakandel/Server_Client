import socket
import threading
import datetime

# Server setup
HOST = socket.gethostbyname(socket.gethostname())  # Localhost
print(HOST)
PORT = 5500    # open  Port to listen on

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

Clients =[]
Nicknames =[]

# locking thread while updating client and nickname list
lock = threading.Lock()


def serect_message_send(client ,user_receiver,seceret_message) :
    try :
        if user_receiver in Nicknames :
           Index_client = Clients.index(client)
           sender_user = Nicknames[Index_client]

           Index_receiver = Nicknames.index(user_receiver)
           receiver_client = Clients[Index_receiver]

           receiver_client.send(f'\nprivate-message from {sender_user} : {seceret_message}'.encode())
           receiver_client.send('\nEnter the message :'.encode())
        else :
          client.send(f'No user as {user_receiver} is found '.encode())
          client.send('\n Please check Online user info for correct user-name ..'.encode())
          client.send('\nEnter the message :'.encode())

    except :
       if user_receiver in Nicknames : 
          Index_receiver = Nicknames.index(user_receiver)
          receiver_client = Clients[Index_receiver]
          print(f'{user_receiver} is offline ...')
          print('Removing user from server ..')
          Broadcast(receiver_client,f'{user_receiver} has left the server ..')
          with lock :
             receiver_client.close()
             del Clients[Index_receiver]
             del Nicknames[Index_receiver]

         

              
       



def online_info (client) :
   client.send(" --- Online User : --- ".encode())
   index_user =  Clients.index(client)
   user_nick = Nicknames[index_user]
   for nick  in Nicknames :
      if  user_nick != nick :
         client.send(f"Online-user:{nick}\n".encode())
   client.send("\nEnter the message".encode())

def Broadcast(client,message) : 
     client.send("Enter the message : ".encode()) 
     Index = Clients.index(client)
     nickname = Nicknames[Index]
     time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
     for user in Clients : 
              
           if user != client :
               try:                  
                user.send(f'[{time}] {nickname} : {message}'.encode()) # sending msg to individual user
                user.send('Enter the message :'.encode())
               except :
                   # if msg cannot send to user means he is offline or error 
                   # better to remove that user  user 

                    # removing user and its nickname                
                    Index_user = Clients.index(user)
                    user_nick = Nicknames[Index_user]
                    
                    # broadcast to other user  that left server 
                    Broadcast(user,f' Good Bye .. \n Leaving  serer ')

                    # after broadcast 
                    with lock :
                       del Clients[Index_user]
                       del Nicknames[Index_user]
                       user.close()

               


def receive_msg (client) :
    while True :
        try :
            recv_message = client.recv(1024).decode()

            # if message is quitting server 

            if recv_message.lower() == "server-quit" :
             # quitting the server request from client                         
              with lock : 
               if client in Clients :             
                Index = Clients.index(client)
                print(f"{Nicknames[Index]} is disconnecting From the server ...")
                client.send("server-quit".encode())
              with lock :
                Broadcast(client, f"{Nicknames[Index]} has left the server")               
                del Clients[Index]
                del Nicknames[Index]
                client.close()             
              break

            elif recv_message == "online-user.info" :
               online_info(client)

            elif recv_message.startswith("/pm")  :
               message_parts = recv_message.split(" ",2)

               if len(message_parts) < 3 :
                  client.send("Enter private message In correct format : </pm> <user> <message>".encode())
               else :
                 user_receiver = message_parts[1]
                 serect_message = message_parts[2]
                 serect_message_send(client,user_receiver,serect_message)
            
            else  :
             Broadcast(client,recv_message)
        except :
            print('An Error Occured !!')
            print("Disconnecting From the server ...")
            client.close()

            # removing client and their nickname from list
            
            with lock :
             Index = Clients.index(client)
             del Clients[Index]
             del Nicknames[Index]
            break


# accepting multiple clients 
def receive_client () :
    while True :
      client,client_address = server.accept()
      print(f"Connection established to {client_address}")
     

      # asking for nickname 
      client.send("NICK:".encode("utf-8"))
      nickname = client.recv(1024).decode("utf-8")
   
      while  nickname in Nicknames :
         client.send("[Nick-name already exist] Enter new NICK:".encode("utf-8"))
         nickname = client.recv(1024).decode("utf-8")

      print(f"Client nickname is set to {nickname}")



      with lock : 
         # Appending client sockets and nicknames to respective lists..
         Clients.append(client)
         Nicknames.append(nickname)
      Broadcast(client,f'{nickname} has joined the server ...')   
         
 
     # creating threads to handle new clients and  recieving  messages from different clients .
      thread_recvmsg = threading.Thread(target=receive_msg,args=(client,))
      thread_recvmsg.start()   
           
   


print('Server is starting ....')
thread_client= threading.Thread(target=receive_client)
thread_client.start() 