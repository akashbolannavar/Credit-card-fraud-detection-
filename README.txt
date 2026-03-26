╔══════════════════════════════════════════════════════════╗
║       FRAUDSHIELD — CREDIT CARD FRAUD DETECTION          ║
║              College Project Setup Guide                  ║
╚══════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FILES IN THIS FOLDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  fraud_detection.html  ← Main website (open this in Chrome)
  app.py                ← Python Flask backend
  README.txt            ← This file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 STEP 1 — INSTALL PYTHON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Go to: https://python.org/downloads
  Download & install (CHECK "Add to PATH" box!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 STEP 2 — INSTALL LIBRARIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Open CMD and run:
    pip install flask flask-cors scikit-learn pandas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 STEP 3 — RUN BACKEND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  cd D:\fraud_detection
  python app.py

  You should see:
    Running on http://127.0.0.1:5000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 STEP 4 — OPEN WEBSITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Double-click fraud_detection.html in File Explorer
  DO NOT type 127.0.0.1:5000 in the browser!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 LOGIN CREDENTIALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Username: sanjay      Password: college123
  Username: admin       Password: admin123
  Username: analyst     Password: analyst123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TEST CASES FOR DEMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FRAUD:   Amount=$90000, Hour=2, Merchant=Crypto, Country=Foreign
  SUSPECT: Amount=$3000,  Hour=23, Merchant=ATM,   Country=Asia
  SAFE:    Amount=$150,   Hour=14, Merchant=Retail, Country=Domestic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Login System (Admin/Analyst/Viewer roles)
  ✅ Real-time fraud scoring
  ✅ Radar Chart (6 risk components)
  ✅ Gauge Meter (fraud probability)
  ✅ Model Ensemble Table (XGB, LGB, RF, GB)
  ✅ Alert Status Panel
  ✅ Live Transaction Feed (auto-ticking)
  ✅ Flask REST API backend
  ✅ Works offline (local ML simulation)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ALGORITHMS USED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  XGBoost, LightGBM, Random Forest, Gradient Boost
  Dataset: IEEE-CIS Fraud Detection (Kaggle)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
