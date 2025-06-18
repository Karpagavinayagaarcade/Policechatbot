from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
from dotenv import load_dotenv
import logging
from local_llm import LocalLLM
from tamil_chat import TamilChat
import sys

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Google Maps API key
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    logger.error("Google Maps API key not found in environment variables. Nearby services will not work.")
    GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

# Initialize the local LLM and Tamil chat
try:
    llm = LocalLLM()
    tamil_chat = TamilChat()
    logger.info("Local LLM and Tamil chat initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chat systems: {str(e)}")
    # Initialize with basic functionality if LLM fails
    llm = None
    tamil_chat = TamilChat()
    logger.warning("Initialized with basic functionality (LLM disabled)")

# Load data from JSON files
def load_json_data(filename):
    try:
        with open(f'static/data/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        return {}

# Load data
departments = load_json_data('departments.json')
common_queries = load_json_data('common_queries.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tamil')
def tamil():
    session['lang'] = 'tamil'
    return render_template('chat.html', lang='tamil')

@app.route('/english')
def english():
    session['lang'] = 'english'
    return render_template('chat.html', lang='english')

@app.route('/nearby')
def nearby():
    lang = session.get('lang', 'english')
    if GOOGLE_MAPS_API_KEY == "YOUR_API_KEY_HERE":
        return render_template('error.html', 
                             message="Google Maps API key is not configured. Please contact the administrator.",
                             lang=lang)
    return render_template('nearby.html', lang=lang, google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/chat', methods=['GET', 'POST'])
def chat_page():
    if request.method == 'POST':
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            language = data.get('language', 'english')
            
            if not user_message:
                return jsonify({'error': 'Empty message'}), 400
            
            # Get response based on language
            if language == 'tamil':
                response = tamil_chat.get_response(user_message)
            else:
                if llm is None:
                    response = "I apologize, but the advanced chat functionality is currently unavailable. Please try again later."
                else:
                    response = llm.get_response(user_message, language)
            
            # Log the response for debugging
            logger.info(f"Response for '{user_message}' ({language}): {response}")
            
            return jsonify({
                'response': response,
                'language': language
            })
            
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({
                'error': 'An error occurred while processing your request.',
                'details': str(e)
            }), 500
    
    # For GET requests, redirect to home page
    return redirect(url_for('index'))

@app.route('/departments')
def departments_page():
    lang = session.get('lang', 'english')
    return render_template('departments.html', departments=departments, lang=lang)

@app.route('/common-queries')
def common_queries_page():
    lang = session.get('lang', 'english')
    return render_template('common-queries.html', queries=common_queries[lang], lang=lang)

@app.route('/kids-mode')
def kids_mode():
    lang = session.get('lang', 'english')
    return render_template('kids-mode.html', lang=lang)

@app.route('/emergency')
def emergency():
    lang = session.get('lang', 'english')
    return render_template('emergency-contacts.html', lang=lang)

if __name__ == '__main__':
    try:
        # Disable colorama for Windows
        if sys.platform == 'win32':
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['PYTHONUNBUFFERED'] = '1'
        
        # Run the app without debug mode on Windows
        if sys.platform == 'win32':
            app.run(host='0.0.0.0', port=5000, debug=False)
        else:
            app.run(debug=True)
    except Exception as e:
        logger.error(f"Error starting Flask app: {str(e)}")
        sys.exit(1) 