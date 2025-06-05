import locale
from datetime import datetime, timedelta
import pandas as pd
from typing import Union, Optional
import streamlit as st

# Türkçe yerel ayarlar için
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except:
        # Varsayılan ayarları kullan
        pass

def format_currency(amount: Union[float, int], currency: str = "₺") -> str:
    """Para birimi formatlaması"""
    if amount is None:
        return "N/A"
    
    try:
        if abs(amount) >= 1_000_000_000:
            return f"{amount/1_000_000_000:.2f}B {currency}"
        elif abs(amount) >= 1_000_000:
            return f"{amount/1_000_000:.2f}M {currency}"
        elif abs(amount) >= 1_000:
            return f"{amount/1_000:.2f}K {currency}"
        else:
            return f"{amount:.2f} {currency}"
    except:
        return f"{amount} {currency}"

def format_percentage(value: Union[float, int], decimal_places: int = 2) -> str:
    """Yüzde formatlaması"""
    if value is None:
        return "N/A"
    
    try:
        return f"{value:.{decimal_places}f}%"
    except:
        return f"{value}%"

def format_number(number: Union[float, int], decimal_places: int = 2) -> str:
    """Sayı formatlaması"""
    if number is None:
        return "N/A"
    
    try:
        if isinstance(number, float):
            return f"{number:,.{decimal_places}f}"
        else:
            return f"{number:,}"
    except:
        return str(number)

def get_turkish_date(date: datetime, include_time: bool = False) -> str:
    """Türkçe tarih formatlaması"""
    turkish_months = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }
    
    turkish_days = {
        0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 
        4: "Cuma", 5: "Cumartesi", 6: "Pazar"
    }
    
    try:
        day_name = turkish_days[date.weekday()]
        month_name = turkish_months[date.month]
        
        if include_time:
            return f"{day_name}, {date.day} {month_name} {date.year} {date.hour:02d}:{date.minute:02d}"
        else:
            return f"{day_name}, {date.day} {month_name} {date.year}"
    except:
        return date.strftime("%d.%m.%Y %H:%M" if include_time else "%d.%m.%Y")

def get_turkish_time_period(period: str) -> str:
    """Zaman periyodunu Türkçe'ye çevirir"""
    period_translations = {
        "1d": "1 Gün",
        "5d": "5 Gün", 
        "1mo": "1 Ay",
        "3mo": "3 Ay",
        "6mo": "6 Ay",
        "1y": "1 Yıl",
        "2y": "2 Yıl",
        "5y": "5 Yıl",
        "10y": "10 Yıl",
        "ytd": "Yıl Başından Beri",
        "max": "Maksimum"
    }
    
    return period_translations.get(period, period)

def calculate_performance_metrics(data: pd.DataFrame) -> dict:
    """Performans metriklerini hesaplar"""
    if data.empty or len(data) < 2:
        return {}
    
    try:
        # Günlük getiriler
        daily_returns = data['Close'].pct_change().dropna()
        
        # Yıllık getiri
        total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
        days = (data.index[-1] - data.index[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1
        
        # Volatilite (yıllık)
        annual_volatility = daily_returns.std() * (252 ** 0.5)
        
        # Sharpe oranı (risk-free rate = 0 varsayımı)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0
        
        # Maximum düşüş
        cumulative_returns = (1 + daily_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        positive_days = (daily_returns > 0).sum()
        total_days = len(daily_returns)
        win_rate = positive_days / total_days if total_days > 0 else 0
        
        return {
            "Toplam Getiri": total_return * 100,
            "Yıllık Getiri": annual_return * 100,
            "Yıllık Volatilite": annual_volatility * 100,
            "Sharpe Oranı": sharpe_ratio,
            "Maksimum Düşüş": max_drawdown * 100,
            "Kazanma Oranı": win_rate * 100,
            "En İyi Gün": daily_returns.max() * 100,
            "En Kötü Gün": daily_returns.min() * 100
        }
    
    except Exception as e:
        st.error(f"Performans metrik hesaplama hatası: {str(e)}")
        return {}

def get_risk_level(volatility: float, beta: Optional[float] = None) -> str:
    """Risk seviyesi belirler"""
    risk_levels = {
        "Düşük": (0, 15),
        "Orta": (15, 25),
        "Yüksek": (25, 35),
        "Çok Yüksek": (35, float('inf'))
    }
    
    volatility_pct = volatility * 100 if volatility < 1 else volatility
    
    for level, (min_vol, max_vol) in risk_levels.items():
        if min_vol <= volatility_pct < max_vol:
            return level
    
    return "Bilinmiyor"

def get_trend_analysis(data: pd.DataFrame, short_period: int = 10, long_period: int = 50) -> dict:
    """Trend analizi yapar"""
    if len(data) < long_period:
        return {"trend": "Yetersiz Veri", "strength": 0}
    
    try:
        # Kısa ve uzun vadeli hareketli ortalamalar
        short_ma = data['Close'].rolling(window=short_period).mean()
        long_ma = data['Close'].rolling(window=long_period).mean()
        
        current_price = data['Close'].iloc[-1]
        short_ma_current = short_ma.iloc[-1]
        long_ma_current = long_ma.iloc[-1]
        
        # Trend yönü
        if current_price > short_ma_current > long_ma_current:
            trend = "Güçlü Yükseliş"
            strength = 3
        elif current_price > short_ma_current and short_ma_current > long_ma_current:
            trend = "Yükseliş"
            strength = 2
        elif short_ma_current > long_ma_current:
            trend = "Zayıf Yükseliş"
            strength = 1
        elif current_price < short_ma_current < long_ma_current:
            trend = "Güçlü Düşüş"
            strength = -3
        elif current_price < short_ma_current and short_ma_current < long_ma_current:
            trend = "Düşüş"
            strength = -2
        elif short_ma_current < long_ma_current:
            trend = "Zayıf Düşüş"
            strength = -1
        else:
            trend = "Yatay"
            strength = 0
        
        # Trend gücü (son 20 günlük değişim)
        if len(data) >= 20:
            price_change_20d = (current_price / data['Close'].iloc[-20] - 1) * 100
        else:
            price_change_20d = 0
        
        return {
            "trend": trend,
            "strength": strength,
            "price_change_20d": price_change_20d,
            "current_vs_short_ma": (current_price / short_ma_current - 1) * 100,
            "current_vs_long_ma": (current_price / long_ma_current - 1) * 100,
            "short_vs_long_ma": (short_ma_current / long_ma_current - 1) * 100
        }
    
    except Exception as e:
        st.error(f"Trend analizi hatası: {str(e)}")
        return {"trend": "Hata", "strength": 0}

def get_market_session_info() -> dict:
    """Piyasa seansı bilgilerini döndürür"""
    now = datetime.now()
    
    # BIST çalışma saatleri (Pazartesi-Cuma, 09:30-18:00)
    weekday = now.weekday()  # 0=Pazartesi, 6=Pazar
    current_time = now.time()
    
    market_open = datetime.strptime("09:30", "%H:%M").time()
    market_close = datetime.strptime("18:00", "%H:%M").time()
    
    is_weekday = weekday < 5  # Pazartesi-Cuma
    is_market_hours = market_open <= current_time <= market_close
    
    if is_weekday and is_market_hours:
        status = "Açık"
        next_session = "Bugün 18:00'de kapanacak"
    elif is_weekday and current_time < market_open:
        status = "Kapalı"
        next_session = "Bugün 09:30'da açılacak"
    elif is_weekday and current_time > market_close:
        status = "Kapalı"
        next_session = "Yarın 09:30'da açılacak"
    else:
        # Hafta sonu
        status = "Kapalı"
        days_until_monday = (7 - weekday) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_session = f"{days_until_monday} gün sonra Pazartesi 09:30'da açılacak"
    
    return {
        "status": status,
        "next_session": next_session,
        "is_open": status == "Açık",
        "current_time": get_turkish_date(now, include_time=True)
    }

def create_alert_system(data: pd.DataFrame, thresholds: dict) -> list:
    """Uyarı sistemi oluşturur"""
    alerts = []
    
    if data.empty:
        return alerts
    
    try:
        current_price = data['Close'].iloc[-1]
        
        # Fiyat uyarıları
        if 'price_upper' in thresholds and current_price > thresholds['price_upper']:
            alerts.append({
                "type": "warning",
                "message": f"Fiyat hedef seviyesini aştı: {format_currency(current_price)}"
            })
        
        if 'price_lower' in thresholds and current_price < thresholds['price_lower']:
            alerts.append({
                "type": "danger",
                "message": f"Fiyat destek seviyesini kırdı: {format_currency(current_price)}"
            })
        
        # Hacim uyarıları
        if len(data) > 1:
            avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            if current_volume > avg_volume * 2:
                alerts.append({
                    "type": "info",
                    "message": f"Yüksek hacim tespit edildi: {format_number(current_volume)}"
                })
        
        # Volatilite uyarıları
        if len(data) >= 20:
            daily_returns = data['Close'].pct_change().dropna()
            volatility = daily_returns.rolling(window=20).std().iloc[-1]
            
            if volatility > 0.03:  # %3'ten fazla günlük volatilite
                alerts.append({
                    "type": "warning",
                    "message": f"Yüksek volatilite: {format_percentage(volatility * 100)}"
                })
    
    except Exception as e:
        st.error(f"Uyarı sistemi hatası: {str(e)}")
    
    return alerts

def export_data_to_csv(data: pd.DataFrame, filename: str = None) -> str:
    """Verileri CSV formatına çevirir"""
    try:
        if filename is None:
            filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        csv_data = data.to_csv(index=True, encoding='utf-8-sig')
        return csv_data
        
    except Exception as e:
        st.error(f"CSV export hatası: {str(e)}")
        return ""

def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Veri temizleme işlemleri"""
    try:
        # Eksik değerleri temizle
        data = data.dropna()
        
        # Negatif fiyat değerlerini kontrol et
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if col in data.columns:
                data = data[data[col] > 0]
        
        # Volume negatif olamaz
        if 'Volume' in data.columns:
            data = data[data['Volume'] >= 0]
        
        # Aykırı değerleri kontrol et (IQR yöntemi)
        for col in price_columns:
            if col in data.columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Çok aşırı değerleri filtrele (çok konservativ)
                data = data[(data[col] >= lower_bound * 0.5) & (data[col] <= upper_bound * 2)]
        
        return data.sort_index()
        
    except Exception as e:
        st.error(f"Veri temizleme hatası: {str(e)}")
        return data
