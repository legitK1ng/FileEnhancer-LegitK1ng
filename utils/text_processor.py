import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # Fallback to small pipeline if model is not available
    nlp = spacy.blank('en')

def analyze_sentiment(text):
    try:
        return sia.polarity_scores(text)
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return {
            'neg': 0,
            'neu': 0,
            'pos': 0,
            'compound': 0
        }

def extract_entities(text):
    try:
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        return entities
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return []
