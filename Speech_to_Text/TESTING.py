import socket



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
    
def get_ip_address():
    try:
        # Get the IP address of the system
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address
    except Exception as e:
        print("Error getting IP address: %s" % str(e))
        return
    
def main():

    # Get the IP address of the system
    ip_address = get_ip_address()
    port = 10999

    # Start the TCP server
    start_tcp_server(ip_address, port)
    
main()
