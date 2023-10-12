import gradio as gr
import openai
import io
import soundfile as sf
import sounddevice as sd
import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import pygame
import tempfile
from elevenlabs import generate, play
import keyboard


recording = None  # This'll hold the recording data

def start_recording():
    global recording
    if recording is None:  # Only start a new recording if one isn't already rollin'
        print('Start recording...')
        recording = sd.rec(int(44100 * 50), samplerate=44100, channels=2, dtype='int16')

def stop_and_process_recording():
    global recording
    if recording is not None:  # Only stop and process if there's a recording going on
        print('Stop recording...')
        sd.stop()
        filename = 'recording.wav'
        sf.write(filename, recording, 44100)
        transcribe(filename)
        os.remove(filename)  # Trash the recording file after it's been used
        recording = None  # Reset the recording variable
        


# Set up the hotkey
keyboard.add_hotkey('alt+y', lambda e=None: start_recording())  # Will trigger on 'Alt + R + 1' combo
keyboard.on_release(lambda e=None: stop_and_process_recording())  # Will trigger on any key release

ffmpeg_bin_path = r'C:\Users\chuck\OneDrive\Desktop\Dev\chatgpt-api-whisper-api-voice-assistant-main\bin'#change this for where you store the ffmpeg file
if ffmpeg_bin_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + ffmpeg_bin_path

openai.api_key = "OpenAI API Key"
#OpenAICall
 #           ]
messages = [{"role": "system", "content": 'You are an AI that Acts like actors of famus characters real or fictional'},
]
def transcribe(audio):
    global messages
    messages.clear()
    # Convert the recorded audio to a supported format
    recorded_audio = AudioSegment.from_file(audio)
    converted_audio = 'converted_audio.wav'
    recorded_audio.export(converted_audio, format='wav')

    with open(converted_audio, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    messages.append({"role": "user", "content": "Act as Jordan Belfort AKA the wolf of wallstreet"}),#add any actor or famus celebrity u want
    messages.append({"role": "user", "content": transcript["text"]})
    


    response = openai.ChatCompletion.create(model="gpt-4-0314", messages=messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # Replace gTTS with ElevenLabs
    voice_id = "look on eleven labs for the voice ID u prefered"  # Replace this with the voice_id from ElevenLabs API
    api_key = "elevenlabs apikey" # Use the ElevenLabs API key variable
    model_id = "eleven_monolingual_v1"  # 11labs multilingual voice
    audio = generate(system_message['content'], voice=voice_id, api_key=api_key)

    # You can remove the temp file code and play audio directly
    audio_data, samplerate = sf.read(io.BytesIO(audio), dtype='int16')
    sd.play(audio_data, samplerate)
    sd.wait()

ui = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="text", title="Your AI Assistant Code by Sesh").launch(share=True)
ui.launch(share=True)
