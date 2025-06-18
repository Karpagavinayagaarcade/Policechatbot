import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = self.openai_api_key
        
        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer()
        
        # Create document embeddings
        self.documents = self._prepare_documents()
        self.embeddings = self.vectorizer.fit_transform(self.documents)
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load all knowledge base files"""
        knowledge_base = {}
        
        # Load emergency contacts
        with open('static/data/emergency_contacts.json', 'r', encoding='utf-8') as f:
            knowledge_base['emergency_contacts'] = json.load(f)
        
        # Load departments
        with open('static/data/departments.json', 'r', encoding='utf-8') as f:
            knowledge_base['departments'] = json.load(f)
        
        # Load common queries
        with open('static/data/common_queries.json', 'r', encoding='utf-8') as f:
            knowledge_base['common_queries'] = json.load(f)
        
        # Load kids safety
        with open('static/data/kids_safety.json', 'r', encoding='utf-8') as f:
            knowledge_base['kids_safety'] = json.load(f)
        
        # Load response patterns
        with open('static/data/english_responses.json', 'r', encoding='utf-8') as f:
            knowledge_base['english_responses'] = json.load(f)
        
        with open('static/data/tamil_responses.json', 'r', encoding='utf-8') as f:
            knowledge_base['tamil_responses'] = json.load(f)
        
        return knowledge_base
    
    def _prepare_documents(self) -> List[str]:
        """Prepare documents for embedding"""
        documents = []
        
        # Add emergency contacts
        for lang in ['english', 'tamil']:
            for contact, number in self.knowledge_base['emergency_contacts'][lang].items():
                documents.append(f"{contact}: {number}")
        
        # Add departments
        for lang in ['english', 'tamil']:
            for category, items in self.knowledge_base['departments'][lang].items():
                if isinstance(items, dict):
                    for dept, desc in items.items():
                        documents.append(f"{dept}: {desc}")
        
        # Add common queries
        for lang in ['english', 'tamil']:
            for category, items in self.knowledge_base['common_queries'][lang].items():
                if isinstance(items, dict):
                    for query, answer in items.items():
                        documents.append(f"Q: {query}\nA: {answer}")
        
        # Add kids safety
        for lang in ['english', 'tamil']:
            for category, items in self.knowledge_base['kids_safety'][lang].items():
                if isinstance(items, list):
                    for item in items:
                        documents.append(item)
        
        # Add response patterns
        for lang in ['english', 'tamil']:
            for pattern in self.knowledge_base[f'{lang}_responses']['patterns']:
                documents.append(f"Keywords: {', '.join(pattern['keywords'])}\nResponse: {pattern['response']}")
        
        return documents
    
    def _get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Get relevant context for the query"""
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.embeddings)
        
        # Get top k most similar documents
        top_indices = np.argsort(similarities[0])[-top_k:][::-1]
        
        # Combine relevant documents
        context = "\n\n".join([self.documents[i] for i in top_indices])
        return context
    
    def _create_prompt(self, query: str, context: str, language: str) -> str:
        """Create prompt for ChatGPT"""
        if language == 'tamil':
            return f"""You are a helpful Tamil Nadu Police Assistant. Use the following context to answer the user's question in Tamil:

Context:
{context}

User Question: {query}

Please provide a helpful and accurate response in Tamil based on the context. If the context doesn't contain enough information, you can provide general guidance about police procedures."""
        else:
            return f"""You are a helpful Tamil Nadu Police Assistant. Use the following context to answer the user's question:

Context:
{context}

User Question: {query}

Please provide a helpful and accurate response based on the context. If the context doesn't contain enough information, you can provide general guidance about police procedures."""
    
    def get_response(self, query: str, language: str = 'english') -> str:
        """Get response using RAG"""
        try:
            # Check for emergency keywords
            emergency_keywords = {
                'english': ['emergency', 'help', 'danger', 'threat', 'attack', 'robbery', 'theft', 'assault'],
                'tamil': ['அவசர', 'உதவி', 'ஆபத்து', 'அச்சுறுத்தல்', 'தாக்குதல்', 'கொள்ளை', 'திருட்டு', 'தாக்குதல்']
            }
            
            if any(keyword in query.lower() for keyword in emergency_keywords[language]):
                if language == 'tamil':
                    return "அவசர உதவிக்கு உடனே 100-ஐ அழையுங்கள். நாங்கள் உங்களுக்கு உதவுவோம்."
                else:
                    return "EMERGENCY: Please call 100 immediately for police assistance!"
            
            # Get relevant context
            context = self._get_relevant_context(query)
            
            # Create prompt
            prompt = self._create_prompt(query, context, language)
            
            # Get response from ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful Tamil Nadu Police Assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            if language == 'tamil':
                return "மன்னிக்கவும், ஏதோ தவறு ஏற்பட்டுள்ளது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
            else:
                return "I apologize, but something went wrong. Please try again." 