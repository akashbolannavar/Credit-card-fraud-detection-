from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import mysql.connector
import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# ── EMAIL SETTINGS ────────────────────────────────
EMAIL_SENDER   = "akashbolannavar1234@gmail.com"
EMAIL_PASSWORD = "xfrn otxp srys fpvw"
EMAIL_RECEIVER = "akashbolannavar1234@gmail.com"

# ── LOAD ML MODELS ────────────────────────────────
print("Loading ML models...")
xgb_model = pickle.load(open('model_xgb.pkl','rb'))
lgb_model = pickle.load(open('model_lgb.pkl','rb'))
rf_model  = pickle.load(open('model_rf.pkl', 'rb'))
gb_model  = pickle.load(open('model_gb.pkl', 'rb'))
scaler    = pickle.load(open('scaler.pkl',   'rb'))
print("All models loaded!")

# ── MYSQL CONFIG ──────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',
    'database': 'fraud_db'
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            tx_id     VARCHAR(50),
            amount    FLOAT,
            hour      INT,
            merchant  VARCHAR(50),
            country   VARCHAR(50),
            txcount   INT,
            age       INT,
            gender    VARCHAR(5),
            score     FLOAT,
            result    VARCHAR(20),
            level     VARCHAR(20),
            timestamp DATETIME
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            fullname  VARCHAR(100),
            email     VARCHAR(100),
            username  VARCHAR(50) UNIQUE,
            password  VARCHAR(100),
            role      VARCHAR(20),
            created   DATETIME
        )
    ''')
    c.execute('''
        INSERT IGNORE INTO users (fullname,email,username,password,role,created)
        VALUES
        ('Akash','akashbolannavar1234@gmail.com','Akash','Kle@123','Admin',NOW()),
        ('Sanjay','sanjay@gmail.com','sanjay','college123','Admin',NOW()),
        ('Analyst','analyst@gmail.com','analyst','analyst123','Analyst',NOW())
    ''')
    conn.commit()
    conn.close()
    print("MySQL Database ready: fraud_db")

def save_transaction(tx_id, amount, hour, merchant, country,
                     txcount, age, gender, score, result, level):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions
        (tx_id,amount,hour,merchant,country,txcount,age,
         gender,score,result,level,timestamp)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ''', (tx_id, amount, hour, merchant, country,
          txcount, age, gender, score, result, level,
          datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# ── FRAUD ALERT EMAIL ─────────────────────────────
def send_fraud_alert(tx_id, amount, score, merchant, country):
    try:
        print("Sending fraud alert email...")

        # Set color and status based on score
        if score >= 65:
            color       = "ff4444"
            border      = "ff4444"
            bg          = "ff000033"
            status      = "Transaction BLOCKED"
            emoji       = "FRAUD ALERT DETECTED"
            risk        = "HIGH RISK"
        elif score >= 35:
            color       = "FF9F0A"
            border      = "FF9F0A"
            bg          = "FF9F0A33"
            status      = "Transaction FLAGGED for Review"
            emoji       = "SUSPECT TRANSACTION"
            risk        = "MEDIUM RISK"
        else:
            color       = "00ff88"
            border      = "00ff88"
            bg          = "00ff8833"
            status      = "Transaction APPROVED"
            emoji       = "TRANSACTION SAFE"
            risk        = "LOW RISK"

        msg            = MIMEMultipart("alternative")
        msg["Subject"] = risk + " - FraudShield Alert - " + str(tx_id)
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER

        html = """
<html>
<body style="font-family:Arial;background:#0a0a0a;color:white;padding:20px;">
<div style="background:#1a1a2e;border:2px solid #""" + border + """;
            border-radius:10px;padding:20px;max-width:580px;margin:auto;">
  <h1 style="color:#""" + color + """;text-align:center;">
    """ + emoji + """
  </h1>
  <div style="background:""" + bg + """;border-radius:8px;
              padding:15px;text-align:center;margin:15px 0;">
    <h2 style="color:#""" + color + """;margin:0;">""" + status + """</h2>
  </div>
  <table style="width:100%;color:white;border-collapse:collapse;">
    <tr style="background:#ffffff11;">
      <td style="padding:10px;color:#aaa;">Transaction ID</td>
      <td style="padding:10px;color:#00d4ff;font-weight:bold;">""" + str(tx_id) + """</td>
    </tr>
    <tr>
      <td style="padding:10px;color:#aaa;">Amount</td>
      <td style="padding:10px;color:#""" + color + """;font-weight:bold;font-size:18px;">$""" + str(amount) + """</td>
    </tr>
    <tr style="background:#ffffff11;">
      <td style="padding:10px;color:#aaa;">Fraud Score</td>
      <td style="padding:10px;color:#""" + color + """;font-weight:bold;font-size:18px;">""" + str(score) + """%</td>
    </tr>
    <tr>
      <td style="padding:10px;color:#aaa;">Risk Level</td>
      <td style="padding:10px;color:#""" + color + """;font-weight:bold;">""" + risk + """</td>
    </tr>
    <tr style="background:#ffffff11;">
      <td style="padding:10px;color:#aaa;">Merchant</td>
      <td style="padding:10px;color:white;">""" + str(merchant) + """</td>
    </tr>
    <tr>
      <td style="padding:10px;color:#aaa;">Country</td>
      <td style="padding:10px;color:white;">""" + str(country) + """</td>
    </tr>
    <tr style="background:#ffffff11;">
      <td style="padding:10px;color:#aaa;">Date and Time</td>
      <td style="padding:10px;color:#ffd60a;">""" + datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + """</td>
    </tr>
  </table>
  <p style="color:#666;text-align:center;margin-top:20px;font-size:11px;">
    FraudShield v3.0 - Real-Time Fraud Detection System
  </p>
</div>
</body>
</html>"""

        msg.attach(MIMEText(html, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent (" + risk + ") to " + EMAIL_RECEIVER + " ✅")

    except Exception as e:
        print("Email error: " + str(e))

# ── LOGIN ALERT EMAIL ─────────────────────────────
def send_login_alert(username, email, role):
    try:
        print("Sending login alert email...")
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = "Login Alert - FraudShield System"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = email
        now = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')

        html = """
<html>
<body style="font-family:Arial;background:#0a0a0a;color:white;padding:20px;">
<div style="background:#1a1a2e;border:2px solid #00d4ff;
            border-radius:10px;padding:20px;max-width:580px;margin:auto;">
  <h1 style="color:#00d4ff;text-align:center;">
    FraudShield Login Alert
  </h1>
  <div style="background:rgba(0,255,136,0.1);border:1px solid #00ff88;
              border-radius:8px;padding:15px;text-align:center;margin:15px 0;">
    <h2 style="color:#00ff88;margin:0;">Successful Login Detected</h2>
  </div>
  <table style="width:100%;color:white;border-collapse:collapse;">
    <tr style="background:#ffffff11;">
      <td style="padding:10px;color:#aaa;">Username</td>
      <td style="padding:10px;color:#00d4ff;font-weight:bold;">""" + str(username) + """</td>
    </tr>
    <tr>
      <td style="padding:10px;color:#aaa;">Role</td>
      <td style="padding:10px;color:#00ff88;font-weight:bold;">""" + str(role) + """</td>
    </tr>
    <tr style="background:#ffffff11;">
      <td style="padding:10px;color:#aaa;">Email</td>
      <td style="padding:10px;color:white;">""" + str(email) + """</td>
    </tr>
    <tr>
      <td style="padding:10px;color:#aaa;">Login Time</td>
      <td style="padding:10px;color:#ffd60a;font-weight:bold;">""" + now + """</td>
    </tr>
  </table>
  <div style="background:rgba(255,255,0,0.05);border-radius:8px;
              padding:12px;text-align:center;margin-top:15px;">
    <p style="color:#aaa;margin:0;font-size:13px;">
      If this was not you, contact your administrator immediately!
    </p>
  </div>
  <p style="color:#666;text-align:center;margin-top:20px;font-size:11px;">
    FraudShield v3.0 - Real-Time Fraud Detection System
  </p>
</div>
</body>
</html>"""

        msg.attach(MIMEText(html, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
        print("Login alert email sent to " + email + " ✅")

    except Exception as e:
        print("Login email error: " + str(e))

# ── ML FEATURES ───────────────────────────────────
def prepare_features(amount, hour, merchant, country, txcount, age, gender):
    merchant_risk = {
        'retail':0.1,'grocery':0.1,'restaurant':0.1,
        'online':0.3,'atm':0.5,'travel':0.3,
        'luxury':0.6,'crypto':0.9
    }
    country_risk = {
        'domestic':0.1,'asia':0.5,
        'europe':0.4,'foreign':0.8
    }
    m_risk      = merchant_risk.get(merchant, 0.3)
    c_risk      = country_risk.get(country, 0.3)
    hour_risk   = 0.9 if hour<=3 else 0.7 if hour<=5 else 0.6 if hour>=22 else 0.1
    amount_risk = 0.9 if amount>50000 else 0.7 if amount>10000 else 0.4 if amount>2000 else 0.1
    age_risk    = 0.6 if age<22 or age>75 else 0.1
    tx_risk     = 0.8 if txcount>20 else 0.5 if txcount>10 else 0.1

    features     = np.zeros(30)
    features[0]  = hour_risk*10
    features[1]  = amount_risk*10
    features[2]  = m_risk*10
    features[3]  = c_risk*10
    features[4]  = tx_risk*10
    features[5]  = age_risk*10
    features[6]  = hour_risk*amount_risk*10
    features[7]  = m_risk*c_risk*10
    features[8]  = tx_risk*age_risk*10
    features[9]  = (m_risk+c_risk+hour_risk)*3
    features[10] = amount_risk*m_risk*10
    features[11] = c_risk*hour_risk*10
    features[12] = tx_risk*m_risk*10
    features[13] = age_risk*c_risk*10
    features[14] = (amount_risk*0.4+m_risk*0.3+c_risk*0.3)*10
    features[15] = hour_risk*tx_risk*10
    features[16] = amount_risk*c_risk*10
    features[17] = m_risk*age_risk*10
    features[18] = (hour_risk+tx_risk)*5
    features[19] = (m_risk+amount_risk)*5
    features[20] = c_risk*tx_risk*10
    features[21] = hour_risk*age_risk*10
    features[22] = amount_risk*tx_risk*10
    features[23] = (m_risk*c_risk*hour_risk)*10
    features[24] = (amount_risk+tx_risk)*5
    features[25] = m_risk*hour_risk*10
    features[26] = c_risk*age_risk*10
    features[27] = (amount_risk*m_risk*c_risk)*10
    features[28] = hour_risk*5
    features[29] = amount
    return features.reshape(1,-1)

def get_ensemble_score(features, amount, hour, merchant, country, txcount, age):
    xgb_prob = float(xgb_model.predict_proba(features)[0][1])
    lgb_prob = float(lgb_model.predict_proba(features)[0][1])
    rf_prob  = float(rf_model.predict_proba(features)[0][1])
    gb_prob  = float(gb_model.predict_proba(features)[0][1])
    ml_score = (xgb_prob+lgb_prob+rf_prob+gb_prob)/4

    rule = 0
    if amount>50000:     rule+=55
    elif amount>10000:   rule+=35
    elif amount>2000:    rule+=15
    if hour<=3:          rule+=35
    elif hour<=5:        rule+=25
    elif hour>=22:       rule+=15
    if merchant=='crypto':   rule+=45
    elif merchant=='luxury': rule+=25
    elif merchant=='atm':    rule+=18
    if country=='foreign':   rule+=40
    elif country=='asia':    rule+=18
    if txcount>20:       rule+=30
    elif txcount>10:     rule+=18
    if age<22 or age>75: rule+=12
    rule_score = min(rule,100)/100

    final_score = float(round(((ml_score*0.3)+(rule_score*0.7))*100,2))
    models = [
        {'name':'XGB','prob':float(round(xgb_prob*100,1)),
         'pred':'Fraud' if xgb_prob>=0.5 else 'Legitimate'},
        {'name':'LGB','prob':float(round(lgb_prob*100,1)),
         'pred':'Fraud' if lgb_prob>=0.5 else 'Legitimate'},
        {'name':'RF', 'prob':float(round(rf_prob*100, 1)),
         'pred':'Fraud' if rf_prob>=0.5  else 'Legitimate'},
        {'name':'GB', 'prob':float(round(gb_prob*100, 1)),
         'pred':'Fraud' if gb_prob>=0.5  else 'Legitimate'},
    ]
    return final_score, models

# ── ROUTES ────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    data     = request.json
    amount   = float(data.get('amount',500))
    hour     = int(data.get('hour',12))
    merchant = data.get('merchant','retail')
    country  = data.get('country','domestic')
    txcount  = int(data.get('txcount',3))
    age      = int(data.get('age',35))
    gender   = data.get('gender','M')

    features      = prepare_features(amount,hour,merchant,country,txcount,age,gender)
    score, models = get_ensemble_score(features,amount,hour,merchant,country,txcount,age)
    score  = float(score)
    level  = 'high'   if score>=65 else 'medium' if score>=35 else 'low'
    result = 'fraud'  if score>=65 else 'suspect' if score>=35 else 'safe'
    tx_id  = 'TXN'+datetime.datetime.now().strftime('%H%M%S')+str(random.randint(1000,9999))

    save_transaction(tx_id,amount,hour,merchant,country,
                     txcount,age,gender,score,result,level)

    print("Saved: {} | ${} | {} | Score:{}%".format(
          tx_id,amount,result.upper(),score))

    send_fraud_alert(tx_id, amount, score, merchant, country)

    return jsonify({
        'tx_id':  tx_id,
        'score':  score,
        'result': result,
        'level':  level,
        'models': models
    })

@app.route('/login_check', methods=['POST'])
def login_check():
    data     = request.json
    username = data.get('username','')
    password = data.get('password','')
    try:
        conn = get_conn()
        c    = conn.cursor(dictionary=True)
        c.execute('SELECT * FROM users WHERE username=%s AND password=%s',
                  (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            send_login_alert(user['username'], user['email'], user['role'])
            return jsonify({
                'status':   'success',
                'username': user['username'],
                'role':     user['role'],
                'fullname': user['fullname'],
                'email':    user['email']
            })
        else:
            return jsonify({'status':'error','message':'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    data     = request.json
    fullname = data.get('fullname','')
    email    = data.get('email','')
    username = data.get('username','')
    password = data.get('password','')
    role     = data.get('role','Analyst')

    if not fullname or not email or not username or not password:
        return jsonify({'status':'error','message':'All fields required'}), 400
    try:
        conn = get_conn()
        c    = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=%s',(username,))
        if c.fetchone():
            conn.close()
            return jsonify({'status':'error','message':'Username already exists!'}), 400
        c.execute('''INSERT INTO users (fullname,email,username,password,role,created)
                     VALUES (%s,%s,%s,%s,%s,%s)''',
                  (fullname,email,username,password,role,
                   datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        return jsonify({'status':'success','message':'Account created successfully!'})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_conn()
    c    = conn.cursor(dictionary=True)
    c.execute('SELECT id,fullname,email,username,role,created FROM users')
    rows = c.fetchall()
    conn.close()
    return jsonify({'total':len(rows),'users':rows})

@app.route('/transactions', methods=['GET'])
def get_transactions():
    conn = get_conn()
    c    = conn.cursor(dictionary=True)
    c.execute('SELECT * FROM transactions ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return jsonify({'total':len(rows),'transactions':rows})

@app.route('/frauds', methods=['GET'])
def get_frauds():
    conn = get_conn()
    c    = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM transactions WHERE level='high' ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify({'total_frauds':len(rows),'transactions':rows})

@app.route('/stats', methods=['GET'])
def get_stats():
    conn = get_conn()
    c    = conn.cursor()
    c.execute("SELECT COUNT(*) FROM transactions")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM transactions WHERE level='high'")
    frauds = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM transactions WHERE level='medium'")
    suspects = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM transactions WHERE level='low'")
    safe = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM transactions WHERE level='high'")
    blocked = c.fetchone()[0] or 0
    conn.close()
    return jsonify({
        'total':          total,
        'frauds':         frauds,
        'suspects':       suspects,
        'safe':           safe,
        'amount_blocked': round(float(blocked),2)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'model':  'FraudShield v3.0 - Real ML',
        'db':     'MySQL'
    })

def send_startup_email():
    try:
        print("Sending startup email...")
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = "FraudShield System Started!"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER

        html = """
<html>
<body style="font-family:Arial;background:#0a0a0a;padding:20px;">
<div style="background:#1a1a2e;border:2px solid #00ff88;
            border-radius:10px;padding:20px;max-width:500px;margin:auto;">
  <h1 style="color:#00ff88;text-align:center;">
    FraudShield System ONLINE
  </h1>
  <div style="background:rgba(0,255,136,0.1);border-radius:8px;
              padding:15px;text-align:center;">
    <h2 style="color:#00d4ff;margin:0;">Backend Started Successfully!</h2>
  </div>
  <table style="width:100%;color:white;margin-top:15px;">
    <tr><td style="color:#aaa;">Status</td>
        <td style="color:#00ff88;font-weight:bold;">ONLINE</td></tr>
    <tr><td style="color:#aaa;">ML Models</td>
        <td style="color:#00d4ff;">4 Models Loaded</td></tr>
    <tr><td style="color:#aaa;">Database</td>
        <td style="color:#00d4ff;">MySQL Connected</td></tr>
    <tr><td style="color:#aaa;">API Port</td>
        <td style="color:#ffd60a;">5000</td></tr>
  </table>
  <p style="color:#666;text-align:center;margin-top:15px;font-size:11px;">
    FraudShield v3.0 - System Alert
  </p>
</div>
</body>
</html>"""

        msg.attach(MIMEText(html, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Startup email sent ✅")
    except Exception as e:
        print("Startup email error: " + str(e))


#

if __name__ == '__main__':
    init_db()
    send_startup_email()
    print("="*50)
    print("  FraudShield Backend - Real ML + Email")
    print("  Email: " + EMAIL_SENDER)
    print("  POST /predict       - Fraud detection")
    print("  POST /login_check   - Login + email alert")
    print("  POST /signup        - Register to MySQL")
    print("  GET  /users         - View all users")
    print("  GET  /transactions  - View all data")
    print("  GET  /stats         - Summary")
    print("="*50)
    app.run(debug=True, port=5000)