import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TamilGPT2Chatbot:
    def __init__(self):
        try:
            # Use the AI4Bharat Tamil GPT-2 model
            model_name = "ai4bharat/IndicGPT2-Tamil"
            logger.info(f"Loading model from {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.to('cuda')
                logger.info("Model moved to GPU")
            else:
                logger.info("Using CPU for model inference")
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise

    def generate_response(self, prompt, max_length=100):
        try:
            # Tokenize the input
            inputs = self.tokenizer.encode(prompt, return_tensors='pt')
            
            # Move inputs to the same device as the model
            if torch.cuda.is_available():
                inputs = inputs.to('cuda')
            
            # Generate response
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode and return the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "மன்னிக்கவும், பதில் உருவாக்குவதில் பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."

    def get_emergency_contacts(self):
        return {
            "அவசர உதவி": "100",
            "குழந்தைகள் உதவி": "1098",
            "போக்குவரத்து காவல்துறை": "103",
            "கைப்பற்றல்": "100",
            "தீயணைப்பு": "101"
        }

    def get_department_info(self):
        return {
            "குற்றவியல் பிரிவு": "044-23452345",
            "போக்குவரத்து பிரிவு": "044-23452346",
            "கணினி குற்றங்கள் பிரிவு": "044-23452347",
            "பெண்கள் பாதுகாப்பு பிரிவு": "044-23452348",
            "குழந்தைகள் பாதுகாப்பு பிரிவு": "044-23452349"
        }

    def get_common_queries(self):
        return {
            "காவல்நிலையம் கிடைக்கும்": "அருகிலுள்ள காவல்நிலையத்தை கண்டுபிடிக்க",
            "கைப்பற்றல் செய்தல்": "கைப்பற்றல் செய்வதற்கான வழிமுறைகள்",
            "போக்குவரத்து சான்று": "போக்குவரத்து சான்று பெறுவதற்கான வழிமுறைகள்",
            "காவல்துறை சான்று": "காவல்துறை சான்று பெறுவதற்கான வழிமுறைகள்"
        } 