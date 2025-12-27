import os
import requests
import numpy as np
from pymongo import MongoClient
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'finance_db'
COLLECTION_NAME = 'boletos'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Telegram credentials not found in .env")

def send_telegram_message(message, file_path=None):
    """Sends a message and optionally a PDF file to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        # Send text
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Telegram message sent.")
        
        # Send File if exists
        if file_path and os.path.exists(file_path):
            url_doc = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': TELEGRAM_CHAT_ID}
                resp_doc = requests.post(url_doc, data=data, files=files)
                resp_doc.raise_for_status()
            print(f"File sent: {file_path}")
        elif file_path:
             print(f"File not found: {file_path}")

    except Exception as e:
        print(f"Error sending Telegram: {e}")

def get_business_days_until(target_date_str):
    """Calculates business days from today until target date."""
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        today = date.today()
        
        if target_date < today:
            return -1 # Already passed
            
        # busday_count returns the number of business days between begindate and enddate
        # weekmask='1111100' means Mon-Fri are business days
        days = np.busday_count(today, target_date, weekmask='1111100')
        return int(days)
    except Exception as e:
        print(f"Date error: {e}")
        return None

def main():
    print(f"Checking deadlines on {date.today()}...")
    
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Check all boletos (in production, filter by status != PAID)
    # Finding boletos with due_date
    boletos = collection.find({"due_date": {"$exists": True}})
    
    count_notified = 0
    
    for boleto in boletos:
        due_date_str = boleto.get('due_date')
        if not due_date_str:
            continue
            
        days_left = get_business_days_until(due_date_str)
        
        # Logic: Notify if exactly 2 business days left
        # And check if we haven't notified yet for this event
        if days_left == 2 and not boleto.get('notification_sent_2_days'):
            print(f"Boleto due in 2 days: {boleto.get('beneficiary_name')}")
            
            msg = (
                f"🚨 **ATENÇÃO: Boleto Vencendo!** 🚨\n\n"
                f"Beneficiário: {boleto.get('beneficiary_name')}\n"
                f"Vencimento: {due_date_str} (daqui a 2 dias úteis)\n"
                f"Valor: R$ {boleto.get('document_value'):.2f}\n"
                f"Código de Barras: {boleto.get('barcode')}\n\n"
                f"Segue o boleto em anexo para pagamento."
            )
            
            file_path = boleto.get('file_path')
            send_telegram_message(msg, file_path)
            
            # Mark as notified to avoid spamming if script runs again same day
            collection.update_one(
                {"_id": boleto["_id"]},
                {"$set": {"notification_sent_2_days": True}}
            )
            
            count_notified += 1
            
    print(f"Check finished. {count_notified} notifications sent.")

if __name__ == "__main__":
    main()
