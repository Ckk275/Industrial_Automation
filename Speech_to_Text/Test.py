import time
import threading
import pyaudio
import wave
from google.cloud import speech

# Function to capture audio from the microphone
def get_audio_from_microphone():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Use 16000 Hz sample rate for the Google Cloud Speech-to-Text API
    RECORD_SECONDS = 3

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

# Function to perform transcription
def transcribe_audio(wav_filename):
    with open(wav_filename, 'rb') as f:
        wav_data = f.read()

    # Set up Google Cloud Speech-to-Text client
    client = speech.SpeechClient.from_service_account_file('key.json')

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

    # Print the transcribed text
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

# Background thread to continuously capture audio and transcribe
def continuous_transcription():
    while True:
        wav_filename = get_audio_from_microphone()
        # Check if audio was captured
        if wav_filename:
            transcribe_audio(wav_filename)
        # Wait for 5 seconds before the next iteration
        time.sleep(5)

# Start the background thread
thread = threading.Thread(target=continuous_transcription)
thread.start()

# Keep the main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    thread.join()
