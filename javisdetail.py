import os  # 운영체제 관련 기능 (폴더 생성, 파일 경로 조작 등)에 쓰임
import wave  # .wav 오디오 파일 입출력용 모듈
import csv  # CSV 파일 입출력용 모듈
from datetime import datetime  # 현재 날짜와 시각 정보를 얻기 위한 모듈

import pyaudio  # 음성 녹음 기능을 제공하는 외부 라이브러리
import speech_recognition as sr  # 음성 -> 문자 변환 기능 외부 라이브러리


def create_records_folder():
    """
    'records' 폴더가 존재하지 않으면 새로 만들고,
    폴더 이름을 반환하는 함수입니다.
    녹음된 음성파일들을 저장할 공간을 만듭니다.
    """
    folder = 'records'  # 저장용 폴더명 지정
    if not os.path.exists(folder):  # 폴더가 없으면
        os.mkdir(folder)  # 새로운 폴더 생성
    return folder  # 폴더명 반환


def get_timestamp_filename():
    """
    현재 시각을 기준으로 '년월일-시분초.wav' 형식의 문자열을 만들어서
    음성 녹음 저장용 파일명을 반환합니다.
    예를 들어 20250827-182900.wav 와 같은 형태입니다.
    """
    now = datetime.now()  # 현재 시각을 datetime 객체로 가져오기
    timestamp = now.strftime('%Y%m%d-%H%M%S')  # 포맷팅하여 문자열 생성 (년월일-시분초)
    filename = f'{timestamp}.wav'  # 확장자 추가하여 파일명 완성
    return filename  # 생성된 파일명 반환


def record_audio(duration=10, sample_rate=44100, channels=1, chunk=1024):
    """
    시스템 기본 마이크로부터 음성을 녹음하는 함수입니다.

    - duration: 녹음 길이(초 단위), 기본은 10초입니다.
    - sample_rate: 초당 샘플링 횟수 (Hz), 기본 44100Hz (CD 품질)
    - channels: 채널 수, 기본은 1채널(모노)
    - chunk: 버퍼 크기(프레임), 한 번에 처리할 음성 데이터 양

    녹음된 음성 데이터를 바이트 리스트로 반환합니다.
    """
    p = pyaudio.PyAudio()  # PyAudio 객체 생성

    # 녹음용 스트림 생성:
    # 16비트(2바이트), 모노, sample_rate, 입력 스트림으로 설정
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print('Recording started...')  # 녹음 시작 알림 출력
    frames = []  # 녹음 데이터 저장 리스트 초기화

    # duration 동안 버퍼 단위로 음성 데이터 읽기
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)  # 읽어온 데이터를 리스트에 추가

    print('Recording finished.')  # 녹음 완료 알림 출력

    # 스트림과 PyAudio 종료 (자원 해제)
    stream.stop_stream()
    stream.close()
    p.terminate()

    return frames  # 녹음된 데이터 반환


def save_audio_file(frames, folder, filename,
                    sample_rate=44100, channels=1):
    """
    녹음된 음성 데이터를 .wav 파일 형태로 저장하는 함수입니다.

    - frames: 녹음된 음성 데이터(바이트 리스트)
    - folder: 저장할 폴더 경로
    - filename: 저장할 파일명 (확장자 포함)
    - sample_rate, channels: 녹음 당시의 샘플링 속도, 채널 수

    저장된 파일 경로를 반환합니다.
    """
    filepath = os.path.join(folder, filename)  # 파일 경로 생성 (폴더 + 파일명)

    wf = wave.open(filepath, 'wb')  # write 모드로 .wav 파일 열기
    wf.setnchannels(channels)  # 오디오 채널 수 설정
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))  # 샘플 폭 지정 (16비트)
    wf.setframerate(sample_rate)  # 샘플링 비율(Hz) 설정
    wf.writeframes(b''.join(frames))  # 녹음된 음성 데이터를 파일에 기록
    wf.close()  # 파일 닫기

    print(f'File saved at: {filepath}')  # 저장 위치 출력
    return filepath  # 저장된 파일 경로 반환


def list_audio_files(folder='records'):
    """
    지정한 폴더 내에 있는 모든 .wav 확장자를 가진 음성파일 목록을 리스트로 반환합니다.
    """
    return [f for f in os.listdir(folder) if f.endswith('.wav')]


def speech_to_text(audio_filepath):
    """
    주어진 음성 파일로부터 텍스트를 추출하는 함수입니다.

    speech_recognition 라이브러리의 Google 무료 API를 사용해 인식합니다.

    인식 실패 시 빈 문자열을 반환합니다.
    """
    recognizer = sr.Recognizer()  # 음성 인식기 객체 생성
    with sr.AudioFile(audio_filepath) as source:
        audio = recognizer.record(source)  # 전체 음성 파일 읽기

    try:
        text = recognizer.recognize_google(audio, language='ko-KR')  # 한국어 인식 시도
    except sr.UnknownValueError:
        # 음성 인식이 불가능한 경우 (음성 없음 등)
        text = ''
    except sr.RequestError as e:
        # API 요청 실패 (네트워크 문제 등)
        print(f'Speech recognition error: {e}')
        text = ''

    return text


def save_transcript_to_csv(audio_filepath, transcript_text):
    """
    음성 인식 결과 텍스트를 CSV 파일로 저장하는 함수입니다.

    저장 파일명은 음성 파일명과 같고 확장자만 .csv 입니다.

    CSV는 'Time(Seconds)', 'Text' 컬럼으로 구성하며,
    여기서는 전체 녹음시간과 텍스트 한 줄만 저장합니다.
    """
    folder = os.path.dirname(audio_filepath)  # 파일 경로에서 폴더 경로 추출
    base_name = os.path.splitext(os.path.basename(audio_filepath))[0]  # 확장자 제외한 파일명 추출
    csv_filename = f'{base_name}.csv'  # csv 파일명 생성 (같은 이름, 확장자만 csv)
    csv_filepath = os.path.join(folder, csv_filename)  # 저장할 csv 전체 경로

    with wave.open(audio_filepath, 'rb') as wf:
        frames = wf.getnframes()  # 총 프레임 수
        rate = wf.getframerate()  # 샘플링 속도(Hz)
        duration = frames / float(rate)  # 음성 길이(초 단위 계산)

    with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time(Seconds)', 'Text'])  # 헤더(컬럼명) 작성
        writer.writerow([f'{duration:.2f}', transcript_text])  # 녹음 길이 및 변환 텍스트 기록

    print(f'Transcript saved as {csv_filepath}')  # 저장 완료 안내 메시지 출력


def main():
    """
    주요 실행 함수:
    1. 음성 저장용 폴더 생성 및 준비
    2. 10초간 음성 녹음 후 .wav로 저장
    3. 폴더 내 모든 wav 파일 리스트를 가져와
       각각 음성인식(STT) 수행 후 인식 결과를 CSV로 저장
    """
    folder = create_records_folder()  # 폴더 생성/준비
    filename = get_timestamp_filename()  # 파일명 생성 (시간 기반)
    frames = record_audio(duration=10)  # 10초간 음성 녹음
    audio_path = save_audio_file(frames, folder, filename)  # 파일 저장

    wav_files = list_audio_files(folder)  # 폴더 내 wav 파일 목록 가져오기

    for wav_file in wav_files:
        path = os.path.join(folder, wav_file)
        print(f'Processing {wav_file}...')  # 처리중인 파일명 출력
        text = speech_to_text(path)  # 음성 -> 텍스트 변환
        print(f'Transcript: {text}')  # 변환된 텍스트 출력
        save_transcript_to_csv(path, text)  # CSV 저장


if __name__ == '__main__':
    main()  # 직접 실행 시 메인 함수 호출
