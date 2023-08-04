import pyaudio
import wave
from google.cloud import speech

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
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return "output.wav"

# Set up Google Cloud Speech-to-Text client
client = speech.SpeechClient.from_service_account_file('key.json')

# Get audio from the microphone
wav_file = get_audio_from_microphone()

# Read the audio data from the WAV file
with open(wav_file, 'rb') as f:
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

# Print the transcribed text
for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))
