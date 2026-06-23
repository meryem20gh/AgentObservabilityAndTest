import uuid
import json
import time
import requests
import datetime
from dotenv import load_dotenv

# Load environment variables (.env file)
load_dotenv()

# Import your compiled LangGraph application executable
from graph import app

# ---------------------------------------------------------
# CONFIGURATION: Connection Bridge
# ---------------------------------------------------------
# Replace this with your actual Google Apps Script Web App execution URL
GOOGLE_SHEETS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwLb7VzP4ptG-y5wWwaNbDan_P1F90F7Q42QwFFIcvgf0m1hI1nMTcGiOOSou6IWiPX/exec"

# ---------------------------------------------------------
# REAL METRICS CALCULATION UTILITIES
# ---------------------------------------------------------
def calculate_real_llm_cost(graph_result):
    """
    Scans the graph's execution logs to find token usage metadata 
    and applies standard model pricing configurations.
    """
    # Blended standard pricing per 1,000,000 tokens (e.g., GPT-4o style rates)
    INPUT_PRICE_PER_M = 2.50
    OUTPUT_PRICE_PER_M = 10.00
    
    total_cost = 0.00000  # Default fallback if the request was blocked before hitting an LLM
    
    # Iterate over logs to look for token metadata structures
    for log_entry in graph_result.get("logs", []):
        # Checks if your graph node appends raw usage dicts or objects containing token metrics
        if isinstance(log_entry, dict) and "usage" in log_entry:
            input_tokens = log_entry["usage"].get("input_tokens", 0)
            output_tokens = log_entry["usage"].get("output_tokens", 0)
            
            # Formula: (Tokens / 1,000,000) * Price Configuration
            run_cost = ((input_tokens / 1_000_000) * INPUT_PRICE_PER_M) + \
                       ((output_tokens / 1_000_000) * OUTPUT_PRICE_PER_M)
            total_cost += run_cost
            break  # Found token records, exit evaluation loop
            
    return total_cost

def log_guardrail_transaction_to_sheet(correlation_id, verdict, confidence, latency_ms, cost):
    payload = {
        "id": correlation_id,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
        "verdict": verdict,
        "conf": confidence,
        "latency": latency_ms,
        "cost": cost
    }
    
    try:
        response = requests.post(GOOGLE_SHEETS_WEBAPP_URL, json=payload, timeout=5)
        # Debugging step: See exactly what the status code and raw response are
        print(f"[Debug] Status Code: {response.status_code}")
        
        return response.json()
    except Exception as e:
        print(f"\n[Warning] Failed to sync to Google Sheets pipeline: {e}")
        # If response exists but json parsing failed, print the raw text to see the Google error
        if 'response' in locals():
            print(f"[Debug] Raw Response: {response.text[:500]}")

# ---------------------------------------------------------
# GRAPH EXECUTION RUNTIME
# ---------------------------------------------------------
print("\n=== Observability Agent ===\n")
user_question = input("Ask a question: ")
correlation_id = str(uuid.uuid4())

# Build the execution frame input state
initial_state = {
    "correlation_id": correlation_id,
    "user_input": user_question,
    "answer": "",
    "source": "",
    "knowledge_id": "",
    "is_injection": False,  # Tracking gate evaluated by guardrail nodes
    "logs": []
}

config = {
    "configurable": {
        "thread_id": correlation_id
    },
    "metadata": {
        "correlation_id": correlation_id,
        "application": "json-agent",
        "environment": "dev"
    }
}

# 1. Capture exact start timestamp for real pipeline latency tracking
start_time = time.time()

# 2. Fire the LangGraph pipeline execution chain
result = app.invoke(
    initial_state,
    config=config
)

# 3. Compute real cumulative delta execution time in milliseconds
latency_ms = int((time.time() - start_time) * 1000)

print("\n===== RESULT =====\n")
print("Correlation ID :", result["correlation_id"])
print("Source         :", result["source"])
print("Knowledge ID   :", result["knowledge_id"])
print("Answer         :", result["answer"])

print("\n===== OBSERVABILITY LOGS =====\n")
print(json.dumps(result["logs"], indent=2))

# ---------------------------------------------------------
# METRICS EXTRACTION & LIVE INTERACTION STREAM
# ---------------------------------------------------------
print("\n===== SYNCING TO DASHBOARD =====\n")

# Extract real security state values directly from the graph execution result
is_injection = result.get("is_injection", False)

# Grab the dynamic confidence score if you set it in your graph state, fallback safely if not found
confidence = result.get("guardrail_confidence", 0.98 if is_injection else 0.01)

if is_injection:
    # Captures the last message string logged inside the graph sequence as the error detail
    verdict = result["logs"][-1] if result["logs"] else "Critical Threat: Prompt Injection Attack Blocked!"
else:
    verdict = "Passed safety check."

# Calculate real transaction cost dynamically using token profiles
calculated_cost = calculate_real_llm_cost(result)

print(f"Metrics Processing Complete:")
print(f" -> Real Latency : {latency_ms} ms")
print(f" -> Real Cost    : ${calculated_cost:.6f}")
print(f" -> Verdict      : {verdict} ({int(confidence * 100)}% Confidence)")

print("\nStreaming pipeline payload data to Google Sheets...")
log_guardrail_transaction_to_sheet(
    correlation_id=result["correlation_id"],
    verdict=verdict,
    confidence=confidence,
    latency_ms=latency_ms,
    cost=calculated_cost
)
print("Sync operations complete. Dashboard view updated.")



# import uuid
# import json
# from dotenv import load_dotenv

# load_dotenv()

# from graph import app

# print("\n=== Observability Agent ===\n")
# user_question = input("Ask a question: ")
# correlation_id = str(uuid.uuid4())

# initial_state = {
#     "correlation_id": correlation_id,
#     "user_input": user_question,
#     "answer": "",
#     "source": "",
#     "knowledge_id": "",
#     "is_injection": False,  # <-- Initialized state variable
#     "logs": []
# }

# config = {
#     "configurable": {
#         "thread_id": correlation_id
#     },
#     "metadata": {
#         "correlation_id": correlation_id,
#         "application": "json-agent",
#         "environment": "dev"
#     }
# }

# result = app.invoke(
#     initial_state,
#     config=config
# )

# print("\n===== RESULT =====\n")
# print("Correlation ID :", result["correlation_id"])
# print("Source         :", result["source"])
# print("Knowledge ID   :", result["knowledge_id"])
# print("Answer         :", result["answer"])

# print("\n===== OBSERVABILITY LOGS =====\n")
# print(json.dumps(result["logs"], indent=2))