import os
from docx import Document
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

class DocumentProcessor:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.creds = None
        self.service = None

    def read_word_document(self, file_path):
        """Read content from a Word document."""
        try:
            doc = Document(file_path)
            content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            return '\n'.join(content)
        except Exception as e:
            print(f"Error reading Word document: {str(e)}")
            return None

    def read_excel_file(self, file_path, sheet_name=None):
        """Read content from an Excel file."""
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path, sheet_name=0)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
            return None

    def setup_google_sheets(self, credentials_path):
        """Set up Google Sheets API credentials."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('sheets', 'v4', credentials=self.creds)

    def read_google_sheet(self, spreadsheet_id, range_name):
        """Read content from a Google Sheet."""
        try:
            if not self.service:
                raise Exception("Google Sheets service not initialized. Call setup_google_sheets first.")
            
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None
            
            # Convert to pandas DataFrame for consistent format
            df = pd.DataFrame(values[1:], columns=values[0])
            return df.to_dict('records')
        except Exception as e:
            print(f"Error reading Google Sheet: {str(e)}")
            return None

    def process_document(self, file_path, doc_type='word'):
        """Process a document based on its type."""
        if doc_type == 'word':
            return self.read_word_document(file_path)
        elif doc_type == 'excel':
            return self.read_excel_file(file_path)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    def update_knowledge_base(self, data, knowledge_base):
        """Update the chatbot's knowledge base with new information."""
        if isinstance(data, str):
            # Handle text content
            knowledge_base['general_info'].update({
                'text_content': data
            })
        elif isinstance(data, list):
            # Handle structured data (Excel/Google Sheets)
            for item in data:
                if 'category' in item and 'content' in item:
                    category = item['category']
                    if category not in knowledge_base:
                        knowledge_base[category] = {}
                    knowledge_base[category].update({
                        item.get('key', 'content'): item['content']
                    })
        return knowledge_base 