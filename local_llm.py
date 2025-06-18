from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import json
import os
import logging
import multiprocessing
import re
from tamil_chat import TamilChat

logger = logging.getLogger(__name__)

class LocalLLM:
    def __init__(self, model_path: str = "models/llama-2-7b-chat.Q4_K_M.gguf"):
        """Initialize the local LLM system"""
        try:
            # Initialize logger
            self.logger = logging.getLogger(__name__)
            
            # Initialize Tamil chat system
            self.tamil_chat = TamilChat()
            
            # Get number of CPU cores
            cpu_count = multiprocessing.cpu_count()
            # Use 75% of available CPU cores for the LLM
            n_threads = max(1, int(cpu_count * 0.75))
            
            # Initialize the LLaMA model with CPU optimizations
            self.llm = Llama(
                model_path=model_path,
                n_ctx=1024,  # Reduced context window for better CPU performance
                n_threads=n_threads,  # Use optimal number of CPU threads
                n_gpu_layers=0,  # CPU only
                n_batch=512,  # Batch size for better CPU utilization
                verbose=False  # Reduce logging overhead
            )
            
            # Initialize sentence transformer with CPU optimizations
            self.embedder = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device='cpu',
                cache_folder='./model_cache'  # Cache embeddings locally
            )
            
            # Load knowledge base
            self.knowledge_base = self._load_knowledge_base()
            
            # Create document embeddings with progress tracking
            self.logger.info("Preparing document embeddings...")
            self.documents = self._prepare_documents()
            self.embeddings = self.embedder.encode(
                self.documents,
                batch_size=32,  # Smaller batch size for CPU
                show_progress_bar=True
            )
            
            self.logger.info(f"Local LLM system initialized successfully using {n_threads} CPU threads")
            
        except Exception as e:
            self.logger.error(f"Error initializing Local LLM system: {str(e)}")
            raise
    
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
        
        # Load FIR information
        with open('static/data/fir_info.json', 'r', encoding='utf-8') as f:
            knowledge_base['fir_info'] = json.load(f)
        
        # Load response patterns
        with open('static/data/english_responses.json', 'r', encoding='utf-8') as f:
            knowledge_base['english_responses'] = json.load(f)
        
        with open('static/data/tamil_responses.json', 'r', encoding='utf-8') as f:
            knowledge_base['tamil_responses'] = json.load(f)
        
        return knowledge_base
    
    def _prepare_documents(self) -> List[str]:
        """Prepare documents for embedding"""
        documents = []
        
        # Add emergency contacts (English only)
        for contact, number in self.knowledge_base['emergency_contacts']['english'].items():
            documents.append(f"{contact}: {number}")
        
        # Add departments (English only)
        for category, items in self.knowledge_base['departments']['english'].items():
            if isinstance(items, dict):
                for dept, desc in items.items():
                    documents.append(f"{dept}: {desc}")
        
        # Add common queries (English only)
        for category, items in self.knowledge_base['common_queries']['english'].items():
            if isinstance(items, dict):
                for query, answer in items.items():
                    documents.append(f"Q: {query}\nA: {answer}")
        
        # Add kids safety (English only)
        for category, items in self.knowledge_base['kids_safety']['english'].items():
            if isinstance(items, list):
                for item in items:
                    documents.append(item)
        
        # Add response patterns (English only)
        response_data = self.knowledge_base['english_responses']
        if isinstance(response_data, dict) and 'patterns' in response_data:
            for pattern in response_data['patterns']:
                if isinstance(pattern, dict) and 'keywords' in pattern and 'response' in pattern:
                    documents.append(f"Keywords: {', '.join(pattern['keywords'])}\nResponse: {pattern['response']}")
        
        return documents
    
    def _get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Get relevant context for the query using sentence transformers"""
        # Get query embedding
        query_embedding = self.embedder.encode([query])[0]
        
        # Calculate cosine similarities using numpy for better CPU performance
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Combine relevant documents
        context = "\n\n".join([self.documents[i] for i in top_indices])
        return context
    
    def _create_prompt(self, query: str, context: str, language: str) -> str:
        """Create prompt for the LLM"""
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
    
    def is_emergency(self, message: str, language: str) -> bool:
        """Check if the message contains emergency keywords"""
        emergency_keywords = {
            'english': ['emergency', 'help', 'danger', 'threat', 'attack', 'robbery', 'theft', 'assault'],
            'tamil': ['அவசர', 'உதவி', 'ஆபத்து', 'அச்சுறுத்தல்', 'தாக்குதல்', 'கொள்ளை', 'திருட்டு', 'தாக்குதல்']
        }
        return any(keyword in message.lower() for keyword in emergency_keywords[language])

    def get_emergency_response(self, language: str) -> str:
        """Get emergency response based on language"""
        if language == 'tamil':
            return "அவசர உதவிக்கு உடனே 100-ஐ அழையுங்கள். நாங்கள் உங்களுக்கு உதவுவோம்."
        return "EMERGENCY: Please call 100 immediately for police assistance!"

    def get_response(self, message: str, lang: str = 'en') -> str:
        """Get response from the model"""
        try:
            # For Tamil mode, use TamilChat system
            if lang == 'ta':
                return self.tamil_chat.get_response(message)
            
            # For English mode, continue with LLM logic
            message = message.strip()
            
            if message.lower() in ["hello", "hi", "greetings"]:
                return "Hello! I am the Tamil Nadu Police Help Assistant. How can I assist you today?"
            
            # Check for emergency keywords in English
            emergency_keywords = ['emergency', 'help', 'danger', 'threat', 'attack', 'robbery', 'assault']
            if any(keyword in message.lower() for keyword in emergency_keywords):
                return "For emergency help, immediately call 100. We will help you."

            # Get relevant context for English responses
            context = self._get_relevant_context(message)
            
            # Create prompt for English responses
            prompt = f"""You are a Tamil Nadu Police Help Assistant. You must respond in English only. Do not provide Tamil translations.

User Query: {message}

Relevant Information:
{context}

Important Note: You must respond in English only. Do not provide Tamil translations. The response should be in English only.

Response:"""

            # Generate response with stricter parameters
            response = self.llm(
                prompt,
                max_tokens=200,
                stop=["User:", "English:", "Note:", "Translation:", "Solution:", "Answer:", "Response:"],
                temperature=0.1,
                top_p=0.9,
                repeat_penalty=1.2,
                echo=False
            )
            
            # Extract text from response dictionary
            response_text = response['choices'][0]['text'].strip() if isinstance(response, dict) else str(response).strip()
            
            return response_text

        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return "Sorry, unable to generate response at the moment. Please try again." 