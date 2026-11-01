# 🛡️ CyberGuard AI — Cyberbullying Detection System

An AI-powered Cyberbullying and Toxicity Detection platform developed for a Class 12 Computer Science / AI project. CyberGuard AI features a client-server architecture with an offline Scikit-Learn Machine Learning pipeline (TF-IDF Vectorizer + Logistic Regression, achieving **93.55% accuracy**), a **FastAPI** backend, an interactive **Streamlit** dashboard, and a modern **Dark Navy, Blue & Purple** responsive web dashboard.

---

## 🎨 Dashboard Design System

The frontend matches a modern cybersecurity theme:
- **Background:** Dark Navy (`#0b1020`)
- **Surface Cards:** Dark Blue (`#121d35`)
- **Card Borders:** Subtle Slate (`#263653`)
- **Buttons:** Electric Blue & Purple gradient (`linear-gradient(110deg, #3868e8, #7659ed)`)
- **Sidebar:** Collapsible navigation with clean 3-line hamburger menu (`☰`)
- **Three Metric Cards:** Real session-based counts (`Messages analyzed`, `Likely safe`, `Flagged for review`)
- **Detection Activity:** Weekly bar chart overview (marked as demo/illustrative)
- **Quick Text Analysis:** Real-time AI prediction panel with accessible labels, keyboard support (`Ctrl + Enter`), loading indicators, and context-aware estimated labels (`"Potentially harmful language detected"` vs `"Likely non-bullying message"`)
- **Safety Hub:** Online safety guidance and privacy-safe in-memory session history

---

## 🚀 How to Run the Application

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed, then install required packages:
```bash
# Install frontend packages (Streamlit, Plotly, Pandas, etc.)
pip install -r requirements.txt

# Install backend packages (FastAPI, Uvicorn, Scikit-Learn, etc.)
pip install -r backend/requirements.txt
```

### 2. Running the FastAPI Backend
Start the backend server on port 8000:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Built-in Web Dashboard:** [http://localhost:8000/dashboard](http://localhost:8000/dashboard)

### 3. Running the Streamlit App
Open a separate terminal window at the project root and run:
```bash
streamlit run app.py
```
Streamlit will automatically open the dashboard at [http://localhost:8501](http://localhost:8501).

### 4. Running the Standalone HTML/CSS/JS Dashboard
You can directly open `frontend/index.html` in any web browser, or access it via `http://localhost:8000/` when the FastAPI server is running. It connects automatically to `/api/v1/predict` (with automatic fallback to the live cloud backend on Render).

---

## 🔌 API Route & Response Schema

### `POST /api/v1/predict`
Analyzes input text for cyberbullying, threats, insults, and hate speech.

#### Request Schema:
```json
{
  "text": "Your message here"
}
```

#### Response Schema:
```json
{
  "success": true,
  "data": {
    "label": 1,
    "is_cyberbullying": true,
    "prediction": "Cyberbullying",
    "confidence": 0.88,
    "confidence_percent": 88.0,
    "matched_words": ["idiot", "loser"],
    "method": "TF-IDF + Logistic Regression",
    "category": "Insult / Name-calling",
    "severity": "Medium",
    "disclaimer": "This confidence score is a statistical estimate from a machine learning model, not a guarantee."
  }
}
```

---

## 🔒 Privacy & Safety Features
1. **Session-Only History:** Real user messages are not logged or stored permanently; analysis history is kept strictly in-memory during the active browser session.
2. **Estimated Labels:** AI predictions are explicitly phrased as probabilistic estimates (`"Potentially harmful language detected"` or `"Likely non-bullying message"`), reminding users that context matters.
3. **Unicode NFKC Normalization:** Sanitizes incoming text against homoglyph spoofing and full-width bypass characters.
4. **Offline Resilience:** Both `api_client.py` and `script.js` feature automatic fallback mechanisms to ensure the application never crashes during live demonstrations.

---

## 🧪 Testing & Verification
Run the backend test suite:
```bash
cd backend
python -m pytest
```
Result: **20 / 20 tests passing**.
