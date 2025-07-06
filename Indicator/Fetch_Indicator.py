import os
import yfinance as yf
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
# ==================== Dataset ====================
class StockDataset(Dataset):
    def __init__(self, prices, window_size=10):
        self.X, self.y = [], []
        for i in range(len(prices) - window_size):
            self.X.append(prices[i:i + window_size])
            self.y.append(prices[i + window_size])
        self.X = np.array(self.X, dtype=np.float32)
        self.y = np.array(self.y, dtype=np.float32).reshape(-1, 1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ==================== PyTorch Model ====================
class StockPriceModel(nn.Module):
    def __init__(self, input_size):
        super(StockPriceModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)

# ==================== Fetch Data ====================
def fetch_data(symbol, period = "1y"):
    data = yf.Ticker(symbol).history(period=period)
    data.reset_index(inplace=True)
    return data

# ==================== Train Model ====================
def train_model(symbol, window_size=10, epochs=100):
    prices = fetch_data(symbol)
    dataset = StockDataset(prices, window_size)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = StockPriceModel(window_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        for x_batch, y_batch in loader:
            pred = model(x_batch)
            loss = criterion(pred, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    os.makedirs("Model", exist_ok=True)
    model_path = f"Model/{symbol}_model.pt"
    torch.save(model.state_dict(), model_path)
    print(f"✅ Model saved to {model_path}")
    return model

# ==================== Load Model ====================
def load_model(symbol, window_size=10):
    model = StockPriceModel(window_size)
    model_path = f"Model/{symbol}_model.pt"
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        model.eval()
        print(f"📂 Loaded model from {model_path}")
        return model
    return None