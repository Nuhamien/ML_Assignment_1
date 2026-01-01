import os
import joblib
import numpy as np
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. FIX: Setup absolute paths for Vercel deployment
# This finds the folder where this main.py file is sitting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_model_path(filename):
    return os.path.join(BASE_DIR, filename)

# 2. FIX: Load models using the absolute path
try:
    lr_model = joblib.load(get_model_path("loan_lr_model.joblib"))
    dt_model = joblib.load(get_model_path("loan_dt_model.joblib"))
    scaler = joblib.load(get_model_path("loan_scaler.joblib"))
    print("Successfully loaded models from:", BASE_DIR)
except Exception as e:
    print(f"CRITICAL ERROR loading models: {e}")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoanInput(BaseModel):
    gender: int         # 0: Female, 1: Male
    married: int        # 0: No, 1: Yes
    dependents: int     # 0, 1, 2, 3
    education: int      # 0: Graduate, 1: Not Graduate
    self_employed: int  # 0: No, 1: Yes
    applicant_income: float
    coapplicant_income: float
    loan_amount: float
    loan_term: float
    credit_history: float # 1.0 or 0.0
    property_area: int  # 0: Rural, 1: Urban, 2: Semiurban
    model_choice: str   # "logistic" or "decision_tree"

@app.post("/predict")
def predict_loan(data: LoanInput):
    # Organise features into a list (order must match the training dataframe)
    features = [
        data.gender, data.married, data.dependents, data.education,
        data.self_employed, data.applicant_income, data.coapplicant_income,
        data.loan_amount, data.loan_term, data.credit_history, data.property_area
    ]
    
    features_array = np.array([features])

    if data.model_choice == "logistic":
        # Logistic Regression needs scaled data
        scaled_features = scaler.transform(features_array)
        prediction = lr_model.predict(scaled_features)
    else:
        # Decision Tree uses raw features
        prediction = dt_model.predict(features_array)

    # Convert 1 to "Approved" and 0 to "Rejected"
    result = "Approved" if prediction[0] == 1 else "Rejected"
    
    return {
        "status": result,
        "model_used": data.model_choice
    }

@app.get("/")
def home():
    return {"message": "Loan Prediction API is Live!"}

# 3. FIX: Create the handler for Vercel (Mangum)
handler = Mangum(app)