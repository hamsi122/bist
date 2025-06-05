import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Optional
import streamlit as st

class ChartGenerator:
    """Grafik oluşturma sınıfı"""
    
    def __init__(self, stock_data: pd.DataFrame, technical_indicators: Dict):
        self.stock_data = stock_data
        self.technical_indicators = technical_indicators
        
        # Türkçe tema ayarları
        self.theme_colors = {
            'background': '#FFFFFF',
            'grid': '#E5E5E5',
            'text': '#2E2E2E',
            'up_color': '#26A69A',
            'down_color': '#EF5350',
            'volume_color': '#78909C',
            'ma_colors': ['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#B19CD9', '#C44569'],
            'indicator_colors': ['#3F51B5', '#E91E63', '#00BCD4', '#4CAF50', '#FF9800']
        }
    
    def create_price_chart(self, title: str) -> go.Figure:
        """Fiyat grafiği oluşturur"""
        fig = go.Figure()
        
        # Mum grafiği
        fig.add_trace(go.Candlestick(
            x=self.stock_data.index,
            open=self.stock_data['Open'],
            high=self.stock_data['High'],
            low=self.stock_data['Low'],
            close=self.stock_data['Close'],
            name="Fiyat",
            increasing_line_color=self.theme_colors['up_color'],
            decreasing_line_color=self.theme_colors['down_color']
        ))
        
        # Hareketli ortalamalar ekle
        ma_colors = self.theme_colors['ma_colors']
        color_idx = 0
        
        for indicator, data in self.technical_indicators.items():
            if indicator.startswith('MA') and not data.empty:
                period = indicator.replace('MA', '')
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data.values,
                    mode='lines',
                    name=f"{period} Günlük Ortalama",
                    line=dict(color=ma_colors[color_idx % len(ma_colors)], width=2),
                    opacity=0.8
                ))
                color_idx += 1
        
        # Bollinger Bands
        if 'BB_Upper' in self.technical_indicators and 'BB_Lower' in self.technical_indicators:
            upper_band = self.technical_indicators['BB_Upper']
            lower_band = self.technical_indicators['BB_Lower']
            middle_band = self.technical_indicators.get('BB_Middle')
            
            # Alt band
            fig.add_trace(go.Scatter(
                x=lower_band.index,
                y=lower_band.values,
                mode='lines',
                name='Bollinger Alt',
                line=dict(color='rgba(128, 128, 128, 0.3)', width=1),
                showlegend=False
            ))
            
            # Üst band ve aradaki alan
            fig.add_trace(go.Scatter(
                x=upper_band.index,
                y=upper_band.values,
                mode='lines',
                name='Bollinger Bantları',
                line=dict(color='rgba(128, 128, 128, 0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)'
            ))
            
            # Orta band
            if middle_band is not None:
                fig.add_trace(go.Scatter(
                    x=middle_band.index,
                    y=middle_band.values,
                    mode='lines',
                    name='Bollinger Orta',
                    line=dict(color='rgba(128, 128, 128, 0.5)', width=1, dash='dash')
                ))
        
        # Grafik düzeni
        fig.update_layout(
            title=f"📈 {title} - Fiyat Grafiği",
            xaxis_title="Tarih",
            yaxis_title="Fiyat (₺)",
            template="plotly_white",
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type="date"
            )
        )
        
        return fig
    
    def create_technical_chart(self, title: str) -> go.Figure:
        """Teknik indikatör grafiği oluşturur"""
        # Alt grafikli yapı oluştur
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Fiyat ve Hareketli Ortalamalar', 'RSI', 'MACD', 'Stochastic'),
            row_heights=[0.5, 0.2, 0.2, 0.1]
        )
        
        # 1. Alt grafik: Fiyat ve MA
        fig.add_trace(go.Candlestick(
            x=self.stock_data.index,
            open=self.stock_data['Open'],
            high=self.stock_data['High'],
            low=self.stock_data['Low'],
            close=self.stock_data['Close'],
            name="Fiyat",
            increasing_line_color=self.theme_colors['up_color'],
            decreasing_line_color=self.theme_colors['down_color']
        ), row=1, col=1)
        
        # Hareketli ortalamalar
        ma_colors = self.theme_colors['ma_colors']
        color_idx = 0
        
        for indicator, data in self.technical_indicators.items():
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
        
        # 2. Alt grafik: RSI
        if 'RSI' in self.technical_indicators:
            rsi_data = self.technical_indicators['RSI']
            fig.add_trace(go.Scatter(
                x=rsi_data.index,
                y=rsi_data.values,
                mode='lines',
                name='RSI',
                line=dict(color=self.theme_colors['indicator_colors'][0], width=2)
            ), row=2, col=1)
            
            # RSI seviye çizgileri
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
        
        # 3. Alt grafik: MACD
        if 'MACD' in self.technical_indicators and 'Signal' in self.technical_indicators:
            macd_data = self.technical_indicators['MACD']
            signal_data = self.technical_indicators['Signal']
            
            fig.add_trace(go.Scatter(
                x=macd_data.index,
                y=macd_data.values,
                mode='lines',
                name='MACD',
                line=dict(color=self.theme_colors['indicator_colors'][1], width=2)
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=signal_data.index,
                y=signal_data.values,
                mode='lines',
                name='Signal',
                line=dict(color=self.theme_colors['indicator_colors'][2], width=2)
            ), row=3, col=1)
            
            # MACD Histogram
            if 'Histogram' in self.technical_indicators:
                histogram_data = self.technical_indicators['Histogram']
                colors = ['green' if val >= 0 else 'red' for val in histogram_data.values]
                
                fig.add_trace(go.Bar(
                    x=histogram_data.index,
                    y=histogram_data.values,
                    name='MACD Histogram',
                    marker_color=colors,
                    opacity=0.6
                ), row=3, col=1)
        
        # 4. Alt grafik: Stochastic
        if 'Stoch_K' in self.technical_indicators and 'Stoch_D' in self.technical_indicators:
            stoch_k = self.technical_indicators['Stoch_K']
            stoch_d = self.technical_indicators['Stoch_D']
            
            fig.add_trace(go.Scatter(
                x=stoch_k.index,
                y=stoch_k.values,
                mode='lines',
                name='Stoch %K',
                line=dict(color=self.theme_colors['indicator_colors'][3], width=2)
            ), row=4, col=1)
            
            fig.add_trace(go.Scatter(
                x=stoch_d.index,
                y=stoch_d.values,
                mode='lines',
                name='Stoch %D',
                line=dict(color=self.theme_colors['indicator_colors'][4], width=2)
            ), row=4, col=1)
            
            # Stochastic seviye çizgileri
            fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5, row=4, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5, row=4, col=1)
        
        # Grafik düzeni
        fig.update_layout(
            title=f"🔧 {title} - Teknik İndikatörler",
            height=800,
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
        
        # Y ekseni etiketleri
        fig.update_yaxes(title_text="Fiyat (₺)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Stochastic", row=4, col=1, range=[0, 100])
        fig.update_xaxes(title_text="Tarih", row=4, col=1)
        
        return fig
    
    def create_volume_chart(self, title: str) -> go.Figure:
        """Hacim analiz grafiği oluşturur"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Fiyat', 'Hacim Analizi'),
            row_heights=[0.7, 0.3]
        )
        
        # Fiyat grafiği
        fig.add_trace(go.Candlestick(
            x=self.stock_data.index,
            open=self.stock_data['Open'],
            high=self.stock_data['High'],
            low=self.stock_data['Low'],
            close=self.stock_data['Close'],
            name="Fiyat",
            increasing_line_color=self.theme_colors['up_color'],
            decreasing_line_color=self.theme_colors['down_color']
        ), row=1, col=1)
        
        # Hacim çubuk grafiği
        colors = []
        for i in range(len(self.stock_data)):
            if i == 0:
                colors.append(self.theme_colors['volume_color'])
            else:
                if self.stock_data['Close'].iloc[i] >= self.stock_data['Close'].iloc[i-1]:
                    colors.append(self.theme_colors['up_color'])
                else:
                    colors.append(self.theme_colors['down_color'])
        
        fig.add_trace(go.Bar(
            x=self.stock_data.index,
            y=self.stock_data['Volume'],
            name='Hacim',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)
        
        # Hacim hareketli ortalaması
        if 'Volume_MA' in self.technical_indicators:
            volume_ma = self.technical_indicators['Volume_MA']
            fig.add_trace(go.Scatter(
                x=volume_ma.index,
                y=volume_ma.values,
                mode='lines',
                name='Hacim MA(20)',
                line=dict(color='orange', width=2)
            ), row=2, col=1)
        
        # OBV indikatörü varsa ekle
        if 'OBV' in self.technical_indicators:
            # OBV için üçüncü bir alt grafik oluşturabiliriz
            pass
        
        fig.update_layout(
            title=f"📊 {title} - Hacim Analizi",
            height=600,
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
        
        fig.update_yaxes(title_text="Fiyat (₺)", row=1, col=1)
        fig.update_yaxes(title_text="Hacim", row=2, col=1)
        fig.update_xaxes(title_text="Tarih", row=2, col=1)
        
        return fig
    
    def create_comparison_chart(self, comparison_data: Dict[str, pd.DataFrame], title: str) -> go.Figure:
        """Karşılaştırma grafiği oluşturur"""
        fig = go.Figure()
        
        colors = self.theme_colors['indicator_colors']
        
        for i, (symbol, data) in enumerate(comparison_data.items()):
            if not data.empty:
                # Normalize et (ilk değere göre yüzde değişim)
                normalized_data = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=normalized_data,
                    mode='lines',
                    name=symbol.replace('.IS', ''),
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        fig.update_layout(
            title=f"📊 {title} - Performans Karşılaştırması",
            xaxis_title="Tarih",
            yaxis_title="Değişim (%)",
            template="plotly_white",
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Sıfır çizgisi ekle
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    def create_sector_analysis_chart(self, sector_data: Dict) -> go.Figure:
        """Sektör analizi grafiği oluşturur"""
        if not sector_data:
            return go.Figure()
        
        symbols = list(sector_data.keys())
        pe_ratios = [data.get('P/E', 0) for data in sector_data.values()]
        market_caps = [data.get('Piyasa Değeri', 0) for data in sector_data.values()]
        
        # Bubble chart oluştur
        fig = go.Figure(data=go.Scatter(
            x=pe_ratios,
            y=[data.get('ROE', 0) for data in sector_data.values()],
            mode='markers+text',
            text=[symbol.replace('.IS', '') for symbol in symbols],
            textposition="top center",
            marker=dict(
                size=[cap/1e9 if cap else 5 for cap in market_caps],  # Piyasa değerine göre boyut
                color=pe_ratios,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="P/E Oranı"),
                sizemode='diameter',
                sizeref=2.*max([cap/1e9 if cap else 1 for cap in market_caps])/(40.**2),
                sizemin=4
            )
        ))
        
        fig.update_layout(
            title="🏭 Sektör Analizi - P/E vs ROE",
            xaxis_title="P/E Oranı",
            yaxis_title="ROE (%)",
            template="plotly_white",
            height=500
        )
        
        return fig
