from google.cloud import speech


client = speech.SpeechClient.from_service_account_file('key.json')
file_name = "output.wav"

with open (file_name, 'rb') as f:
    mp3_data = f.read()

audioFile = speech.RecognitionAudio(content=mp3_data)

config = speech.RecognitionConfig(
        sample_rate_hertz = 16000,
        enable_automatic_punctuation = True,
        language_code ='en-US'
)

response = client.recognize(
    config  = config,
    audio =audioFile
)

for result in response.results:
    print ("Transcript: {} ".format(result.alternatives[0].transcript))