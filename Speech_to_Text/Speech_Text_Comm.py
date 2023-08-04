import socket
import pyaudio
import wave
import threading
from google.cloud import speech

# Set up Google Cloud Speech-to-Text client
client = speech.SpeechClient.from_service_account_file('key.json')

# Function to capture audio from the microphone
def get_audio_from_microphone():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Use 16000 Hz sample rate for the Google Cloud Speech-to-Text API
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    wav_filename = "output.wav"
    wf = wave.open(wav_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return wav_filename

# Global variables for server_socket, client_socket, client_address
server_socket = None
client_socket = None
client_address = None

# Lock to ensure synchronous recording and sending
lock = threading.Lock()

# Function to create a TCP socket and start a server
def start_tcp_server(host, port):
    # Create a TCP socket and save it to the global variable
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print("Server listening on %s:%s" % (host, port))

        # Accept a client connection and save it to global variables
        global client_socket
        global client_address
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from %s:%s" % (client_address[0], client_address[1]))
    except KeyboardInterrupt:
        print("Server interrupted")
    except Exception as e:
        print("Error: %s" % str(e))
        raise Exception('Error in start_tcp_server()') from e

# Function to receive data from the client
def receive():
    data = client_socket.recv(1024).decode('utf-8')
    return data

# Function to send data to the client
def send(data_string):
    client_socket.send(data_string.encode('utf-8'))

# Function to close the server socket
def close_server():
    server_socket.close()

# Function to close the client socket
def close_client():
    client_socket.close()

# Function to handle transcription
def handle_transcription():
    # Acquire the lock to ensure synchronized recording and sending
    with lock:
        print("Starting audio recording...")
        wav_filename = get_audio_from_microphone()
        print("Recording complete.")

        # Perform transcription
        print("Transcribing audio...")
        with open(wav_filename, 'rb') as f:
            wav_data = f.read()

        # Create RecognitionAudio and RecognitionConfig objects
        audio = speech.RecognitionAudio(content=wav_data)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            enable_automatic_punctuation=True,
            language_code='en-US'
        )

        # Perform the transcription
        response = client.recognize(
            config=config,
            audio=audio
        )

        # Get the transcribed text
        transcribed_text = ""
        for result in response.results:
            transcribed_text += result.alternatives[0].transcript + " "
        
        # Send the transcribed text back to the client
        send(transcribed_text)
        print("Transcription complete. Sent result to client.")

# Main function
def main():
    try:
        # Get the IP address of the system
        ip_address = socket.gethostbyname(socket.gethostname())
        port = 10999

        # Start the TCP server
        start_tcp_server(ip_address, port)

        # Receive pilot msg from the client and send acknowledgment
        initial_msg = receive()
        print("Received initial msg: %s" % initial_msg)
        send('Confirmed')

        # Receive data from the client in a loop
        while True:
            data = receive()
            print("Received data: %s" % data)

            # Check if the client wants to transcribe audio
            if data == 'Transcribe':
                # Call the function to handle transcription
                handle_transcription()

            # Check if the client has disconnected
            if not data:
                print("Client Disconnected")
                break

            # Send a receive acknowledgment response back to the client
            send('Received')
            print("Sent response to client")

    except KeyboardInterrupt:
        print("Server interrupted")
    except Exception as e:
        print("Error: %s" % str(e))
    finally:
        # Close the server socket
        close_server()

# Call the main function
if __name__ == "__main__":
    main()
