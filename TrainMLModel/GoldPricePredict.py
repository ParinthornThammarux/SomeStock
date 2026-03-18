# ================================
# 1. Import Libraries
# ================================
import yfinance as yf
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

import matplotlib.pyplot as plt

# ================================
# 2. Download Data
# ================================
tickers = {
    "gold": "GC=F",
    "dxy": "DX=F",
    "sp500": "^GSPC",
    "oil": "CL=F",
    "bond": "^TNX"
}

data = {}

for name, ticker in tickers.items():
    df = yf.download(ticker, start="2016-01-01", progress=True)

    if df.empty or "Close" not in df.columns:
        continue

    data[name] = df["Close"]

if len(data) == 0:
    raise ValueError("No data downloaded!")

df = pd.concat(data, axis=1)
df.columns = data.keys()
df.dropna(inplace=True)

# ================================
# 3. Feature Engineering
# ================================
for col in df.columns:
    df[f"{col}_lag1"] = df[col].shift(1)
    df[f"{col}_lag3"] = df[col].shift(3)
    df[f"{col}_lag7"] = df[col].shift(7)

df["gold_ma7"] = df["gold"].rolling(7).mean()
df["gold_ma14"] = df["gold"].rolling(14).mean()

# ================================
# 4. Target
# ================================
df["target"] = df["gold"].shift(-7)
df.dropna(inplace=True)

# ================================
# 5. Split
# ================================
X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# ================================
# 6. Train
# ================================
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

xgb_model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    random_state=42
)
xgb_model.fit(X_train, y_train)

# ================================
# 7. Predict
# ================================
lr_pred = lr_model.predict(X_test)
xgb_pred = xgb_model.predict(X_test)

# ================================
# 📊 8. Plot (เฉพาะ 1 ปีล่าสุด)
# ================================
# รวมเป็น DataFrame
# plot_df = pd.DataFrame({
#     "Actual": y_test,
#     "Linear Regression": lr_pred,
#     "XGBoost": xgb_pred
# }, index=y_test.index)

# # เอาแค่ 1 ปีล่าสุด
# plot_df = plot_df.last("365D")

# plt.figure(figsize=(12,6))

# plt.plot(plot_df.index, plot_df["Actual"], label="Actual")
# plt.plot(plot_df.index, plot_df["Linear Regression"], label="Linear Regression")
# plt.plot(plot_df.index, plot_df["XGBoost"], label="XGBoost")

# plt.title("Gold Price Prediction vs Actual (Last 1 Year)")
# plt.xlabel("Date")
# plt.ylabel("Price")
# plt.legend()

# plt.show()

# ================================
# Save Results ✅
# ================================
result_df = pd.DataFrame({
    "Actual": y_test,
    "Linear Regression": lr_pred,
    "XGBoost": xgb_pred
}, index=y_test.index)

# เอาแค่ 1 ปีล่าสุด
result_df = result_df.last("365D")

result_df.to_csv("predictions.csv")

print("✅ Saved predictions.csv")