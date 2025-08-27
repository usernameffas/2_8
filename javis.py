import os
import wave
import csv
from datetime import datetime

import pyaudio
import speech_recognition as sr  # STT 라이브러리

def create_records_folder():
    folder = 'records'
    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder

def get_timestamp_filename():
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d-%H%M%S')
    filename = f'{timestamp}.wav'
    return filename

def record_audio(duration=10, sample_rate=44100, channels=1, chunk=1024):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print('Recording started...')
    frames = []

    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print('Recording finished.')

    stream.stop_stream()
    stream.close()
    p.terminate()

    return frames

def save_audio_file(frames, folder, filename,
                    sample_rate=44100, channels=1):
    filepath = os.path.join(folder, filename)
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f'File saved at: {filepath}')
    return filepath

def list_audio_files(folder='records'):
    return [f for f in os.listdir(folder) if f.endswith('.wav')]

def speech_to_text(audio_filepath):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_filepath) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        text = ''
    except sr.RequestError as e:
        print(f'Speech recognition error: {e}')
        text = ''
    return text

def save_transcript_to_csv(audio_filepath, transcript_text):
    folder = os.path.dirname(audio_filepath)
    base_name = os.path.splitext(os.path.basename(audio_filepath))[0]
    csv_filename = f'{base_name}.csv'
    csv_filepath = os.path.join(folder, csv_filename)

    with wave.open(audio_filepath, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)

    with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time(Seconds)', 'Text'])
        writer.writerow([f'{duration:.2f}', transcript_text])

    print(f'Transcript saved as {csv_filepath}')

def main():
    folder = create_records_folder()
    filename = get_timestamp_filename()
    frames = record_audio(duration=10)
    audio_path = save_audio_file(frames, folder, filename)

    wav_files = list_audio_files(folder)

    for wav_file in wav_files:
        path = os.path.join(folder, wav_file)
        print(f'Processing {wav_file}...')
        text = speech_to_text(path)
        print(f'Transcript: {text}')
        save_transcript_to_csv(path, text)

if __name__ == '__main__':
    main()
