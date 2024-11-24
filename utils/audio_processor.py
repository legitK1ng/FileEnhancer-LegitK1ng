import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from sklearn.cluster import DBSCAN

def convert_to_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    wav_path = file_path.rsplit('.', 1)[0] + '.wav'
    audio.export(wav_path, format='wav')
    return wav_path

def transcribe_audio(file_path):
    if not file_path.endswith('.wav'):
        file_path = convert_to_wav(file_path)
        
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
        
    try:
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service: {str(e)}"

def diarize_speakers(file_path):
    if not file_path.endswith('.wav'):
        file_path = convert_to_wav(file_path)
        
    audio = AudioSegment.from_wav(file_path)
    samples = np.array(audio.get_array_of_samples())
    
    # Simple clustering-based diarization
    features = np.array([samples[i:i+1024] for i in range(0, len(samples), 1024)])
    clustering = DBSCAN(eps=0.5, min_samples=5).fit(features)
    
    speakers = {'speaker_' + str(i): [] for i in set(clustering.labels_) if i != -1}
    for i, label in enumerate(clustering.labels_):
        if label != -1:
            speakers['speaker_' + str(label)].append(i * 1024 / audio.frame_rate)
            
    return speakers
