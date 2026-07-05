
import json
import os
import time
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_reports():
    with open("anomaly_report.json") as f:
        anomaly = json.load(f)
    with open("lstm_forecast.json") as f:
        forecast = json.load(f)
    return anomaly, forecast

def analyze_with_groq(anomaly_data):
    summary_text = ""
    for c in anomaly_data["results"]:
        summary_text += f"Container: {c['container']}, Anomalies: {c['anomaly_count']}/{c['total_records']} ({c['anomaly_percentage']}%)\n"

    prompt = f"""
You are a Kubernetes container health expert. Analyze this anomaly detection report:

{summary_text}

Provide:
1. Which containers are most at risk
2. What the anomaly pattern likely means
3. Recommended immediate actions
Keep it concise and technical.
"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

def generate_incident_report_with_gemini(anomaly_data, forecast_data, groq_analysis):
    forecast_summary = ""
    for name, data in forecast_data["forecasts"].items():
        trend = "RISING" if data["forecast"][-1] > data["last_value"] else "STABLE"
        forecast_summary += f"{name}: current={data['last_value']:.4f}, trend={trend}\n"

    prompt = f"""
You are an SRE engineer. Generate a professional incident report based on:

ANOMALY ANALYSIS:
{groq_analysis}

CPU FORECAST TRENDS:
{forecast_summary}

Write a structured report with:
- Executive Summary (2 sentences)
- Affected Containers
- Risk Level (Critical/High/Medium/Low)
- Root Cause Analysis
- Recommended Actions
Be concise and professional.
"""
    # Try models in order until one works
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-8b",
        "gemini-2.0-flash-lite",
    ]

    for model_name in models_to_try:
        try:
            print(f"    Trying model: {model_name}...")
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            print(f"    ✅ Success with {model_name}")
            return response.text
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print(f"    ⚠️  {model_name} quota exceeded, trying next...")
                time.sleep(3)
                continue
            else:
                raise e

    # If all Gemini models fail, use Groq for the full report too
    print("    ⚠️  All Gemini models quota exceeded — using Groq for full report")
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def main():
    print("🤖 Loading anomaly and forecast data...\n")
    anomaly_data, forecast_data = load_reports()

    print("🦙 Step 1: Analyzing with Groq (Llama 3.3 70B)...")
    groq_analysis = analyze_with_groq(anomaly_data)
    print("\nGroq Analysis:")
    print("-" * 50)
    print(groq_analysis)

    print("\n✨ Step 2: Generating incident report with Gemini...")
    incident_report = generate_incident_report_with_gemini(
        anomaly_data, forecast_data, groq_analysis
    )
    print("\n" + "=" * 60)
    print("INCIDENT REPORT")
    print("=" * 60)
    print(incident_report)

    # Save everything
    full_report = {
        "groq_analysis": groq_analysis,
        "incident_report": incident_report,
        "generated_at": anomaly_data["generated_at"]
    }
    with open("incident_report.json", "w") as f:
        json.dump(full_report, f, indent=2)

    with open("incident_report.txt", "w") as f:
        f.write("=== GROQ ANALYSIS ===\n")
        f.write(groq_analysis)
        f.write("\n\n=== INCIDENT REPORT ===\n")
        f.write(incident_report)

    print("\n✅ Saved to: incident_report.json and incident_report.txt")

if __name__ == "__main__":
    main()
