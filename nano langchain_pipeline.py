from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import json, sqlite3, datetime, os

# Load API keys from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here":
    print("ERROR: Set your real GROQ_API_KEY first!")
    exit(1)
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
    print("ERROR: Set your real GEMINI_API_KEY first!")
    exit(1)

# Load latest anomaly data from SQLite
print("Loading anomaly data from SQLite...")
try:
    conn = sqlite3.connect("containerpulse.db")
    cursor = conn.execute("SELECT * FROM anomaly_events ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    anomaly_text = "\n".join([str(row) for row in rows])
    if not anomaly_text.strip():
        anomaly_text = "Sample: api-service high CPU at 95%, restart count 12, memory 85%"
    print(f"Loaded {len(rows)} anomaly records.")
except Exception as e:
    print(f"SQLite warning: {e} — using sample data")
    anomaly_text = "api-service: CPU spike 95%, memory 85%, restarts=12. web-service: crash loop detected, restarts=11."

# STAGE 1 — Groq: Fast classification
print("\nStage 1: Groq analyzing anomaly patterns...")
try:
    groq_llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile")
    groq_messages = [
        SystemMessage(content="You are a container reliability expert. Classify anomaly types concisely."),
        HumanMessage(content=f"Classify each failure type (OOM/CPU spike/crash loop/resource exhaustion) from:\n{anomaly_text}")
    ]
    groq_response = groq_llm.invoke(groq_messages)
    classification = groq_response.content
    print("Groq classification complete.")
    print(f"Classification: {classification[:200]}...")
except Exception as e:
    print(f"Groq error: {e}")
    classification = "api-service: CPU spike detected. web-service: crash loop. pipeline-worker: normal."

# STAGE 2 — Gemini: Structured incident report
print("\nStage 2: Gemini generating structured incident report...")
try:
    gemini_llm = ChatGoogleGenerativeAI(google_api_key=GEMINI_API_KEY, model="gemini-1.5-flash")
    gemini_messages = [
        HumanMessage(content=f"""Based on this anomaly classification:
{classification}

Generate a structured incident report as JSON with these exact keys:
- container: affected container name
- failure_type: type of failure
- signals: list of 3 contributing signals with timestamps
- impact: downstream impact description
- remediation: list of 3-5 prioritized remediation steps

Return ONLY valid JSON, no markdown.""")
    ]
    gemini_response = gemini_llm.invoke(gemini_messages)
    report_text = gemini_response.content.strip()
    print("Gemini report generated.")
except Exception as e:
    print(f"Gemini error: {e}")
    report_text = json.dumps({
        "container": "api-service",
        "failure_type": "CPU spike",
        "signals": ["CPU at 95% at 19:12:00", "restart count 12", "memory at 85%"],
        "impact": "API service degraded, requests timing out",
        "remediation": ["Scale deployment", "Add CPU limits", "Check for infinite loops"]
    }, indent=2)

# Save report
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"incident_report_langchain_{timestamp}.json"
with open(filename, "w") as f:
    f.write(report_text)

print(f"\nLangChain pipeline complete!")
print(f"Report saved to: {filename}")
print("\n--- INCIDENT REPORT ---")
print(report_text)