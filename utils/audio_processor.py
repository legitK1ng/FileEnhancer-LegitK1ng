import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from sklearn.cluster import DBSCAN
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessingError(Exception):
    """Custom exception for audio processing errors"""
    pass

def convert_to_wav(file_path):
    """Convert audio file to WAV format"""
    try:
        if not os.path.exists(file_path):
            raise AudioProcessingError(f"File not found: {file_path}")
            
        audio = AudioSegment.from_file(file_path)
        wav_path = file_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_path, format='wav')
        return wav_path
    except Exception as e:
        logger.error(f"Error converting audio file: {str(e)}")
        raise AudioProcessingError(f"Failed to convert audio file: {str(e)}")

def transcribe_audio(file_path):
    """Transcribe audio file to text"""
    try:
        if not os.path.exists(file_path):
            raise AudioProcessingError(f"File not found: {file_path}")
            
        if not file_path.endswith('.wav'):
            file_path = convert_to_wav(file_path)
            
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            
        try:
            transcript = recognizer.recognize_google(audio)
            if not transcript:
                raise AudioProcessingError("No speech detected in audio")
            return transcript
        except sr.UnknownValueError:
            raise AudioProcessingError("Speech recognition could not understand the audio")
        except sr.RequestError as e:
            raise AudioProcessingError(f"Speech recognition service error: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise AudioProcessingError(f"Failed to transcribe audio: {str(e)}")

def diarize_speakers(file_path):
    """Identify different speakers in audio file"""
    try:
        if not os.path.exists(file_path):
            raise AudioProcessingError(f"File not found: {file_path}")
            
        if not file_path.endswith('.wav'):
            file_path = convert_to_wav(file_path)
            
        audio = AudioSegment.from_wav(file_path)
        samples = np.array(audio.get_array_of_samples())
        
        if len(samples) < 1024:
            raise AudioProcessingError("Audio file too short for speaker diarization")
            
        # Simple clustering-based diarization
        features = np.array([samples[i:i+1024] for i in range(0, len(samples), 1024)])
        clustering = DBSCAN(eps=0.5, min_samples=5).fit(features)
        
        # Validate clustering results
        unique_labels = set(clustering.labels_)
        if len(unique_labels) <= 1:
            logger.warning("Could not identify distinct speakers")
            return {'speaker_1': [0]}
            
        speakers = {'speaker_' + str(i): [] for i in unique_labels if i != -1}
        for i, label in enumerate(clustering.labels_):
            if label != -1:
                speakers['speaker_' + str(label)].append(i * 1024 / audio.frame_rate)
                
        return speakers
        
    except Exception as e:
        logger.error(f"Error in speaker diarization: {str(e)}")
        raise AudioProcessingError(f"Failed to identify speakers: {str(e)}")
