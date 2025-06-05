import yfinance as yf
import pandas as pd
from typing import Dict, Optional
import streamlit as st

class FundamentalAnalysis:
    """Temel analiz hesaplamaları için sınıf"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    @st.cache_data(ttl=3600)  # 1 saat cache
    def get_fundamental_metrics(_self) -> Dict:
        """Temel analiz metriklerini getirir"""
        try:
            info = _self.ticker.info
            
            metrics = {
                "Piyasa Değeri": info.get("marketCap"),
                "P/E Oranı": info.get("trailingPE"),
                "P/B Oranı": info.get("priceToBook"),
                "Temettü Verimi": info.get("dividendYield"),
                "Beta": info.get("beta"),
                "ROE (%)": info.get("returnOnEquity"),
                "ROA (%)": info.get("returnOnAssets"),
                "Borç/Özkaynak": info.get("debtToEquity"),
                "Cari Oran": info.get("currentRatio"),
                "Hızlı Oran": info.get("quickRatio"),
                "Brüt Kar Marjı (%)": info.get("grossMargins"),
                "EBITDA Marjı (%)": info.get("ebitdaMargins"),
                "Net Kar Marjı (%)": info.get("profitMargins"),
                "Hisse Başı Kazanç": info.get("trailingEps"),
                "Gelecek Yıl EPS": info.get("forwardEps"),
                "PEG Oranı": info.get("pegRatio"),
                "52 Hafta En Yüksek": info.get("fiftyTwoWeekHigh"),
                "52 Hafta En Düşük": info.get("fiftyTwoWeekLow"),
                "Ortalama Hacim": info.get("averageVolume"),
                "Piyasa Değeri/Gelir": info.get("priceToSalesTrailing12Months"),
                "Kurumsal Değer": info.get("enterpriseValue"),
                "KD/EBITDA": info.get("enterpriseToEbitda"),
                "Nakit ve Nakit Benzerleri": info.get("totalCash"),
                "Toplam Borç": info.get("totalDebt"),
                "Serbest Nakit Akışı": info.get("freeCashflow"),
                "Operasyonel Nakit Akışı": info.get("operatingCashflow")
            }
            
            # None değerleri filtrele ve formatla
            formatted_metrics = {}
            for key, value in metrics.items():
                if value is not None:
                    formatted_metrics[key] = value
            
            return formatted_metrics
            
        except Exception as e:
            st.error(f"Temel analiz hatası ({_self.symbol}): {str(e)}")
            return {}
    
    @st.cache_data(ttl=3600)
    def get_financial_statements(_self) -> Dict:
        """Mali tablolar bilgilerini getirir"""
        try:
            financial_data = {}
            
            # Gelir tablosu
            try:
                income_stmt = _self.ticker.financials
                if not income_stmt.empty:
                    financial_data['income_statement'] = income_stmt
            except:
                pass
            
            # Bilanço
            try:
                balance_sheet = _self.ticker.balance_sheet
                if not balance_sheet.empty:
                    financial_data['balance_sheet'] = balance_sheet
            except:
                pass
            
            # Nakit akış tablosu
            try:
                cashflow = _self.ticker.cashflow
                if not cashflow.empty:
                    financial_data['cashflow'] = cashflow
            except:
                pass
            
            return financial_data
            
        except Exception as e:
            st.error(f"Mali tablo hatası ({_self.symbol}): {str(e)}")
            return {}
    
    def calculate_financial_ratios(self, financial_data: Dict) -> Dict:
        """Mali oranları hesaplar"""
        ratios = {}
        
        try:
            if 'income_statement' in financial_data and 'balance_sheet' in financial_data:
                income_stmt = financial_data['income_statement']
                balance_sheet = financial_data['balance_sheet']
                
                # En son yıl verilerini al
                if not income_stmt.empty and not balance_sheet.empty:
                    latest_year = income_stmt.columns[0]
                    
                    # Temel oranlar
                    total_revenue = income_stmt.loc['Total Revenue', latest_year] if 'Total Revenue' in income_stmt.index else None
                    net_income = income_stmt.loc['Net Income', latest_year] if 'Net Income' in income_stmt.index else None
                    total_assets = balance_sheet.loc['Total Assets', latest_year] if 'Total Assets' in balance_sheet.index else None
                    total_equity = balance_sheet.loc['Total Stockholder Equity', latest_year] if 'Total Stockholder Equity' in balance_sheet.index else None
                    
                    if total_revenue and net_income:
                        ratios['Net Kar Marjı'] = (net_income / total_revenue) * 100
                    
                    if net_income and total_assets:
                        ratios['ROA'] = (net_income / total_assets) * 100
                    
                    if net_income and total_equity:
                        ratios['ROE'] = (net_income / total_equity) * 100
                    
                    # Diğer hesaplamalar...
                    
        except Exception as e:
            st.error(f"Oran hesaplama hatası: {str(e)}")
        
        return ratios
    
    def get_peer_comparison(self, sector_symbols: list) -> Dict:
        """Sektör karşılaştırması yapar"""
        try:
            comparison_data = {}
            
            for symbol in sector_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    comparison_data[symbol] = {
                        'P/E': info.get('trailingPE'),
                        'P/B': info.get('priceToBook'),
                        'ROE': info.get('returnOnEquity'),
                        'Piyasa Değeri': info.get('marketCap')
                    }
                except:
                    continue
            
            return comparison_data
            
        except Exception as e:
            st.error(f"Sektör karşılaştırma hatası: {str(e)}")
            return {}
    
    def calculate_intrinsic_value(self) -> Optional[float]:
        """İçsel değer tahmini yapar (DCF yöntemi ile basit)"""
        try:
            info = self.ticker.info
            
            # Gerekli veriler
            free_cashflow = info.get('freeCashflow')
            shares_outstanding = info.get('sharesOutstanding')
            
            if not free_cashflow or not shares_outstanding:
                return None
            
            # Basit DCF hesaplaması (varsayımsal büyüme oranları ile)
            growth_rate = 0.05  # %5 büyüme varsayımı
            discount_rate = 0.10  # %10 iskonto oranı
            terminal_growth = 0.03  # %3 terminal büyüme
            
            # 5 yıllık projeksiyon
            projected_fcf = []
            for year in range(1, 6):
                fcf = free_cashflow * ((1 + growth_rate) ** year)
                pv_fcf = fcf / ((1 + discount_rate) ** year)
                projected_fcf.append(pv_fcf)
            
            # Terminal değer
            terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            pv_terminal = terminal_value / ((1 + discount_rate) ** 5)
            
            # Toplam değer
            total_value = sum(projected_fcf) + pv_terminal
            intrinsic_value_per_share = total_value / shares_outstanding
            
            return intrinsic_value_per_share
            
        except Exception as e:
            st.error(f"İçsel değer hesaplama hatası: {str(e)}")
            return None
    
    def get_dividend_analysis(self) -> Dict:
        """Temettü analizi yapar"""
        try:
            info = self.ticker.info
            dividends = self.ticker.dividends
            
            dividend_data = {
                "Temettü Verimi": info.get('dividendYield'),
                "Temettü Oranı": info.get('payoutRatio'),
                "Son Temettü": info.get('lastDividendValue'),
                "Temettü Tarihi": info.get('dividendDate'),
                "5 Yıllık Temettü Büyümesi": None
            }
            
            # Son 5 yıl temettü büyümesi hesapla
            if not dividends.empty and len(dividends) >= 2:
                recent_dividends = dividends.tail(5)
                if len(recent_dividends) >= 2:
                    first_dividend = recent_dividends.iloc[0]
                    last_dividend = recent_dividends.iloc[-1]
                    years = len(recent_dividends) - 1
                    
                    if first_dividend > 0 and years > 0:
                        growth_rate = ((last_dividend / first_dividend) ** (1/years)) - 1
                        dividend_data["5 Yıllık Temettü Büyümesi"] = growth_rate * 100
            
            return dividend_data
            
        except Exception as e:
            st.error(f"Temettü analizi hatası: {str(e)}")
            return {}
    
    def get_valuation_summary(self) -> Dict:
        """Değerleme özeti"""
        try:
            fundamentals = self.get_fundamental_metrics()
            intrinsic_value = self.calculate_intrinsic_value()
            
            # Mevcut fiyat
            hist = self.ticker.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            
            valuation = {
                "Mevcut Fiyat": current_price,
                "İçsel Değer Tahmini": intrinsic_value,
                "P/E Oranı": fundamentals.get("P/E Oranı"),
                "P/B Oranı": fundamentals.get("P/B Oranı"),
                "PEG Oranı": fundamentals.get("PEG Oranı")
            }
            
            # Değerleme yorumu
            if current_price and intrinsic_value:
                if current_price < intrinsic_value * 0.9:
                    valuation["Değerleme"] = "Düşük Değerli"
                elif current_price > intrinsic_value * 1.1:
                    valuation["Değerleme"] = "Yüksek Değerli"
                else:
                    valuation["Değerleme"] = "Adil Değerli"
            
            return valuation
            
        except Exception as e:
            st.error(f"Değerleme özeti hatası: {str(e)}")
            return {}
