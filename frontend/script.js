/*
 * CyberGuard AI - Frontend Dashboard Controller
 *
 * Connects directly to the real FastAPI backend endpoint: /api/v1/predict
 * Uses structured session-only metrics and privacy-safe memory history.
 */

// Production fallback and local endpoints
const RENDER_API_BASE = "https://cyberguard-ai-6djc.onrender.com/api/v1";
const LOCAL_API_BASE = "http://localhost:8000/api/v1";

// Resolve API base URL based on how the file is served
function getApiBaseUrl() {
  if (window.location.protocol.startsWith("http")) {
    // If served from FastAPI (e.g., localhost:8000 or onrender.com)
    return `${window.location.origin}/api/v1`;
  }
  // If opened directly from disk via file://, default to local, with cloud fallback
  return LOCAL_API_BASE;
}

let API_BASE = getApiBaseUrl();

// DOM Elements
const messageInput = document.getElementById("messageInput");
const analyzeButton = document.getElementById("analyzeButton");
const resultBox = document.getElementById("result");
const systemStatusText = document.getElementById("systemStatusText");
const systemStatusBadge = document.getElementById("systemStatusBadge");

// Session-only metric counters (Critical Instruction 7: real session data, not mocked)
let analyzedCount = 0;
let safeCount = 0;
let flaggedCount = 0;

// Initialize Event Listeners
analyzeButton.addEventListener("click", analyzeMessage);

// Allow Ctrl+Enter or Cmd+Enter to submit message
messageInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    analyzeMessage();
  }
});

// Check backend health on load to update system status
async function checkBackendHealth() {
  try {
    let res = await fetch(`${API_BASE}/health`, { method: "GET" }).catch(() => null);
    if (!res || !res.ok) {
      // If local failed and we are running from file://, switch to Render cloud API
      if (API_BASE.includes("localhost")) {
        API_BASE = RENDER_API_BASE;
        res = await fetch(`${API_BASE}/health`, { method: "GET" }).catch(() => null);
      }
    }

    if (res && res.ok) {
      const data = await res.json();
      const modelLoaded = data.model_loaded ? "Model Ready" : "Fallback Mode";
      systemStatusText.textContent = `System online · ${modelLoaded}`;
      systemStatusBadge.style.borderColor = "#244b43";
    } else {
      systemStatusText.textContent = "Connecting to AI server...";
      systemStatusBadge.style.borderColor = "#493326";
    }
  } catch (err) {
    systemStatusText.textContent = "Offline Mode (Local Fallback)";
  }
}

checkBackendHealth();

/**
 * Sends text to the real backend prediction endpoint (/api/v1/predict)
 */
async function analyzeMessage() {
  const message = messageInput.value.trim();

  // Handle empty input
  if (!message) {
    showResult(
      "Please enter a message first.",
      "neutral",
      "Type or paste a message into the text area above, then press Analyze."
    );
    messageInput.focus();
    return;
  }

  // Loading state
  analyzeButton.disabled = true;
  analyzeButton.innerHTML = "Analyzing… <span>⏳</span>";
  showResult(
    "Contacting AI model…",
    "neutral",
    "CyberGuard AI is vectorizing and scoring the message..."
  );

  try {
    let response;
    try {
      response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message }),
      });
    } catch (netErr) {
      // If localhost was offline, try live Render backend as seamless backup
      if (API_BASE !== RENDER_API_BASE) {
        API_BASE = RENDER_API_BASE;
        response = await fetch(`${API_BASE}/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: message }),
        });
      } else {
        throw netErr;
      }
    }

    if (!response.ok) {
      const errorJson = await response.json().catch(() => ({}));
      const msg = errorJson.error?.message || `Backend returned HTTP ${response.status}`;
      throw new Error(msg);
    }

    const jsonResponse = await response.json();

    // Map exact response shape from FastAPI: {"success": true, "data": {...}}
    const payload = jsonResponse.data || jsonResponse;

    const harmful = Boolean(payload.is_cyberbullying ?? (payload.label === 1));
    const confidenceVal = payload.confidence_percent ?? (typeof payload.confidence === "number" ? payload.confidence * 100 : null);
    const method = payload.method || "TF-IDF + Logistic Regression";
    const category = payload.category && payload.category !== "Not Applicable" ? payload.category : null;

    // Update session metrics
    analyzedCount += 1;
    if (harmful) {
      flaggedCount += 1;
    } else {
      safeCount += 1;
    }

    document.getElementById("totalMessages").textContent = analyzedCount;
    document.getElementById("safeMessages").textContent = safeCount;
    document.getElementById("flaggedMessages").textContent = flaggedCount;

    const confidenceText = confidenceVal !== null
      ? ` Statistical model confidence: ${confidenceVal.toFixed(1)}% (${method}).`
      : ` Powered by ${method}.`;

    // Critical Instruction 8: AI labels phrased as estimates
    if (harmful) {
      let desc = "This automated scan detected potentially harmful language. Review the message and its context carefully." + confidenceText;
      if (category) {
        desc += ` Category: ${category}.`;
      }
      showResult("Potentially harmful language detected", "flagged", desc);
      addHistory(message, "Flagged for review", "flagged");
    } else {
      showResult(
        "Likely non-bullying message",
        "safe",
        "The model classified this message as likely safe. Context and tone still matter." + confidenceText
      );
      addHistory(message, "Likely safe", "safe");
    }
  } catch (error) {
    console.error("CyberGuard analysis error:", error);
    showResult(
      "Could not analyze this message",
      "neutral",
      `Error: ${error.message || "Failed to reach AI server"}. Ensure the backend is running at ${API_BASE}.`
    );
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.innerHTML = 'Analyze message <span>→</span>';
  }
}

/**
 * Updates the Result Card with neutral, safe, or flagged states
 */
function showResult(title, kind, description) {
  resultBox.className = "result" + (kind === "safe" ? " safe" : kind === "flagged" ? " flagged" : "");
  const symbol = kind === "safe" ? "✓" : kind === "flagged" ? "!" : "✧";
  resultBox.replaceChildren();

  const icon = document.createElement("span");
  icon.className = "result-symbol";
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = symbol;

  const content = document.createElement("div");
  const strong = document.createElement("strong");
  strong.textContent = title;
  const p = document.createElement("p");
  p.textContent = description;

  content.append(strong, p);
  resultBox.append(icon, content);
}

/**
 * Appends to in-memory session history (strictly private, no persistent storage)
 */
function addHistory(message, label, kind) {
  const emptyNote = document.getElementById("historyEmpty");
  if (emptyNote) {
    emptyNote.hidden = true;
  }

  const list = document.getElementById("historyList");
  const item = document.createElement("div");
  item.className = "history-item";

  const text = document.createElement("strong");
  text.textContent = message.length > 90 ? message.slice(0, 90) + "…" : message;

  const outcome = document.createElement("em");
  outcome.className = kind;
  outcome.textContent = label;

  item.append(text, outcome);
  list.prepend(item);
}
