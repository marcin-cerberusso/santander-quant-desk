# ai_oracle.py - Machine Learning Price Prediction Engine
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AIOracleEngine:
    """
    AI Oracle - ML-powered price movement predictor
    Używa Random Forest do klasyfikacji wzrostu/spadku na podstawie wskaźników technicznych
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def create_features(self, df):
        """Tworzy features z danych OHLCV + wskaźników"""
        if df.empty or len(df) < 30:
            return None, None
        
        # Fix MultiIndex from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['close'] = df['Close'].values
        features['volume'] = df['Volume'].values
        features['high_low_spread'] = ((df['High'] - df['Low']) / df['Close']).values
        features['close_open_spread'] = ((df['Close'] - df['Open']) / df['Open']).values
        
        # Moving averages
        features['sma5'] = df['Close'].rolling(5).mean().values
        features['sma10'] = df['Close'].rolling(10).mean().values
        features['sma20'] = df['Close'].rolling(20).mean().values
        features['sma_ratio_5_20'] = (features['sma5'] / features['sma20']).values
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi'] = (100 - (100 / (1 + rs))).values
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        features['macd'] = macd.values
        features['macd_signal'] = macd_signal.values
        features['macd_diff'] = (macd - macd_signal).values
        
        # Momentum
        features['momentum_5'] = df['Close'].pct_change(5).values
        features['momentum_10'] = df['Close'].pct_change(10).values
        
        # Volatility
        vol_std = df['Close'].rolling(10).std()
        vol_mean = df['Close'].rolling(10).mean()
        features['volatility'] = (vol_std / vol_mean).values
        
        # Volume trend
        volume_sma = df['Volume'].rolling(10).mean()
        features['volume_sma'] = volume_sma.values
        features['volume_ratio'] = (df['Volume'] / volume_sma).values
        
        # Target: Czy cena wzrośnie w ciągu następnych 3 dni?
        features['target'] = (df['Close'].shift(-3) > df['Close']).astype(int).values
        
        # Drop NaN
        features = features.dropna()
        
        if features.empty:
            return None, None
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        return X, y
        
        # Drop NaN
        features = features.dropna()
        
        if features.empty:
            return None, None
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        return X, y
    
    def train(self, historical_data):
        """Trenuje model na danych historycznych"""
        X, y = self.create_features(historical_data)
        
        if X is None or len(X) < 50:
            return False
        
        # Normalizacja
        X_scaled = self.scaler.fit_transform(X)
        
        # Trening
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Accuracy na training set (dla informacji)
        train_score = self.model.score(X_scaled, y)
        return train_score
    
    def predict(self, current_data):
        """
        Przewiduje ruch ceny dla najnowszych danych
        
        Returns:
            dict: {
                'prediction': 'UP' | 'DOWN',
                'confidence': float (0-100%),
                'probability_up': float,
                'probability_down': float
            }
        """
        if not self.is_trained:
            # Auto-train on available data
            train_score = self.train(current_data)
            if not train_score:
                return {
                    'prediction': 'NEUTRAL',
                    'confidence': 0,
                    'probability_up': 50,
                    'probability_down': 50,
                    'error': 'Insufficient data for training'
                }
        
        X, _ = self.create_features(current_data)
        
        if X is None or X.empty:
            return {
                'prediction': 'NEUTRAL',
                'confidence': 0,
                'probability_up': 50,
                'probability_down': 50,
                'error': 'Insufficient features'
            }
        
        # Bierzemy tylko ostatni wiersz (najnowsze dane)
        X_latest = X.iloc[-1:].copy()
        
        # Normalizacja
        X_scaled = self.scaler.transform(X_latest)
        
        # Predykcja
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        prob_down = probabilities[0] * 100
        prob_up = probabilities[1] * 100
        
        confidence = max(prob_up, prob_down)
        
        return {
            'prediction': 'UP' if prediction == 1 else 'DOWN',
            'confidence': round(confidence, 1),
            'probability_up': round(prob_up, 1),
            'probability_down': round(prob_down, 1),
            'signal_strength': 'STRONG' if confidence > 70 else 'MODERATE' if confidence > 60 else 'WEAK'
        }
    
    def batch_predict(self, stocks_data_dict):
        """
        Przewiduje dla wielu spółek naraz
        
        Args:
            stocks_data_dict: {ticker: DataFrame}
        
        Returns:
            {ticker: prediction_dict}
        """
        predictions = {}
        
        for ticker, df in stocks_data_dict.items():
            try:
                pred = self.predict(df)
                predictions[ticker] = pred
            except Exception as e:
                predictions[ticker] = {
                    'prediction': 'ERROR',
                    'confidence': 0,
                    'error': str(e)
                }
        
        return predictions


# Quick test function
if __name__ == "__main__":
    import yfinance as yf
    
    print("🧠 AI ORACLE - ML Price Predictor")
    print("=" * 60)
    
    # Test na CDR
    ticker = "CDR.WA"
    print(f"\n📊 Testing on {ticker}...")
    
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    
    if not df.empty:
        oracle = AIOracleEngine()
        
        # Train
        print("🎓 Training model...")
        score = oracle.train(df)
        print(f"✅ Training accuracy: {score*100:.1f}%")
        
        # Predict
        print("\n🔮 Predicting next move...")
        prediction = oracle.predict(df)
        
        print(f"\n{'='*60}")
        print(f"🎯 PREDICTION: {prediction['prediction']}")
        print(f"💪 Confidence: {prediction['confidence']}%")
        print(f"📈 Prob UP: {prediction['probability_up']}%")
        print(f"📉 Prob DOWN: {prediction['probability_down']}%")
        print(f"⚡ Strength: {prediction['signal_strength']}")
        print(f"{'='*60}")
    else:
        print("❌ Failed to download data")
