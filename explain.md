이 코드는 자동으로 음성을 10초 녹음하고 그것을 파일로 저장하며, 저장된 모든 음성 파일을 탐색하여 텍스트로 변환 후, 변환 텍스트를 각기 CSV 파일로 저장하는 작업을 순차적으로 수행한다.

음성 녹음 → 저장 → 인식 → 저장 의 전체 파이프라인을 포함하는 음성 기록 및 분석 도구의 기본 구조라 할 수 있다.


1. 필요한 라이브러리 가져오기
os : 운영체제 기능 (폴더 생성, 파일 경로 관리 등)

wave : WAV 오디오 파일을 생성하고 읽기 위한 표준 라이브러리

csv : 텍스트 변환 결과를 CSV 파일로 저장하기 위한 라이브러리

datetime : 현재 시간 정보 획득 (파일명에 사용)

pyaudio : 마이크에서 오디오 데이터를 녹음하는 외부 라이브러리

speech_recognition (as sr) : 음성 파일을 텍스트로 변환하는 Speech To Text(STT) 라이브러리

2. create_records_folder()
records 폴더가 존재하는지 확인하고 없으면 새로 생성한다.

음성 녹음 파일을 저장할 기본 폴더를 준비하는 역할이다.

함수 실행 결과로 폴더명을 반환한다.

3. get_timestamp_filename()
현재 시스템의 날짜와 시간을 받아와서,

년월일-시분초.wav 형식의 고유한 파일명을 만든다.

이 이름으로 저장해 파일이 덮어써지는 일이 없다.

4. record_audio(duration=10, sample_rate=44100, channels=1, chunk=1024)
PyAudio 객체를 생성해 마이크 입력 스트림을 연다.

형식은 16비트, 1채널, 44100Hz 샘플링 속도를 기본으로 한다.

duration초 동안 오디오 데이터를 버퍼 단위(chunk)로 계속 읽어온다.

읽어온 데이터를 리스트에 저장하고 녹음이 끝나면 스트림과 PyAudio 객체를 닫는다.

녹음된 음성 데이터를 바이너리 덩어리로 리스트 형태로 반환한다.

5. save_audio_file(frames, folder, filename, sample_rate=44100, channels=1)
frames에 저장된 녹음 데이터를 합쳐 WAV 파일로 저장한다.

저장 위치는 folder + filename이다.

wav 파일 헤더에 채널 수, 샘플 수, 샘플링 속도를 지정한다.

파일 저장이 완료되면 저장 경로를 출력한다.

6. list_audio_files(folder='records')
지정된 폴더 내 .wav 확장자 파일 목록을 리스트로 반환한다.

음성 파일들을 조회하기 위한 유틸리티 함수이다.

7. speech_to_text(audio_filepath)
지정된 오디오 파일을 불러와 텍스트로 변환한다.

speech_recognition 라이브러리의 Google 무료 API를 이용한다.

인식 과정 중 예외가 발생하면 빈 문자열로 처리한다.

변환된 텍스트를 반환한다.

8. save_transcript_to_csv(audio_filepath, transcript_text)
오디오 파일명과 같은 이름을 가진 .csv 파일을 만든다.

WAV 파일 길이라는 ‘시간(초)’ 값과 변환된 텍스트를 CSV 형식으로 저장한다.

CSV 헤더는 ‘Time(Seconds)’, ‘Text’ 두 칼럼으로 구성된다.

저장 완료 후 저장 위치를 출력한다.

9. main() 함수 흐름
저장 폴더를 준비한다.

현재 시각 기반 파일명을 생성한다.

10초 동안 마이크에서 음성을 녹음한다.

녹음 데이터를 wav파일로 저장한다.

‘records’ 폴더 내 모든 wav 파일 목록을 조회한다.

각 파일을 순회하며 STT 변환 후 텍스트와 시간을 CSV 파일로 저장한다.

변환된 텍스트를 출력한다.

