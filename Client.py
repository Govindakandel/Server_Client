import socket 
import threading


# locking thread while updating client and nickname list
lock = threading.Lock()

def receive_msg () :
      
    while True :
        try :
            recv_message = client.recv(1024).decode()
            if recv_message == "NICK:" :
                Nickname = str(input("Enter your Nickname to Connect to Server : "))
                client.send(Nickname.encode())
            elif recv_message == "server-quit" :
                client.close()
                print("Sucessfully left the server ..")
                break
            else :
                 print(f"\n{recv_message}")
        except :
            print('An Error Occured !!')
            print("Disconnecting From the server ...")
            client.close()
            break
        
def send_msg() :
    

    while True :
        try :   
          message_send = str(input())
          client.send(message_send.encode())
          if message_send.lower() == "server-quit" :
            break 

        except :
            print('An Error Occured !!')
            print("Disconnecting From the server ...")
            client.close()
            break




print("-"*20+"CONNECT TO SERVER "+"-"*20)


Start = True 
while Start :
   # server details 
      Host = str(input('Enter the server IP ["Q" to quit] :'))  # server ip address
      if Host.upper() == "Q" :
          Start = False
          print("Program is closed ")
          break
      port = int(input('Enter port number to connect :')) # server connecting port
    
      server_Address = (Host,port)  
    
      try :
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # creating socket for ipv4 and tcp protocal 
        client.connect(server_Address)
        print( " Sucessfully connect to the server ...")
        print("-"*40)

        
        # existing loop
        Connect_Sucess = True
        Start = False

      except :
        print('Faild to connect to server ...')


if Connect_Sucess : 
    with lock :
       # welcome message 
       print("-"*40)
       print("Welcome to Server chat room !!")
       print("-- Some importants commands --")
       print("See online users : <online-user.info>")
       print("Sending private message : </pm> <receiver-user> <message>")
       print("Quitting the server : <server-quit> ") 
       print("-"*40)
       # creating threads to handle both recieving and sending message
       thread_recvmsg = threading.Thread(target=receive_msg)
       thread_sendmsg = threading.Thread(target=send_msg)
       thread_recvmsg.start()
       thread_sendmsg.start()