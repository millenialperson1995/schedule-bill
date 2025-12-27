# Boleto Automation

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**
    *   Open the `.env` file.
    *   Replace `YOUR_DEEPSEEK_API_KEY_HERE` with your actual API Key.
    *   Ensure your MongoDB is running (default: `mongodb://localhost:27017/`).

## How to Run

1.  **Add Files**
    *   Place your PDF boleto files into the `input_boletos` folder.

2.  **Run the Script**
    ```bash
    python process_boletos.py
    ```

3.  **Results**
    *   The script will read the PDFs, extract data using AI, and save it to MongoDB.
    *   Processed files are moved to the `processed_boletos` folder.
    *   Check your MongoDB database `finance_db`, collection `boletos` for the data.
