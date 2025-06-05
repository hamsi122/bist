import pandas as pd
import numpy as np
from typing import Dict, Optional
import streamlit as st

class TechnicalAnalysis:
    """Teknik analiz hesaplamaları için sınıf"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.indicators = {}
    
    def calculate_moving_averages(self, periods: list = [5, 10, 20, 50, 100, 200]) -> Dict:
        """Hareketli ortalama hesaplar"""
        ma_data = {}
        
        for period in periods:
            if len(self.data) >= period:
                ma_key = f"MA{period}"
                ma_data[ma_key] = self.data['Close'].rolling(window=period).mean()
        
        return ma_data
    
    def calculate_rsi(self, period: int = 14) -> Optional[pd.Series]:
        """RSI (Relative Strength Index) hesaplar"""
        if len(self.data) < period + 1:
            return None
        
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD hesaplar"""
        if len(self.data) < slow:
            return {}
        
        ema_fast = self.data['Close'].ewm(span=fast).mean()
        ema_slow = self.data['Close'].ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict:
        """Bollinger Bands hesaplar"""
        if len(self.data) < period:
            return {}
        
        sma = self.data['Close'].rolling(window=period).mean()
        std = self.data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'BB_Upper': upper_band,
            'BB_Middle': sma,
            'BB_Lower': lower_band
        }
    
    def calculate_stochastic(self, k_period: int = 14, d_period: int = 3) -> Dict:
        """Stochastic Oscillator hesaplar"""
        if len(self.data) < k_period:
            return {}
        
        lowest_low = self.data['Low'].rolling(window=k_period).min()
        highest_high = self.data['High'].rolling(window=k_period).max()
        
        k_percent = 100 * ((self.data['Close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'Stoch_K': k_percent,
            'Stoch_D': d_percent
        }
    
    def calculate_williams_r(self, period: int = 14) -> Optional[pd.Series]:
        """Williams %R hesaplar"""
        if len(self.data) < period:
            return None
        
        highest_high = self.data['High'].rolling(window=period).max()
        lowest_low = self.data['Low'].rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - self.data['Close']) / (highest_high - lowest_low))
        
        return williams_r
    
    def calculate_cci(self, period: int = 20) -> Optional[pd.Series]:
        """Commodity Channel Index hesaplar"""
        if len(self.data) < period:
            return None
        
        typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x)))
        )
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        
        return cci
    
    def calculate_atr(self, period: int = 14) -> Optional[pd.Series]:
        """Average True Range hesaplar"""
        if len(self.data) < period:
            return None
        
        high_low = self.data['High'] - self.data['Low']
        high_close_prev = np.abs(self.data['High'] - self.data['Close'].shift(1))
        low_close_prev = np.abs(self.data['Low'] - self.data['Close'].shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_volume_indicators(self) -> Dict:
        """Hacim bazlı indikatörler hesaplar"""
        volume_indicators = {}
        
        # Volume Moving Average
        if len(self.data) >= 20:
            volume_indicators['Volume_MA'] = self.data['Volume'].rolling(window=20).mean()
        
        # On Balance Volume (OBV)
        if len(self.data) > 1:
            price_change = self.data['Close'].diff()
            obv = []
            obv_value = 0
            
            for i, change in enumerate(price_change):
                if pd.isna(change):
                    obv.append(obv_value)
                elif change > 0:
                    obv_value += self.data['Volume'].iloc[i]
                    obv.append(obv_value)
                elif change < 0:
                    obv_value -= self.data['Volume'].iloc[i]
                    obv.append(obv_value)
                else:
                    obv.append(obv_value)
            
            volume_indicators['OBV'] = pd.Series(obv, index=self.data.index)
        
        return volume_indicators
    
    def calculate_momentum_indicators(self) -> Dict:
        """Momentum indikatörleri hesaplar"""
        momentum_indicators = {}
        
        # Rate of Change (ROC)
        periods = [10, 20]
        for period in periods:
            if len(self.data) > period:
                roc = ((self.data['Close'] - self.data['Close'].shift(period)) / 
                       self.data['Close'].shift(period)) * 100
                momentum_indicators[f'ROC_{period}'] = roc
        
        # Momentum
        if len(self.data) > 10:
            momentum = self.data['Close'] - self.data['Close'].shift(10)
            momentum_indicators['Momentum'] = momentum
        
        return momentum_indicators
    
    def calculate_all_indicators(self) -> Dict:
        """Tüm teknik indikatörleri hesaplar"""
        try:
            all_indicators = {}
            
            # Hareketli ortalamalar
            ma_data = self.calculate_moving_averages()
            all_indicators.update(ma_data)
            
            # RSI
            rsi = self.calculate_rsi()
            if rsi is not None:
                all_indicators['RSI'] = rsi
            
            # MACD
            macd_data = self.calculate_macd()
            all_indicators.update(macd_data)
            
            # Bollinger Bands
            bb_data = self.calculate_bollinger_bands()
            all_indicators.update(bb_data)
            
            # Stochastic
            stoch_data = self.calculate_stochastic()
            all_indicators.update(stoch_data)
            
            # Williams %R
            williams_r = self.calculate_williams_r()
            if williams_r is not None:
                all_indicators['Williams_R'] = williams_r
            
            # CCI
            cci = self.calculate_cci()
            if cci is not None:
                all_indicators['CCI'] = cci
            
            # ATR
            atr = self.calculate_atr()
            if atr is not None:
                all_indicators['ATR'] = atr
            
            # Hacim indikatörleri
            volume_indicators = self.calculate_volume_indicators()
            all_indicators.update(volume_indicators)
            
            # Momentum indikatörleri
            momentum_indicators = self.calculate_momentum_indicators()
            all_indicators.update(momentum_indicators)
            
            return all_indicators
            
        except Exception as e:
            st.error(f"Teknik analiz hesaplama hatası: {str(e)}")
            return {}
    
    def get_trading_signals(self) -> Dict:
        """Al/Sat sinyalleri üretir"""
        signals = {
            "RSI_Signal": "Nötr",
            "MACD_Signal": "Nötr", 
            "MA_Signal": "Nötr",
            "Overall_Signal": "Nötr"
        }
        
        try:
            indicators = self.calculate_all_indicators()
            
            # RSI sinyalleri
            if 'RSI' in indicators:
                latest_rsi = indicators['RSI'].iloc[-1]
                if latest_rsi < 30:
                    signals["RSI_Signal"] = "Al"
                elif latest_rsi > 70:
                    signals["RSI_Signal"] = "Sat"
            
            # MACD sinyalleri
            if 'MACD' in indicators and 'Signal' in indicators:
                latest_macd = indicators['MACD'].iloc[-1]
                latest_signal = indicators['Signal'].iloc[-1]
                
                if latest_macd > latest_signal:
                    signals["MACD_Signal"] = "Al"
                else:
                    signals["MACD_Signal"] = "Sat"
            
            # MA sinyalleri
            if 'MA20' in indicators and 'MA50' in indicators:
                ma20 = indicators['MA20'].iloc[-1]
                ma50 = indicators['MA50'].iloc[-1]
                
                if ma20 > ma50:
                    signals["MA_Signal"] = "Al"
                else:
                    signals["MA_Signal"] = "Sat"
            
            # Genel sinyal
            buy_signals = sum(1 for signal in signals.values() if signal == "Al")
            sell_signals = sum(1 for signal in signals.values() if signal == "Sat")
            
            if buy_signals > sell_signals:
                signals["Overall_Signal"] = "Al"
            elif sell_signals > buy_signals:
                signals["Overall_Signal"] = "Sat"
            
        except Exception as e:
            st.error(f"Sinyal hesaplama hatası: {str(e)}")
        
        return signals
