import requests

# The local URL where your FastAPI is running
URL = "http://127.0.0.1:8000/predict"

# Fake data matching your LoanInput Pydantic model
test_data = {
    "gender": 1,
    "married": 1,
    "dependents": 2,
    "education": 0,
    "self_employed": 0,
    "applicant_income": 5000.0,
    "coapplicant_income": 2000.0,
    "loan_amount": 150.0,
    "loan_term": 360.0,
    "credit_history": 1.0,
    "property_area": 2,
    "model_choice": "logistic"  # Test both "logistic" and "decision_tree"
}

print(f"🚀 Sending test request to {URL}...")

try:
    response = requests.post(URL, json=test_data)
    
    if response.status_code == 200:
        print("✅ SUCCESS!")
        print("Response from API:", response.json())
    else:
        print(f"❌ FAILED with status code: {response.status_code}")
        print("Error details:", response.text)

except Exception as e:
    print(f"📡 Connection Error: {e}")