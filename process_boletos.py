import os
import shutil
import json
import PyPDF2
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, Field
from typing import Optional

# Load environment variables
load_dotenv()

# Configuration
INPUT_FOLDER = 'input_boletos'
PROCESSED_FOLDER = 'processed_boletos'
ERROR_FOLDER = 'error_boletos'
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'finance_db'
COLLECTION_NAME = 'boletos'

# Initialize Deepseek client
API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file")
BASE_URL = "https://api.deepseek.com"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# --- Pydantic Data Model ---
class BoletoData(BaseModel):
    beneficiary_name: str
    due_date: str = Field(description="Format YYYY-MM-DD")
    document_value: float = Field(gt=0, description="Value must be positive")
    barcode: Optional[str] = None

def extract_text_from_pdf(filepath):
    """Extracts text from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")
    return text

def extract_info_with_deepseek(text):
    """Uses Deepseek API to extract structured data from raw text."""
    prompt = f"""
    Extract the following information from the boleto text below.
    Return ONLY a JSON object compatible with this schema:
    - beneficiary_name (string)
    - due_date (string, format YYYY-MM-DD)
    - document_value (number)
    - barcode (string, optional)

    Text:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts data from documents and outputs pure JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        content = response.choices[0].message.content
        data_dict = json.loads(content)
        
        # Validation using Pydantic
        boleto = BoletoData(**data_dict)
        return boleto.model_dump()
        
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid JSON")
    except ValidationError as e:
        raise ValueError(f"Data validation failed: {e}")
    except Exception as e:
        raise ValueError(f"AI Extraction error: {e}")

def save_to_mongodb(data):
    """Saves the extracted data to MongoDB."""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        result = collection.insert_one(data)
        print(f"Saved to MongoDB with ID: {result.inserted_id}")
        return True
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        return False

def move_file(filepath, dest_folder):
    """Moves a file to a destination folder, creating it if needed."""
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(filepath)
    destination = os.path.join(dest_folder, filename)
    shutil.move(filepath, destination)
    print(f"Moved {filename} to {dest_folder}")

def main():
    # Ensure standard directories exist
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(ERROR_FOLDER, exist_ok=True)

    print(f"Monitoring {INPUT_FOLDER} for PDFs...")

    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    
    if not files:
        print("No PDF files found in input folder.")
        return

    for filename in files:
        filepath = os.path.join(INPUT_FOLDER, filename)
        print(f"Processing {filename}...")

        try:
            # 1. Extract Text
            text = extract_text_from_pdf(filepath)
            if not text:
                raise ValueError("No text extracted from PDF")

            # 2. AI Extraction & Validation
            print("Sending to AI for extraction...")
            data = extract_info_with_deepseek(text)
            
            # Add metadata
            data['original_filename'] = filename
            
            # Predict destination path
            destination = os.path.join(PROCESSED_FOLDER, filename)
            # Use absolute path for safety
            data['file_path'] = os.path.abspath(destination)

            print(f"Extracted & Validated: {data}")

            # 3. Save to DB
            if save_to_mongodb(data):
                # 4. Move to Success Folder
                move_file(filepath, PROCESSED_FOLDER)
            else:
                raise ValueError("Database save failed")

        except Exception as e:
            print(f"FAILED processing {filename}: {e}")
            move_file(filepath, ERROR_FOLDER)

if __name__ == "__main__":
    main()
