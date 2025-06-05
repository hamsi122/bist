import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional

class DataFetcher:
    """BIST 100 hisse senedi verilerini çeken sınıf"""
    
    def __init__(self):
        self.bist100_symbols = [
            # BIST 100 şirketleri - İstanbul Stock Exchange symbols
            "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS", "EKGYO.IS",
            "EREGL.IS", "FROTO.IS", "GARAN.IS", "HALKB.IS", "ISCTR.IS",
            "KCHOL.IS", "KOZAL.IS", "PETKM.IS", "SAHOL.IS", "SISE.IS",
            "TEKFEN.IS", "THYAO.IS", "TOASO.IS", "TUPRS.IS", "VAKBN.IS",
            "YKBNK.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS",
            "AKSA.IS", "ALARK.IS", "ALBRK.IS", "ALCAR.IS", "ALGYO.IS",
            "ALKIM.IS", "ALMAD.IS", "ANACM.IS", "ANADM.IS", "ANHYT.IS",
            "ANSGR.IS", "ARANT.IS", "ARSAN.IS", "ASGYO.IS", "ASUZU.IS",
            "AVOD.IS", "AYDEM.IS", "AYGAZ.IS", "BAGFS.IS", "BAHKM.IS",
            "BAKAB.IS", "BANVT.IS", "BARMA.IS", "BERA.IS", "BIENY.IS",
            "BIGCH.IS", "BINHO.IS", "BIOEN.IS", "BIZIM.IS", "BLCYT.IS",
            "BOBET.IS", "BORLS.IS", "BRISA.IS", "BRKSN.IS", "BRKVY.IS",
            "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "CEMTS.IS",
            "CCOLA.IS", "CEMAS.IS", "CEMTS.IS", "CIMSA.IS", "CLEBI.IS",
            "CMENT.IS", "CMBTN.IS", "COBET.IS", "CRDFA.IS", "CRFSA.IS",
            "CWENE.IS", "DENGE.IS", "DESA.IS", "DEVA.IS", "DGNMO.IS",
            "DIRIT.IS", "DOAS.IS", "DOCO.IS", "DOGUB.IS", "DOHOL.IS",
            "DURDO.IS", "DYOBY.IS", "ECILC.IS", "EDATA.IS", "EGEEN.IS",
            "EGGUB.IS", "EGSER.IS", "ENERY.IS", "ENKAI.IS", "ENTEK.IS",
            "EPLAS.IS", "ESGYO.IS", "EUPWR.IS", "EYGYO.IS", "FENER.IS",
            "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "GEDIK.IS",
            "GEDZA.IS", "GENIL.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS",
            "GIMAT.IS", "GINKO.IS", "GLYHO.IS", "GMTAS.IS", "GOODY.IS",
            "GOZDE.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HATEK.IS",
            "HDFGS.IS", "HEDEF.IS", "HEKTS.IS", "HURGZ.IS", "ICBCT.IS",
            "IDGYO.IS", "IEYHO.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS",
            "IHLGM.IS", "IHYAY.IS", "IMASM.IS", "INDES.IS", "INFO.IS",
            "INTEM.IS", "INVEO.IS", "ISGYO.IS", "ISKUR.IS", "ISMEN.IS",
            "ITTFH.IS", "IZFAS.IS", "JANTS.IS", "KAPLM.IS", "KARTN.IS",
            "KAYSE.IS", "KBORU.IS", "KCAER.IS", "KENT.IS", "KERVT.IS",
            "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLNMA.IS", "KLRHO.IS",
            "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "KONKA.IS", "KONTR.IS",
            "KONYA.IS", "KORDS.IS", "KOZAA.IS", "KRDMA.IS", "KRDMB.IS",
            "KRDMD.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS",
            "KRVGD.IS", "KSTUR.IS", "KTLEV.IS", "KTSKR.IS", "KUTPO.IS",
            "KZBGY.IS", "LIDER.IS", "LIDFA.IS", "LINK.IS", "LKMNH.IS",
            "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MACKO.IS", "MAGEN.IS",
            "MAKIM.IS", "MAKTK.IS", "MARBL.IS", "MAVI.IS", "MEDTR.IS",
            "MEGAP.IS", "MEPET.IS", "MERCN.IS", "MERIT.IS", "MERKO.IS",
            "METRO.IS", "MGROS.IS", "MHRGY.IS", "MIGRS.IS", "MIPAZ.IS",
            "MOBTL.IS", "MOGAN.IS", "MPARK.IS", "MRGYO.IS", "MRSHL.IS",
            "MSGYO.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS", "NETAS.IS",
            "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "ODAS.IS",
            "ONRYT.IS", "ORCAY.IS", "ORGE.IS", "ORMA.IS", "OSTIM.IS",
            "OTKAR.IS", "OYAKC.IS", "OYLUM.IS", "OZBAL.IS", "OZBBC.IS",
            "OZGYO.IS", "OZKGY.IS", "OZRDN.IS", "OZSUB.IS", "PAMEL.IS",
            "PAPIL.IS", "PARSN.IS", "PASEU.IS", "PATEK.IS", "PCILT.IS",
            "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS",
            "PGSUS.IS", "PINSU.IS", "PKART.IS", "PKENT.IS", "PLTUR.IS",
            "POLTK.IS", "PRDGS.IS", "PRKAB.IS", "PRKME.IS", "PRZMA.IS",
            "PSDTC.IS", "QUAGR.IS", "RALYH.IS", "RAYSG.IS", "REEDR.IS",
            "RGYAS.IS", "RHEXP.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS",
            "RUBNS.IS", "RYSAS.IS", "SAHOL.IS", "SANEL.IS", "SANFM.IS",
            "SANKO.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS",
            "SEGYO.IS", "SELEC.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS",
            "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS",
            "SMRTG.IS", "SNGYO.IS", "SNKRN.IS", "SNPAM.IS", "SODSN.IS",
            "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS",
            "SUWEN.IS", "TABGD.IS", "TARK.IS", "TATEN.IS", "TAVHL.IS",
            "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTU.IS", "TEMPZ.IS",
            "TETMT.IS", "TEZOL.IS", "THYAO.IS", "TIRE.IS", "TKFEN.IS",
            "TKNSA.IS", "TLMAN.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS",
            "TRCAS.IS", "TRGYO.IS", "TRILC.IS", "TSGYO.IS", "TSKB.IS",
            "TTKOM.IS", "TTRAK.IS", "TUKAS.IS", "TUPRS.IS", "TURSG.IS",
            "UFUK.IS", "ULKER.IS", "ULUUN.IS", "UNLU.IS", "USAK.IS",
            "UZERB.IS", "VAKBN.IS", "VAKFN.IS", "VANGD.IS", "VBTYZ.IS",
            "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKING.IS", "VKGYO.IS",
            "YAPRK.IS", "YATAS.IS", "YEOTK.IS", "YESIL.IS", "YGGYO.IS",
            "YGYO.IS", "YKBNK.IS", "YONGA.IS", "YUNSA.IS", "ZEDUR.IS",
            "ZOREN.IS", "ZRGYO.IS"
        ]
        
        # Şirket bilgileri ve sektörleri
        self.company_info = {
            "AKBNK.IS": {"name": "Akbank T.A.Ş.", "sector": "Bankacılık"},
            "ARCLK.IS": {"name": "Arçelik A.Ş.", "sector": "Dayanıklı Tüketim"},
            "ASELS.IS": {"name": "Aselsan Elektronik San. ve Tic. A.Ş.", "sector": "Savunma"},
            "BIMAS.IS": {"name": "BİM Birleşik Mağazalar A.Ş.", "sector": "Perakende"},
            "EKGYO.IS": {"name": "Emlak Konut GYO A.Ş.", "sector": "Gayrimenkul"},
            "EREGL.IS": {"name": "Ereğli Demir ve Çelik Fab. T.A.Ş.", "sector": "Çelik"},
            "FROTO.IS": {"name": "Ford Otomotiv Sanayi A.Ş.", "sector": "Otomotiv"},
            "GARAN.IS": {"name": "Türkiye Garanti Bankası A.Ş.", "sector": "Bankacılık"},
            "HALKB.IS": {"name": "Türkiye Halk Bankası A.Ş.", "sector": "Bankacılık"},
            "ISCTR.IS": {"name": "Türkiye İş Bankası A.Ş.", "sector": "Bankacılık"},
            "KCHOL.IS": {"name": "Koç Holding A.Ş.", "sector": "Holding"},
            "PETKM.IS": {"name": "Petkim Petrokimya Holding A.Ş.", "sector": "Petrokimya"},
            "SAHOL.IS": {"name": "Hacı Ömer Sabancı Holding A.Ş.", "sector": "Holding"},
            "SISE.IS": {"name": "Türkiye Şişe ve Cam Fab. A.Ş.", "sector": "Cam"},
            "THYAO.IS": {"name": "Türk Hava Yolları A.O.", "sector": "Havayolu"},
            "TOASO.IS": {"name": "Tofaş Türk Otomobil Fab. A.Ş.", "sector": "Otomotiv"},
            "TUPRS.IS": {"name": "Tüpraş-Türkiye Petrol Raf. A.Ş.", "sector": "Enerji"},
            "VAKBN.IS": {"name": "Türkiye Vakıflar Bankası T.A.O.", "sector": "Bankacılık"},
            "YKBNK.IS": {"name": "Yapı ve Kredi Bankası A.Ş.", "sector": "Bankacılık"},
            # Diğer şirketler için varsayılan bilgiler
        }
    
    def get_bist100_companies(self) -> List[Dict]:
        """BIST 100 şirketleri listesini döndürür"""
        companies = []
        
        for symbol in self.bist100_symbols:
            company_data = self.company_info.get(symbol, {
                "name": symbol.replace(".IS", ""),
                "sector": "Diğer"
            })
            
            companies.append({
                "symbol": symbol,
                "name": company_data["name"],
                "sector": company_data["sector"]
            })
        
        return companies
    
    @st.cache_data(ttl=300)  # 5 dakika cache
    def get_stock_data(_self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Belirli bir hisse senedinin verilerini çeker"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
            
            # Sadece gerekli kolonları seç ve yeniden adlandır
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            available_columns = data.columns.tolist()
            
            # Mevcut kolonları kontrol et ve uygun olanları seç
            column_mapping = {}
            for col in required_columns:
                if col in available_columns:
                    column_mapping[col] = col
                elif col.lower() in [c.lower() for c in available_columns]:
                    # Büyük/küçük harf duyarsız eşleştirme
                    for ac in available_columns:
                        if ac.lower() == col.lower():
                            column_mapping[ac] = col
                            break
            
            # Eğer Dividends ve Stock Splits varsa kaldır
            columns_to_keep = []
            for col in available_columns:
                if col in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']:
                    columns_to_keep.append(col)
            
            # Sadece gerekli kolonları al
            if columns_to_keep:
                data = data[columns_to_keep]
            
            # Adj Close varsa Close ile değiştir
            if 'Adj Close' in data.columns and 'Close' not in data.columns:
                data['Close'] = data['Adj Close']
                data = data.drop(columns=['Adj Close'])
            elif 'Adj Close' in data.columns and 'Close' in data.columns:
                # Adj Close'u kaldır, Close'u kullan
                data = data.drop(columns=['Adj Close'])
            
            # Gerekli kolonları kontrol et
            final_required = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in final_required if col not in data.columns]
            
            if missing_columns:
                st.warning(f"Eksik kolonlar ({symbol}): {missing_columns}")
                return None
            
            # Sadece gerekli kolonları al ve DataFrame olarak döndür
            result_data = data[final_required].copy()
            
            return result_data
            
        except Exception as e:
            st.error(f"Veri çekme hatası ({symbol}): {str(e)}")
            return None
    
    @st.cache_data(ttl=600)  # 10 dakika cache
    def get_market_summary(_self) -> Optional[Dict]:
        """Piyasa özetini getirir"""
        try:
            # BIST 100 endeks verisi
            bist100 = yf.Ticker("XU100.IS")
            bist100_data = bist100.history(period="2d")
            
            if bist100_data.empty:
                return None
            
            # En çok yükselen ve düşenleri bulmak için örnek şirketlerden veri çek
            sample_symbols = ["AKBNK.IS", "GARAN.IS", "ISCTR.IS", "VAKBN.IS", "YKBNK.IS",
                            "THYAO.IS", "BIMAS.IS", "ARCLK.IS", "TUPRS.IS", "EREGL.IS"]
            
            gainers = []
            losers = []
            
            for symbol in sample_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="2d")
                    
                    if len(data) >= 2:
                        current_price = data['Close'].iloc[-1]
                        prev_price = data['Close'].iloc[-2]
                        change_pct = ((current_price - prev_price) / prev_price) * 100
                        
                        company_name = _self.company_info.get(symbol, {}).get("name", symbol)
                        
                        stock_info = {
                            "Sembol": symbol.replace(".IS", ""),
                            "Şirket": company_name,
                            "Fiyat": f"{current_price:.2f} ₺",
                            "Değişim": f"{change_pct:+.2f}%"
                        }
                        
                        if change_pct > 0:
                            gainers.append(stock_info)
                        else:
                            losers.append(stock_info)
                            
                except Exception:
                    continue
            
            # En çok değişenleri sırala
            gainers.sort(key=lambda x: float(x["Değişim"].replace("%", "").replace("+", "")), reverse=True)
            losers.sort(key=lambda x: float(x["Değişim"].replace("%", "").replace("+", "")))
            
            return {
                "top_gainers": gainers[:5],
                "top_losers": losers[:5],
                "bist100_change": bist100_data
            }
        
        except Exception as e:
            st.error(f"Piyasa özeti hatası: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)  # 1 saat cache
    def get_company_info(_self, symbol: str) -> Optional[Dict]:
        """Şirket temel bilgilerini getirir"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "shares_outstanding": info.get("sharesOutstanding")
            }
            
        except Exception as e:
            st.error(f"Şirket bilgisi hatası ({symbol}): {str(e)}")
            return None
