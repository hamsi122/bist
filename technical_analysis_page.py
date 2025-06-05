import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import DataFetcher
from technical_analysis import TechnicalAnalysis
from chart_generator import ChartGenerator
from utils import format_currency, format_percentage

def show_technical_analysis_page():
    """Detaylı teknik analiz sayfası"""
    st.title("🔧 Detaylı Teknik Analiz")
    st.markdown("---")
    
    # Sidebar'dan şirket seçimi
    data_fetcher = DataFetcher()
    bist100_companies = data_fetcher.get_bist100_companies()
    
    # Şirket seçimi
    company_options = [f"{company['symbol']} - {company['name']}" for company in bist100_companies]
    selected_company_display = st.selectbox("Şirket Seçin", company_options)
    selected_symbol = selected_company_display.split(" - ")[0]
    
    # Seçilen şirketi bul
    selected_company = next(c for c in bist100_companies if c['symbol'] == selected_symbol)
    
    # Zaman aralığı
    time_period = st.selectbox(
        "Zaman Aralığı",
        ["1ay", "3ay", "6ay", "1yıl", "2yıl"],
        index=2
    )
    
    period_map = {
        "1ay": "1mo",
        "3ay": "3mo", 
        "6ay": "6mo",
        "1yıl": "1y",
        "2yıl": "2y"
    }
    
    # Veri çek
    with st.spinner("Veriler yükleniyor..."):
        stock_data = data_fetcher.get_stock_data(selected_symbol, period_map[time_period])
    
    if stock_data is None or stock_data.empty:
        st.error(f"❌ {selected_symbol} için veri alınamadı.")
        return
    
    # Teknik analiz hesapla
    tech_analysis = TechnicalAnalysis(stock_data)
    tech_indicators = tech_analysis.calculate_all_indicators()
    trading_signals = tech_analysis.get_trading_signals()
    
    # Ana grafik - Fiyat ve indikatörler
    st.subheader(f"📊 {selected_company['name']} - Kapsamlı Teknik Analiz")
    
    # Çoklu grafik oluştur
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(
            'Fiyat, Hareketli Ortalamalar ve Bollinger Bantları',
            'RSI (Relative Strength Index)',
            'MACD',
            'Stochastic Oscillator',
            'Hacim ve Williams %R'
        ),
        row_heights=[0.4, 0.15, 0.15, 0.15, 0.15]
    )
    
    # 1. Fiyat grafiği
    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'],
        high=stock_data['High'],
        low=stock_data['Low'],
        close=stock_data['Close'],
        name="Fiyat",
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ), row=1, col=1)
    
    # Hareketli ortalamalar
    ma_colors = ['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#B19CD9']
    color_idx = 0
    
    for indicator, data in tech_indicators.items():
        if indicator.startswith('MA') and len(data) > 0:
            period = indicator.replace('MA', '')
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data.values,
                mode='lines',
                name=f"MA{period}",
                line=dict(color=ma_colors[color_idx % len(ma_colors)], width=2)
            ), row=1, col=1)
            color_idx += 1
    
    # Bollinger Bands
    if 'BB_Upper' in tech_indicators and 'BB_Lower' in tech_indicators:
        upper_band = tech_indicators['BB_Upper']
        lower_band = tech_indicators['BB_Lower']
        middle_band = tech_indicators.get('BB_Middle')
        
        fig.add_trace(go.Scatter(
            x=lower_band.index,
            y=lower_band.values,
            mode='lines',
            name='BB Alt',
            line=dict(color='rgba(128, 128, 128, 0.3)', width=1),
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=upper_band.index,
            y=upper_band.values,
            mode='lines',
            name='Bollinger Bantları',
            line=dict(color='rgba(128, 128, 128, 0.3)', width=1),
            fill='tonexty',
            fillcolor='rgba(128, 128, 128, 0.1)'
        ), row=1, col=1)
        
        if middle_band is not None:
            fig.add_trace(go.Scatter(
                x=middle_band.index,
                y=middle_band.values,
                mode='lines',
                name='BB Orta',
                line=dict(color='rgba(128, 128, 128, 0.5)', width=1, dash='dash'),
                showlegend=False
            ), row=1, col=1)
    
    # 2. RSI
    if 'RSI' in tech_indicators:
        rsi_data = tech_indicators['RSI']
        fig.add_trace(go.Scatter(
            x=rsi_data.index,
            y=rsi_data.values,
            mode='lines',
            name='RSI',
            line=dict(color='#3F51B5', width=2)
        ), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
    
    # 3. MACD
    if 'MACD' in tech_indicators and 'Signal' in tech_indicators:
        macd_data = tech_indicators['MACD']
        signal_data = tech_indicators['Signal']
        
        fig.add_trace(go.Scatter(
            x=macd_data.index,
            y=macd_data.values,
            mode='lines',
            name='MACD',
            line=dict(color='#E91E63', width=2)
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=signal_data.index,
            y=signal_data.values,
            mode='lines',
            name='Signal',
            line=dict(color='#00BCD4', width=2)
        ), row=3, col=1)
        
        if 'Histogram' in tech_indicators:
            histogram_data = tech_indicators['Histogram']
            colors = ['green' if val >= 0 else 'red' for val in histogram_data.values]
            
            fig.add_trace(go.Bar(
                x=histogram_data.index,
                y=histogram_data.values,
                name='MACD Histogram',
                marker_color=colors,
                opacity=0.6
            ), row=3, col=1)
    
    # 4. Stochastic
    if 'Stoch_K' in tech_indicators and 'Stoch_D' in tech_indicators:
        stoch_k = tech_indicators['Stoch_K']
        stoch_d = tech_indicators['Stoch_D']
        
        fig.add_trace(go.Scatter(
            x=stoch_k.index,
            y=stoch_k.values,
            mode='lines',
            name='Stoch %K',
            line=dict(color='#4CAF50', width=2)
        ), row=4, col=1)
        
        fig.add_trace(go.Scatter(
            x=stoch_d.index,
            y=stoch_d.values,
            mode='lines',
            name='Stoch %D',
            line=dict(color='#FF9800', width=2)
        ), row=4, col=1)
        
        fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5, row=4, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5, row=4, col=1)
    
    # 5. Hacim ve Williams %R
    # Hacim
    colors = []
    for i in range(len(stock_data)):
        if i == 0:
            colors.append('#78909C')
        else:
            if stock_data['Close'].iloc[i] >= stock_data['Close'].iloc[i-1]:
                colors.append('#26A69A')
            else:
                colors.append('#EF5350')
    
    fig.add_trace(go.Bar(
        x=stock_data.index,
        y=stock_data['Volume'],
        name='Hacim',
        marker_color=colors,
        opacity=0.7,
        yaxis='y5'
    ), row=5, col=1)
    
    # Williams %R (ikinci y ekseni)
    if 'Williams_R' in tech_indicators:
        williams_r = tech_indicators['Williams_R']
        fig.add_trace(go.Scatter(
            x=williams_r.index,
            y=williams_r.values,
            mode='lines',
            name='Williams %R',
            line=dict(color='purple', width=2),
            yaxis='y6'
        ), row=5, col=1)
    
    # Layout güncelle
    fig.update_layout(
        title=f"🔧 {selected_company['name']} - Kapsamlı Teknik Analiz",
        height=1000,
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Y ekseni başlıkları
    fig.update_yaxes(title_text="Fiyat (₺)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Stochastic", row=4, col=1, range=[0, 100])
    fig.update_yaxes(title_text="Hacim", row=5, col=1)
    fig.update_xaxes(title_text="Tarih", row=5, col=1)
    
    # İkinci y ekseni Williams %R için
    fig.update_layout(
        yaxis6=dict(
            title="Williams %R",
            overlaying="y5",
            side="right",
            range=[-100, 0]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Teknik analiz özeti
    st.markdown("---")
    st.subheader("📊 Teknik Analiz Özeti")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("🎯 Al/Sat Sinyalleri")
        for signal_name, signal_value in trading_signals.items():
            color = "🟢" if signal_value == "Al" else "🔴" if signal_value == "Sat" else "🟡"
            st.write(f"{color} **{signal_name}:** {signal_value}")
    
    with col2:
        st.subheader("📈 Mevcut Değerler")
        if 'RSI' in tech_indicators:
            current_rsi = tech_indicators['RSI'].iloc[-1]
            st.write(f"**RSI:** {current_rsi:.2f}")
            
        if 'MACD' in tech_indicators:
            current_macd = tech_indicators['MACD'].iloc[-1]
            st.write(f"**MACD:** {current_macd:.4f}")
            
        if 'Williams_R' in tech_indicators:
            current_williams = tech_indicators['Williams_R'].iloc[-1]
            st.write(f"**Williams %R:** {current_williams:.2f}")
    
    with col3:
        st.subheader("📊 Bollinger Bantları")
        if 'BB_Upper' in tech_indicators:
            current_price = stock_data['Close'].iloc[-1]
            bb_upper = tech_indicators['BB_Upper'].iloc[-1]
            bb_lower = tech_indicators['BB_Lower'].iloc[-1]
            bb_middle = tech_indicators['BB_Middle'].iloc[-1]
            
            st.write(f"**Üst Band:** {bb_upper:.2f} ₺")
            st.write(f"**Orta Band:** {bb_middle:.2f} ₺")
            st.write(f"**Alt Band:** {bb_lower:.2f} ₺")
            
            if current_price > bb_upper:
                st.error("🔴 Aşırı alım")
            elif current_price < bb_lower:
                st.success("🟢 Aşırı satım")
            else:
                st.info("🟡 Normal")
    
    with col4:
        st.subheader("⚡ Momentum")
        if 'Stoch_K' in tech_indicators:
            stoch_k_current = tech_indicators['Stoch_K'].iloc[-1]
            st.write(f"**Stoch %K:** {stoch_k_current:.2f}")
            
        if 'CCI' in tech_indicators:
            cci_current = tech_indicators['CCI'].iloc[-1]
            st.write(f"**CCI:** {cci_current:.2f}")
            
        if 'ATR' in tech_indicators:
            atr_current = tech_indicators['ATR'].iloc[-1]
            st.write(f"**ATR:** {atr_current:.2f}")

if __name__ == "__main__":
    show_technical_analysis_page()