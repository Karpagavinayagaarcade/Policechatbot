import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import codecs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TamilChat:
    def __init__(self):
        """Initialize Tamil chat system"""
        try:
            # Load knowledge base
            self.knowledge_base = self._load_knowledge_base()
            
            # Initialize NLTK components
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('wordnet')
            
            # Define common Tamil patterns
            self.patterns = {
                'case_registration': [
                    'வழக்கு', 'பதிவு', 'செய்வது', 'எப்படி',
                    'வழக்குப் பதிவு', 'வழக்கு பதிவு', 'வழக்கு பதிவு செய்வது',
                    'வழக்குப் பதிவு செய்வது எப்படி'
                ],
                'emergency': [
                    'அவசர', 'உதவி', 'ஆபத்து', 'அச்சுறுத்தல்',
                    'தாக்குதல்', 'கொள்ளை', 'திருட்டு'
                ]
            }
            
            logger.info("Tamil chat system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Tamil chat system: {str(e)}")
            raise

    def _load_knowledge_base(self):
        """Load Tamil knowledge base"""
        try:
            with open('static/data/tamil_responses.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading Tamil knowledge base: {str(e)}")
            return {}

    def _check_patterns(self, message: str) -> str:
        """Check if message matches any predefined patterns"""
        message = message.lower().strip()
        
        # Check for case registration patterns
        if any(pattern in message for pattern in self.patterns['case_registration']):
            return "வழக்குப் பதிவு செய்ய, உங்கள் அருகிலுள்ள காவல் நிலையத்திற்கு செல்லவும். உங்கள் அடையாள சான்று, நிகழ்வு தொடர்பான ஆவணங்கள் மற்றும் சாட்சிகளின் விவரங்களை கொண்டு வாருங்கள். காவல்துறை அதிகாரி உங்கள் புகாரை பதிவு செய்து FIR எண் வழங்குவார்."
        
        # Check for emergency patterns
        if any(pattern in message for pattern in self.patterns['emergency']):
            return "அவசர உதவிக்கு உடனே 100-ஐ அழையுங்கள். நாங்கள் உங்களுக்கு உதவுவோம்."
        
        return None

    def get_response(self, message: str) -> str:
        """Get response for Tamil query"""
        try:
            # Clean the input message
            message = message.strip()
            
            # First check for pattern matches
            pattern_response = self._check_patterns(message)
            if pattern_response:
                return pattern_response
            
            # Check for exact matches in knowledge base
            if message in self.knowledge_base.get('common_queries', {}):
                return self.knowledge_base['common_queries'][message]
            
            # Try to find similar queries
            message_words = set(word_tokenize(message.lower()))
            best_match = None
            best_score = 0
            
            for query in self.knowledge_base.get('common_queries', {}).keys():
                query_words = set(word_tokenize(query.lower()))
                # Calculate Jaccard similarity
                intersection = len(message_words.intersection(query_words))
                union = len(message_words.union(query_words))
                if union > 0:
                    score = intersection / union
                    if score > 0.2:  # Lower threshold for better matching
                        if score > best_score:
                            best_score = score
                            best_match = query
            
            if best_match:
                return self.knowledge_base['common_queries'][best_match]
            
            # Default response for unknown queries
            return "மன்னிக்கவும், உங்கள் கேள்விக்கு தமிழில் பதில் அளிக்க முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும் அல்லது வேறு விதமாக கேள்வியை கேட்கவும்."
            
        except Exception as e:
            logger.error(f"Error in Tamil chat: {str(e)}")
            return "மன்னிக்கவும், தற்போது பதில் அளிக்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்." 