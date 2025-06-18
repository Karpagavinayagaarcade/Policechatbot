# 🚔 Tamil Nadu Police Assistant

A **bilingual web application** designed to assist users with police-related queries in **English 🇬🇧** and **Tamil 🇮🇳**.

---

## ✨ Features

- 🌐 Bilingual support (English & Tamil)  
- 📍 Nearby emergency services locator  
- 🏢 Department details & directory  
- ❓ Assistance with common police-related queries  
- 🧒 Kids Mode for child safety education  
- 📞 Emergency contact shortcuts  
- 🗺️ Location-based services and awareness  

---

## 🧰 Prerequisites

Ensure you have the following installed:

- 🐍 Python 3.8+  
- 📦 `pip` – Python package installer  
- 🔑 Google Maps API Key  

---

## Installation

1️⃣ Clone the repository:
```bash
git clone https://github.com/UMAYAL-N/CopBot.git
cd tamil-nadu-police-assistant
```

2️⃣ Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```

4️⃣ Create a `.env` file in the project root and add your configuration:
```
FLASK_SECRET_KEY=your_secret_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

## ▶️ Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
🌐http://localhost:5000
```

## Project Structure

```
📁 CopBot
├── app.py                 # Main application file
├── local_llm.py           # Local language model implementation
├── tamil_chat.py          # Tamil chat functionality
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JS, images)
│   └── data/              # JSON data files
└── templates/             # HTML templates
```

## 🤝Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏Acknowledgments

- 👮Tamil Nadu Police Department
- 🧠AI4Bharat for language models
- 🗺️Google Maps Platform

## 📬 Contact

For any queries or support, please contact:

Github: https://github.com/UMAYAL-N
📧 Email: numayalnatarajan@gmail.com
Base : India 
