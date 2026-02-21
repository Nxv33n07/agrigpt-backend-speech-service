# 🎙️ AgriGPT Speech & Translation Microservice

A standalone, high-performance "Intelligence Layer" designed for the AgriGPT ecosystem. This service bridges the gap between regional dialects (Telugu, Hindi) and the English-centric AI Agents, ensuring farmers, students, and researchers get expert agricultural advice in their native language.

## ✨ Core Features

- **Multi-lingual STT**: Direct transcription for English, Hindi (`hi-IN`), and Telugu (`te-IN`).
- **Autonomous Intelligence**: Smart detection logic that chooses the best translation engine (LLM vs Standard) based on query complexity.
- **English Bridge**: Automatic conversion of native speech to English for RAG/MCP backend processing.
- **Agricultural Localization**: Advanced LLM-powered translation that understands technical terms like pests, chemicals, and citrus-specific diseases.
- **Failsafe Reliability**: Automatic 10-second timeouts and silent fallbacks ensure the service never hangs or crashes.
- **Session Persistence**: Supports `chat_id` for tracking voice metrics across user sessions.

## 🏗️ Project Structure
```text
agrigpt-speech-service/
├── app/
│   ├── api/            # Route definitions (FastAPI)
│   ├── core/           # Config (CORS, Pydantic Settings, API Keys)
│   ├── services/       # Business Logic (Speech, Translation, LLM)
│   └── main.py         # Entry point (Factory pattern)
├── requirements.txt    # Python dependencies
├── .env                # Secret keys (Gemini, Google)
└── .gitignore          # Git exclusion rules
```

## 🚀 Setup & Launch

### 1. System Dependency (Required)
The service uses **FFmpeg** to handle browser audio formats (WebM/OGG).
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Environment Configuration
Create a `.env` file in the root. The service supports both key names:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Execution
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```
The service will be active at: `http://localhost:8001`

---

## 🔌 API Documentation for Frontend Team

### **1. [POST] /transcribe**
Converts speech to both native language and English.
- **Payload (Form Data)**:
  - `file`: Audio blob from recorder.
  - `lang`: `'en'`, `'hi'`, or `'te'`.
  - `chat_id`: (Optional) Current session ID.
  - `use_llm`: (Optional) `true` to force LLM, `false` to force Standard, `null` (default) for Autonomous mode.
- **Response**:
  ```json
  {
    "native_text": "పంటలకు ఏ ఎరుపువేయ్యాలి?",
    "english_text": "Which fertilizer should I use for crops?",
    "language": "te",
    "llm_used": true
  }
  ```

### **2. [POST] /translate**
Translates English AI responses back to the user's script.
- **Payload (JSON)**:
  ```json
  {
    "text": "AI generated response in English...",
    "target_lang": "te",
    "source_lang": "en",
    "use_llm": null 
  }
  ```
- **Response**:
  ```json
  { 
    "translated_text": "తెలుగు అనువాదం...",
    "llm_used": true 
  }
  ```

### **3. [GET] /health**
Verifies service status and connectivity.

---

## 🧠 Autonomous Engine Logic
The service doesn't just translate; it thinks.
- **Simple Phrases**: "Hello", "Thanks", etc. → Uses **Google Translate** (Fast & Free).
- **Contextual Queries**: "Why are my leaves yellow?" → Uses **Gemini 2.0 Flash** (Expert Accuracy).
- **Error Handling**: If an LLM call takes > 10s or fails, the system instantly switches to the standard engine to prevent user wait times.

---

## 👥 Developers
This service is designed to be a standalone module. Integration is as simple as switching the `SPEECH_API_URL` in your frontend `.env`.
