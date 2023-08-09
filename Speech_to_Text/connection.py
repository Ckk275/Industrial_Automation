import socket
import time


# global variables for server_socket, client_socket, client_address
server_socket = None
client_socket = None
client_address = None

# Fn to Create a TCP socket and start a server
def start_tcp_server(host, port):
    # Create a TCP socket and save to global variable
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print("Server listening on %s:%s" % (host, port))

        # Accept a client connection and save to global variables
        global client_socket
        global client_address
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from %s:%s" % (client_address[0], client_address[1]))
        #Audio.SayEZB('Connected to PLC');
        
        # Move to pickup initial position
        #controlCommand("Auto Position", "AutoPositionAction", "Pick Prep");
        
    
    # Handle exceptions
    except KeyboardInterrupt:
        print("Server interrupted")
    except Exception as e:
        print("Error: %s" % str(e))
        raise Exception('Error in start_tcp_server()') from e
        
# Fn to Receive data from the client
def receive():
    data = client_socket.recv(1024).decode('utf-8')
    return data

# Fn to Send data to the client
def send(data_string):
    client_socket.send(data_string.encode('utf-8'))

# Fn to Close the server socket
def close_server():
    server_socket.close()

# Fn to Close the client socket
def close_client():
    client_socket.close()

# Fn to get the systems IP address. If not available use localhost
def get_ip_address():
    try:
        # Get the IP address of the system
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address
    except Exception as e:
        print("Error getting IP address: %s" % str(e))
        return

# main function
def main():
    try:
        # Get the IP address of the system
        ip_address = get_ip_address()
        port = 10998

        # Start the TCP server
        start_tcp_server(ip_address, port)

        # Receive pilot msg from the client and send acknowledgement
        pilot_msg = receive()
        print("Received pilot msg: %s" % pilot_msg)
        send('Confirmed')

        # Receive data from the client in loop
        while True:
            data = receive()
            print("Received data: %s" % data)

            # Check if the client has disconnected
            if not data:
                print("Client Disconnected")
                break

            # Command JD to Pick and Place
           # Audio.SayEZB('Picking item');
           # controlCommand("Auto Position", "AutoPositionAction", "Pick And Place");
            time.sleep(8)

            # Send a receive acknowledgement response back to the client
            send('Picked Up')
            print("Sent response to client")
    except KeyboardInterrupt:
        print("Server interrupted")
        
    except Exception as e:
        print("Error: %s" % str(e))
    
    finally:
        # Close the server socket
        close_server()
        #Audio.SayEZBWait('bye bye')

# Call the main function
main()