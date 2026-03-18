import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D
from tensorflow.keras.models import Model

# ---------------------------
# 1. โหลดข้อมูล
# ---------------------------
data = yf.download("GC=F", start="2015-01-01", end="2025-01-01")

# ---------------------------
# 2. Feature Engineering
# ---------------------------
data['Return'] = data['Close'].pct_change()
data['MA20'] = data['Close'].rolling(20).mean()
data['MA50'] = data['Close'].rolling(50).mean()
data['Volatility'] = data['Close'].rolling(20).std()
data['Momentum'] = data['Close'] - data['Close'].shift(10)

data = data.dropna()

# ใช้ Return เป็น target (column 0)
features = data[['Return', 'MA20', 'MA50', 'Volatility', 'Momentum']]

# ---------------------------
# 3. Train/Test Split
# ---------------------------
train_size = int(len(features) * 0.8)

train_data = features[:train_size]
test_data = features[train_size:]

# ใช้ StandardScaler (สำคัญมาก)
scaler = StandardScaler()
scaler.fit(train_data)

scaled_train = scaler.transform(train_data)
scaled_test = scaler.transform(test_data)

scaled_data = np.concatenate((scaled_train, scaled_test), axis=0)

# ---------------------------
# 4. Create Dataset
# ---------------------------
def create_dataset(data, window=120):
    X, y = [], []
    for i in range(window, len(data)):
        X.append(data[i-window:i])
        y.append(data[i][0])  # Return
    return np.array(X), np.array(y)

window_size = 120
X, y = create_dataset(scaled_data, window_size)

# split sequence
split = int(len(X) * 0.8)

X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# ---------------------------
# 5. Transformer Model
# ---------------------------
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads)(inputs, inputs)
    x = Dropout(dropout)(x)
    x = LayerNormalization(epsilon=1e-6)(x + inputs)

    ff = Dense(ff_dim, activation="relu")(x)
    ff = Dense(inputs.shape[-1])(ff)
    ff = Dropout(dropout)(ff)

    return LayerNormalization(epsilon=1e-6)(x + ff)

inputs = Input(shape=(window_size, X.shape[2]))

x = transformer_encoder(inputs, 64, 4, 128, 0.2)
x = transformer_encoder(x, 64, 4, 128, 0.2)

x = GlobalAveragePooling1D()(x)
x = Dense(64, activation="relu")(x)
x = Dropout(0.2)(x)
outputs = Dense(1)(x)

model = Model(inputs, outputs)

model.compile(optimizer="adam", loss="mae")

model.summary()

# ---------------------------
# 6. Train
# ---------------------------
history = model.fit(
    X_train,
    y_train,
    epochs=60,
    batch_size=32,
    validation_data=(X_test, y_test),
    shuffle=False
)

# ---------------------------
# 7. Predict (scaled return)
# ---------------------------
pred_scaled = model.predict(X_test)

# ---------------------------
# 8. Inverse Scale Return (สำคัญ!)
# ---------------------------
dummy = np.zeros((len(pred_scaled), scaled_data.shape[1]))
dummy[:, 0] = pred_scaled[:, 0]

pred_return = scaler.inverse_transform(dummy)[:, 0]

# ---------------------------
# 9. Convert Return → Price
# ---------------------------
close_prices = data['Close'].values

start_index = train_size + window_size
last_price = close_prices[start_index]

pred_prices = []

for r in pred_return:
    last_price = last_price * (1 + r)
    pred_prices.append(last_price)

# Real prices
real_prices = close_prices[start_index:start_index + len(pred_prices)]

# ---------------------------
# 10. Plot
# ---------------------------
plt.figure(figsize=(12,6))
plt.plot(real_prices, label="Real Price")
plt.plot(pred_prices, label="Predicted Price")
plt.title("Gold Price Prediction (Transformer - Fixed)")
plt.legend()
plt.show()