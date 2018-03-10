import socket
import threading

class SocketServer(socket.socket):
    clients = []

    def __init__(self):
        socket.socket.__init__(self)
        #To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(('0.0.0.0', 5566))
        self.listen(5)

    def run(self):
        print ("Server started")
        try:
            self.accept_clients()
        except Exception as ex:
            print (ex)
        finally:
            print ("Server closed")
            for client in self.clients:
                client.close()
            self.close()

    def recieve(self, client):
        print("noo");
        while 1:
            data = client.recv(1024)
            if data == '':
                break
            #Message Received
            self.onmessage(client, data)
        #Removing client from clients list
        self.clients.remove(client)
        #Client Disconnected
        self.onclose(client)
        #Closing connection with client
        client.close()
        #Closing thread
        threading.exit()
        print (self.clients)
    
    
    def accept_clients(self):
        while 1:
            (clientsocket, address) = self.accept()
            #Adding client to clients list
            self.clients.append(clientsocket)
            #Client Connected
            self.onopen(clientsocket)
            #Receiving data from client
            threading.Thread(target=self.recieve, args=(clientsocket,)).start()

    def broadcast(self, message):
        #Sending message to all clients
        for client in self.clients:
            client.send(message)

    def onopen(self, client):
        pass

    def onmessage(self, client, message):
        pass

    def onclose(self, client):
        pass