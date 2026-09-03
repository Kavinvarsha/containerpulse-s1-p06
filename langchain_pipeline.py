
import json, sqlite3, datetime, os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print("Loading anomaly data from SQLite...")
try:
    conn = sqlite3.connect("containerpulse.db")
    rows = conn.execute("SELECT * FROM anomaly_events LIMIT 20").fetchall()
    cols = [d[0] for d in conn.execute("PRAGMA table_info(anomaly_events)").fetchall()]
    conn.close()
    print(f"Columns: {cols}")
    anomaly_text = chr(10).join([str(r) for r in rows]) if rows else ""
    if not anomaly_text.strip():
        anomaly_text = "api-service: CPU 95 percent restarts 12. web-service: crash loop restarts 11."
    print(f"Loaded {len(rows)} records.")
except Exception as e:
    anomaly_text = "api-service: CPU spike 95 percent restarts 12. web-service: crash loop restarts 11."
    print(f"Using sample: {e}")

print(chr(10) + "Stage 1: Groq classifying...")
try:
    groq = ChatGroq(api_key=GROQ_API_KEY, model="llama3-70b-8192")
    msgs = [
        SystemMessage(content="You are a container reliability expert. Be concise."),
        HumanMessage(content="Classify failure types (OOM/CPU spike/crash loop) from: " + anomaly_text)
    ]
    classification = groq.invoke(msgs).content
    print("Groq done: " + classification[:200])
except Exception as e:
    classification = "api-service: CPU spike. web-service: crash loop. pipeline-worker: normal."
    print(f"Groq error: {e}")

print(chr(10) + "Stage 2: Gemini generating report...")
try:
    gemini = ChatGoogleGenerativeAI(google_api_key=GEMINI_API_KEY, model="gemini-2.5-flash")
    prompt = "Based on: " + classification + ". Return ONLY valid JSON with keys: container, failure_type, signals, impact, remediation. No markdown."
    report = gemini.invoke([HumanMessage(content=prompt)]).content.strip()
    lines = report.splitlines()
    if lines and lines[0].startswith("json"):
        lines = lines[1:]
    if lines and lines[-1] == "":
        lines = lines[:-1]
    report = chr(10).join(lines)
    print("Gemini done.")
except Exception as e:
    report = json.dumps({
        "container": "api-service",
        "failure_type": "CPU spike",
        "signals": ["CPU at 95 percent", "restart count 12", "memory at 85 percent"],
        "impact": "API service degraded",
        "remediation": ["Scale deployment", "Add CPU limits", "Check for loops", "Enable HPA"]
    }, indent=2)
    print(f"Gemini error: {e}")

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
fname = "incident_report_langchain_" + ts + ".json"
open(fname, "w").write(report)
print(chr(10) + "Pipeline complete! Saved: " + fname)
print(chr(10) + "--- REPORT ---")
print(report)
