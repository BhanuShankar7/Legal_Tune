# ⚖️ Telegram Legal Assistant Bot

A sophisticated AI-powered Legal Assistant for Telegram, designed to explain laws, analyze legal documents, and provide case insights using **Google Gemini 1.5 Flash**.

> **⚠️ Disclaimer**: This bot provides legal *information*, NOT legal advice. Always consult a licensed attorney.

## 🌟 Key Features

*   **🤖 AI-Powered Legal Intelligence**: Powered by **Google Gemini 1.5 Flash** (via v1 REST API).
*   **🌍 Multilingual Support**: Auto-detects and communicates in English, Hindi, Telugu, Tamil, Urdu, and more.
*   **📄 Document Analysis**:
    *   **PDFs**: Extracts and analyzes text from legal documents.
    *   **Images**: Uses OCR (Tesseract) to read scanned FIRs, court notices, etc.
    *   **Word Docs**: Parses `.docx` files.
*   **⚖️ Case Assistance**: Provides strengths, weaknesses, common arguments, and next steps for specific cases.
*   **🔒 Privacy Focused**: Files are processed in-memory and not stored persistently.

## 🛠️ Tech Stack

*   **Core**: Python 3.9+
*   **Bot Framework**: `python-telegram-bot`
*   **LLM**: Google Gemini API v1 (REST)
*   **OCR & Parsing**: `pytesseract` (Tesseract OCR), `pdfplumber`, `python-docx`

## 🚀 Getting Started

### Prerequisites

*   **Python 3.9+** (Anaconda or standard)
*   **Telegam Bot Token** (from [@BotFather](https://t.me/BotFather))
*   **Google Gemini API Key**
*   **Tesseract OCR** (Required for processing images)
    *   **Windows**: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki).
        *   *Important*: Add Tesseract to your System PATH during installation, or update `app/document_processor.py` to point to the `tesseract.exe` path.

### 1. Project Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd "Legal Tune 0.1"

# Create .env file
echo "GEMINI_API_KEY=your_key" > .env
echo "TELEGRAM_BOT_TOKEN=your_token" >> .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Bot

```bash
python app/bot.py
```

## 🎮 Usage Commands

*   `/start` - Welcome menu & disclaimer.
*   `/law <query>` - Explain a law (e.g., `/law IPC 302`).
*   `/case` - Upload a legal document for analysis.
*   `/language` - Information on language support.
*   `/faq` - Common legal questions.
*   `/privacy` - Privacy policy.

## 📂 Project Structure

```
├── app/
│   ├── bot.py               # Main bot application
│   ├── gemini_client.py     # Gemini REST API Client
│   └── document_processor.py # OCR logic
├── .env                     # API Keys (Keep secure!)
├── config.py                # Configuration loader
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```
"# Legal_Tune" 
