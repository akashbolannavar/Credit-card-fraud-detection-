import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score
from sklearn.utils import resample
import xgboost as xgb
import lightgbm as lgb
import pickle
import warnings
warnings.filterwarnings('ignore')

print("="*50)
print("  FraudShield - ML Model Training")
print("="*50)

print("\n[1/6] Loading dataset...")
df = pd.read_csv('creditcard.csv')
print("      Total records : " + str(len(df)))
print("      Fraud cases   : " + str(df['Class'].sum()))

print("\n[2/6] Balancing dataset...")
df_majority = df[df['Class']==0]
df_minority = df[df['Class']==1]
df_minority_up = resample(df_minority,
    replace=True,
    n_samples=len(df_majority),
    random_state=42)
df_bal = pd.concat([df_majority, df_minority_up])
print("      Balanced size : " + str(len(df_bal)))

print("\n[3/6] Preparing features...")
X = df_bal.drop('Class', axis=1)
y = df_bal['Class']
scaler = StandardScaler()
X = X.copy()
X['Amount'] = scaler.fit_transform(X[['Amount']])
X['Time']   = scaler.fit_transform(X[['Time']])
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print("      Train : " + str(len(X_train)))
print("      Test  : " + str(len(X_test)))

print("\n[4/6] Training Models...")
print("      Training XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=100, max_depth=6,
    learning_rate=0.1, random_state=42,
    use_label_encoder=False, eval_metric='logloss')
xgb_model.fit(X_train, y_train)

print("      Training LightGBM...")
lgb_model = lgb.LGBMClassifier(
    n_estimators=100, max_depth=6,
    learning_rate=0.1, random_state=42, verbose=-1)
lgb_model.fit(X_train, y_train)

print("      Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100, max_depth=8,
    random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

print("      Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=100, max_depth=5,
    learning_rate=0.1, random_state=42)
gb_model.fit(X_train, y_train)

print("\n[5/6] Evaluating Models...")
for name, model in [('XGBoost', xgb_model),
                    ('LightGBM', lgb_model),
                    ('Random Forest', rf_model),
                    ('Gradient Boosting', gb_model)]:
    yp = model.predict(X_test)
    yb = model.predict_proba(X_test)[:,1]
    print("\n      " + name)
    print("        Accuracy  : " + str(round(accuracy_score(y_test,yp)*100,2)) + "%")
    print("        AUC-ROC   : " + str(round(roc_auc_score(y_test,yb),4)))
    print("        Precision : " + str(round(precision_score(y_test,yp)*100,2)) + "%")
    print("        Recall    : " + str(round(recall_score(y_test,yp)*100,2)) + "%")

print("\n[6/6] Saving models...")
pickle.dump(xgb_model, open('model_xgb.pkl','wb'))
pickle.dump(lgb_model, open('model_lgb.pkl','wb'))
pickle.dump(rf_model,  open('model_rf.pkl', 'wb'))
pickle.dump(gb_model,  open('model_gb.pkl', 'wb'))
pickle.dump(scaler,    open('scaler.pkl',   'wb'))
print("      model_xgb.pkl saved")
print("      model_lgb.pkl saved")
print("      model_rf.pkl  saved")
print("      model_gb.pkl  saved")
print("      scaler.pkl    saved")
print("\n" + "="*50)
print("  Training Complete!")
print("="*50)