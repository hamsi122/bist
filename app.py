import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

from data_fetcher import DataFetcher
from technical_analysis import TechnicalAnalysis
from fundamental_analysis import FundamentalAnalysis
from chart_generator import ChartGenerator
from utils import format_currency, format_percentage, get_turkish_date
from technical_analysis_page import show_technical_analysis_page

# Sayfa yapılandırması
st.set_page_config(
    page_title="BIST 100 Hisse Analizi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Başlık
st.title("📈 BIST 100 Hisse Senedi Analizi")

# Navigasyon menüsü
page = st.selectbox(
    "Sayfa Seçin:",
    ["Ana Sayfa", "Detaylı Teknik Analiz", "Temel Analiz", "Piyasa Özeti"],
    index=0
)

if page == "Detaylı Teknik Analiz":
    show_technical_analysis_page()
    st.stop()

st.markdown("---")

# Veri çekici sınıfını başlat
@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

data_fetcher = get_data_fetcher()

# Sidebar - Şirket seçimi
st.sidebar.title("🏢 Şirket Seçimi")

# BIST 100 şirketleri listesini al
with st.spinner("BIST 100 şirketleri yükleniyor..."):
    bist100_companies = data_fetcher.get_bist100_companies()

if not bist100_companies:
    st.error("❌ BIST 100 şirket listesi yüklenemedi. Lütfen daha sonra tekrar deneyin.")
    st.stop()

# Sektör filtresi
sectors = sorted(list(set([company['sector'] for company in bist100_companies if company.get('sector')])))
selected_sector = st.sidebar.selectbox(
    "🏭 Sektör Filtresi",
    ["Tümü"] + sectors,
    index=0
)

# Şirketleri filtrele
filtered_companies = bist100_companies
if selected_sector != "Tümü":
    filtered_companies = [c for c in bist100_companies if c.get('sector') == selected_sector]

# Şirket arama
search_term = st.sidebar.text_input("🔍 Şirket Ara", "")
if search_term:
    filtered_companies = [
        c for c in filtered_companies 
        if search_term.lower() in c['name'].lower() or search_term.lower() in c['symbol'].lower()
    ]

# Şirket seçimi
company_options = [f"{company['symbol']} - {company['name']}" for company in filtered_companies]
if not company_options:
    st.sidebar.warning("⚠️ Arama kriterlerinize uygun şirket bulunamadı.")
    st.stop()

selected_company_display = st.sidebar.selectbox("Şirket Seçin", company_options)
selected_symbol = selected_company_display.split(" - ")[0]

# Seçilen şirketi bul
selected_company = next(c for c in filtered_companies if c['symbol'] == selected_symbol)

# Zaman aralığı seçimi
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Zaman Aralığı")
time_period = st.sidebar.selectbox(
    "Dönem Seçin",
    ["1ay", "3ay", "6ay", "1yıl", "2yıl", "5yıl"],
    index=3
)

period_map = {
    "1ay": "1mo",
    "3ay": "3mo", 
    "6ay": "6mo",
    "1yıl": "1y",
    "2yıl": "2y",
    "5yıl": "5y"
}

# Ana içerik alanı
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"📊 {selected_company['name']} ({selected_company['symbol']})")
    
    # Hisse senedi verilerini al
    with st.spinner("Hisse senedi verileri yükleniyor..."):
        stock_data = data_fetcher.get_stock_data(selected_symbol, period_map[time_period])
    
    if stock_data is None or stock_data.empty:
        st.error(f"❌ {selected_symbol} için veri alınamadı.")
    else:
        # Güncel fiyat bilgileri
        current_price = stock_data['Close'].iloc[-1]
        prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        # Fiyat kartları
        price_col1, price_col2, price_col3, price_col4 = st.columns(4)
        
        with price_col1:
            st.metric(
                "💰 Güncel Fiyat",
                format_currency(current_price),
                f"{format_currency(price_change)} ({format_percentage(price_change_pct)})"
            )
        
        with price_col2:
            st.metric("📈 En Yüksek", format_currency(stock_data['High'].max()))
        
        with price_col3:
            st.metric("📉 En Düşük", format_currency(stock_data['Low'].min()))
        
        with price_col4:
            avg_volume = stock_data['Volume'].mean()
            st.metric("📊 Ort. Hacim", f"{avg_volume:,.0f}")

        # Teknik analiz hesapla
        tech_analysis = TechnicalAnalysis(stock_data)
        tech_indicators = tech_analysis.calculate_all_indicators()
        
        # Grafik oluştur
        chart_gen = ChartGenerator(stock_data, tech_indicators)
        
        # Grafik seçenekleri
        chart_tabs = st.tabs(["📈 Fiyat Grafiği", "🔧 Teknik Analiz", "📊 Hacim Analizi", "📋 Detaylı Teknik"])
        
        with chart_tabs[0]:
            st.subheader("Fiyat Grafiği ve Hareketli Ortalamalar")
            fig = chart_gen.create_price_chart(selected_company['name'])
            st.plotly_chart(fig, use_container_width=True)
            
        with chart_tabs[1]:
            st.subheader("Teknik İndikatörler Analizi")
            fig = chart_gen.create_technical_chart(selected_company['name'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Teknik analiz sinyalleri
            trading_signals = tech_analysis.get_trading_signals()
            st.subheader("📊 Al/Sat Sinyalleri")
            
            signal_cols = st.columns(4)
            with signal_cols[0]:
                rsi_signal = trading_signals.get("RSI_Signal", "Nötr")
                color = "🟢" if rsi_signal == "Al" else "🔴" if rsi_signal == "Sat" else "🟡"
                st.metric(f"{color} RSI Sinyali", rsi_signal)
                
            with signal_cols[1]:
                macd_signal = trading_signals.get("MACD_Signal", "Nötr")
                color = "🟢" if macd_signal == "Al" else "🔴" if macd_signal == "Sat" else "🟡"
                st.metric(f"{color} MACD Sinyali", macd_signal)
                
            with signal_cols[2]:
                ma_signal = trading_signals.get("MA_Signal", "Nötr")
                color = "🟢" if ma_signal == "Al" else "🔴" if ma_signal == "Sat" else "🟡"
                st.metric(f"{color} MA Sinyali", ma_signal)
                
            with signal_cols[3]:
                overall_signal = trading_signals.get("Overall_Signal", "Nötr")
                color = "🟢" if overall_signal == "Al" else "🔴" if overall_signal == "Sat" else "🟡"
                st.metric(f"{color} Genel Sinyal", overall_signal)
            
        with chart_tabs[2]:
            st.subheader("Hacim Analizi")
            fig = chart_gen.create_volume_chart(selected_company['name'])
            st.plotly_chart(fig, use_container_width=True)
            
        with chart_tabs[3]:
            st.subheader("Detaylı Teknik İndikatörler")
            
            # RSI detayları
            if 'RSI' in tech_indicators:
                current_rsi = tech_indicators['RSI'].iloc[-1]
                st.write(f"**RSI (14 dönem):** {current_rsi:.2f}")
                if current_rsi < 30:
                    st.success("🟢 RSI aşırı satım bölgesinde - Al sinyali")
                elif current_rsi > 70:
                    st.error("🔴 RSI aşırı alım bölgesinde - Sat sinyali")
                else:
                    st.info("🟡 RSI nötr bölgede")
            
            # MACD detayları
            if 'MACD' in tech_indicators and 'Signal' in tech_indicators:
                current_macd = tech_indicators['MACD'].iloc[-1]
                current_signal = tech_indicators['Signal'].iloc[-1]
                st.write(f"**MACD:** {current_macd:.4f}")
                st.write(f"**MACD Signal:** {current_signal:.4f}")
                if current_macd > current_signal:
                    st.success("🟢 MACD pozitif - Yükseliş trendi")
                else:
                    st.error("🔴 MACD negatif - Düşüş trendi")
            
            # Bollinger Bands
            if 'BB_Upper' in tech_indicators and 'BB_Lower' in tech_indicators:
                current_price = stock_data['Close'].iloc[-1]
                bb_upper = tech_indicators['BB_Upper'].iloc[-1]
                bb_lower = tech_indicators['BB_Lower'].iloc[-1]
                bb_middle = tech_indicators['BB_Middle'].iloc[-1]
                
                st.write(f"**Bollinger Bantları:**")
                st.write(f"- Üst Band: {bb_upper:.2f} ₺")
                st.write(f"- Orta Band: {bb_middle:.2f} ₺")
                st.write(f"- Alt Band: {bb_lower:.2f} ₺")
                
                if current_price > bb_upper:
                    st.error("🔴 Fiyat üst bandın üzerinde - Aşırı alım")
                elif current_price < bb_lower:
                    st.success("🟢 Fiyat alt bandın altında - Aşırı satım")
                else:
                    st.info("🟡 Fiyat bantlar arasında - Normal")
            
            # Williams %R
            if 'Williams_R' in tech_indicators:
                williams_r = tech_indicators['Williams_R'].iloc[-1]
                st.write(f"**Williams %R:** {williams_r:.2f}")
                if williams_r < -80:
                    st.success("🟢 Aşırı satım bölgesi")
                elif williams_r > -20:
                    st.error("🔴 Aşırı alım bölgesi")
                else:
                    st.info("🟡 Normal bölge")

with col2:
    st.subheader("📋 Şirket Bilgileri")
    
    # Şirket temel bilgileri
    if selected_company.get('sector'):
        st.info(f"🏭 **Sektör:** {selected_company['sector']}")
    
    # Kompakt teknik indikatörler özeti
    st.subheader("🔧 Teknik İndikatörler")
    
    if tech_indicators:
        if 'RSI' in tech_indicators and not tech_indicators['RSI'].empty:
            rsi_value = tech_indicators['RSI'].iloc[-1]
            color = "🟢" if 30 <= rsi_value <= 70 else "🔴"
            st.metric(f"{color} RSI", f"{rsi_value:.1f}")
        
        if 'MACD' in tech_indicators and not tech_indicators['MACD'].empty:
            macd_value = tech_indicators['MACD'].iloc[-1]
            st.metric("📈 MACD", f"{macd_value:.4f}")
            
        if 'MA20' in tech_indicators and not tech_indicators['MA20'].empty:
            ma20_value = tech_indicators['MA20'].iloc[-1]
            st.metric("📊 MA20", format_currency(float(ma20_value)))
    else:
        st.info("Hesaplanıyor...")
    
    # Al/Sat sinyali
    if stock_data is not None and not stock_data.empty:
        trading_signals = tech_analysis.get_trading_signals()
        overall_signal = trading_signals.get("Overall_Signal", "Nötr")
        signal_color = "🟢" if overall_signal == "Al" else "🔴" if overall_signal == "Sat" else "🟡"
        st.metric(f"{signal_color} Genel Sinyal", overall_signal)

# Detaylı Temel Analiz Bölümü (Grafiklerin altında)
if stock_data is not None and not stock_data.empty:
    st.markdown("---")
    st.subheader("💼 Detaylı Temel Analiz")
    
    with st.spinner("Temel analiz verileri yükleniyor..."):
        fundamental_analysis = FundamentalAnalysis(selected_symbol)
        fundamental_data = fundamental_analysis.get_fundamental_metrics()
        valuation_summary = fundamental_analysis.get_valuation_summary()
    
    if fundamental_data:
        # Temel metrikler 3 kolon halinde
        fund_col1, fund_col2, fund_col3 = st.columns(3)
        
        with fund_col1:
            st.subheader("📈 Karlılık Oranları")
            profitability_metrics = {k: v for k, v in fundamental_data.items() 
                                   if any(word in k.lower() for word in ['margin', 'roe', 'roa', 'profit'])}
            
            for key, value in profitability_metrics.items():
                if value is not None:
                    if isinstance(value, (int, float)):
                        if 'margin' in key.lower() or 'roe' in key.lower() or 'roa' in key.lower():
                            st.metric(key, f"{value*100:.1f}%" if value < 1 else f"{value:.1f}%")
                        else:
                            st.metric(key, f"{value:.2f}")
                    else:
                        st.metric(key, str(value))
        
        with fund_col2:
            st.subheader("💰 Değerleme Oranları")
            valuation_metrics = {k: v for k, v in fundamental_data.items() 
                                if any(word in k.lower() for word in ['p/e', 'p/b', 'peg', 'price', 'ratio'])}
            
            for key, value in valuation_metrics.items():
                if value is not None:
                    if isinstance(value, (int, float)):
                        st.metric(key, f"{value:.2f}")
                    else:
                        st.metric(key, str(value))
        
        with fund_col3:
            st.subheader("🏦 Mali Durum")
            financial_metrics = {k: v for k, v in fundamental_data.items() 
                                if any(word in k.lower() for word in ['debt', 'cash', 'current', 'quick', 'beta'])}
            
            for key, value in financial_metrics.items():
                if value is not None:
                    if isinstance(value, (int, float)):
                        if 'cash' in key.lower() and value > 1000000:
                            st.metric(key, f"{value/1000000:.1f}M ₺")
                        elif 'ratio' in key.lower() or 'beta' in key.lower():
                            st.metric(key, f"{value:.2f}")
                        else:
                            st.metric(key, f"{value:.2f}")
                    else:
                        st.metric(key, str(value))
    
    # Değerleme özeti
    if valuation_summary:
        st.subheader("🎯 Değerleme Özeti")
        val_col1, val_col2, val_col3 = st.columns(3)
        
        with val_col1:
            current_price = valuation_summary.get("Mevcut Fiyat")
            if current_price:
                st.metric("Mevcut Fiyat", f"{current_price:.2f} ₺")
        
        with val_col2:
            intrinsic_value = valuation_summary.get("İçsel Değer Tahmini")
            if intrinsic_value:
                st.metric("İçsel Değer", f"{intrinsic_value:.2f} ₺")
        
        with val_col3:
            valuation_status = valuation_summary.get("Değerleme", "Bilinmiyor")
            color = "🟢" if valuation_status == "Düşük Değerli" else "🔴" if valuation_status == "Yüksek Değerli" else "🟡"
            st.metric(f"{color} Değerleme", valuation_status)

# Alt kısım - BIST 100 özeti
st.markdown("---")
st.subheader("📊 BIST 100 Piyasa Özeti")

# BIST 100 genel durumu
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔝 En Çok Yükselen")
    with st.spinner("Piyasa verileri yükleniyor..."):
        market_summary = data_fetcher.get_market_summary()
    
    if market_summary and 'top_gainers' in market_summary:
        gainers_df = pd.DataFrame(market_summary['top_gainers'])
        if not gainers_df.empty:
            st.dataframe(gainers_df, use_container_width=True)
        else:
            st.info("Veri bulunamadı")
    else:
        st.info("Piyasa özeti şu anda kullanılamıyor")

with col2:
    st.subheader("🔻 En Çok Düşenler")
    if market_summary and 'top_losers' in market_summary:
        losers_df = pd.DataFrame(market_summary['top_losers'])
        if not losers_df.empty:
            st.dataframe(losers_df, use_container_width=True)
        else:
            st.info("Veri bulunamadı")
    else:
        st.info("Piyasa özeti şu anda kullanılamıyor")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        📈 BIST 100 Hisse Analizi - Gerçek zamanlı piyasa verileri ile güçlendirilmiştir<br>
        Son güncelleme: {}
    </div>
    """.format(get_turkish_date(datetime.now())),
    unsafe_allow_html=True
)

# Otomatik yenileme
if st.sidebar.button("🔄 Verileri Yenile"):
    st.cache_resource.clear()
    st.rerun()

# Veri ihracı
if st.sidebar.button("📊 Verileri İndir"):
    if stock_data is not None and not stock_data.empty:
        csv = stock_data.to_csv()
        st.sidebar.download_button(
            label="CSV İndir",
            data=csv,
            file_name=f"{selected_symbol}_analiz_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
