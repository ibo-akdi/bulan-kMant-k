# -*- coding: utf-8 -*-
"""
Ana Giris Noktasi
===================
Sosyal Aglarda Yanlis Bilgi Riskinin Bulanik Mantik ile Modellenmesi

Bu dosya calistirildiginda tum boru hatti otomatik olarak calisir:
1. Veri seti yuklenir ve olusturulur
2. Bulanik cikarim sistemi kurulur
3. Simulasyon calistirilir (1000+ ornek)
4. Duyarlilik analizi yapilir
5. Karsilastirma deneyi calistirilir
6. Tum grafikler uretilir
7. Sonuclar kaydedilir

Kullanim
--------
    python main.py              # Tam pipeline
    python main.py --sadece-sim # Sadece simulasyon
    python main.py --sadece-grs # Sadece grafikler
    streamlit run gui/app.py    # GUI baslat
"""

import os
import sys
import time
import argparse

# Windows konsol encoding duzeltmesi
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Proje kok dizinini Python path'e ekle
PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJE_DIZINI)


def tam_pipeline_calistir(ornek_sayisi=1000, fonksiyon_tipi='karisik', graf_entegre=True):
    """
    Tam veri isleme hattini calistirir.
    
    Parametreler
    ------------
    ornek_sayisi : int
        Sentetik veri ornek sayisi.
    fonksiyon_tipi : str
        Uyelik fonksiyonu tipi: 'ucgensel', 'yamuksal', 'karisik'
    graf_entegre : bool
        Facebook graf verisi kullanilsin mi.
    """
    from experiments.simulation import simulasyon_calistir, senaryo_testleri
    from experiments.sensitivity import duyarlilik_raporu
    from experiments.comparison import karsilastirma_deneyi_calistir
    from visualization.plots import tum_grafikleri_uret
    
    baslangic = time.time()
    
    print("\n")
    print("+--------------------------------------------------------------+")
    print("|                                                              |")
    print("|   Sosyal Aglarda Yanlis Bilgi Riskinin                       |")
    print("|   Bulanik Mantik ile Modellenmesi                            |")
    print("|                                                              |")
    print("|   Mamdani Tipi Bulanik Cikarim Sistemi                       |")
    print("|                                                              |")
    print("+--------------------------------------------------------------+")
    print()
    
    # ========================================
    # ASAMA 1: Simulasyon
    # ========================================
    print("\n>> ASAMA 1/4: SIMULASYON")
    print("-" * 50)
    df_sonuclar, fis = simulasyon_calistir(
        ornek_sayisi=ornek_sayisi,
        fonksiyon_tipi=fonksiyon_tipi,
        graf_entegre=graf_entegre
    )
    
    # Senaryo testleri
    print("\n>> SENARYO TESTLERI")
    print("-" * 50)
    senaryo_testleri(fis)
    
    # ========================================
    # ASAMA 2: Duyarlilik Analizi
    # ========================================
    print("\n>> ASAMA 2/4: DUYARLILIK ANALIZI")
    print("-" * 50)
    rapor = duyarlilik_raporu(fis)
    
    # ========================================
    # ASAMA 3: Model Karsilastirmasi
    # ========================================
    print("\n>> ASAMA 3/4: MODEL KARSILASTIRMASI")
    print("-" * 50)
    karsilastirma = karsilastirma_deneyi_calistir(df=df_sonuclar, fonksiyon_tipi=fonksiyon_tipi)
    
    # ========================================
    # ASAMA 4: Gorsellestirme
    # ========================================
    print("\n>> ASAMA 4/4: GORSELLESTIRME")
    print("-" * 50)
    tum_grafikleri_uret(
        fis=fis,
        risk_degerleri=df_sonuclar['risk_seviyesi'].values,
        bulanik_riskler=karsilastirma['bulanik_riskler'],
        temel_riskler=karsilastirma['temel_riskler'],
        metrikler=karsilastirma['metrikler']
    )
    
    # ========================================
    # SONUC RAPORU
    # ========================================
    toplam_sure = time.time() - baslangic
    
    print("\n")
    print("+--------------------------------------------------------------+")
    print("|                    CALISMA TAMAMLANDI                        |")
    print("+--------------------------------------------------------------+")
    print(f"|  Toplam sure          : {toplam_sure:6.1f} saniye                        |")
    print(f"|  Ornek sayisi         : {ornek_sayisi:6d}                                |")
    print(f"|  Uyelik fonksiyonu    : {fonksiyon_tipi:10s}                          |")
    print(f"|  Kural sayisi         : {len(fis.kurallar):6d}                                |")
    print("|                                                              |")
    print("|  Cikti Dosyalari:                                            |")
    print("|  > data/processed/sentetik_veri.csv                          |")
    print("|  > data/processed/simulasyon_sonuclari.csv                   |")
    print("|  > data/processed/karsilastirma_sonuclari.csv                |")
    print("|  > visualization/output/*.png                                |")
    print("|                                                              |")
    print("|  GUI baslatmak icin:                                         |")
    print("|  > streamlit run gui/app.py                                  |")
    print("+--------------------------------------------------------------+")
    print()
    
    return {
        'df_sonuclar': df_sonuclar,
        'fis': fis,
        'karsilastirma': karsilastirma,
        'duyarlilik_raporu': rapor
    }


def sadece_simulasyon(ornek_sayisi=1000, fonksiyon_tipi='karisik', graf_entegre=True):
    """Sadece simulasyonu calistirir."""
    from experiments.simulation import simulasyon_calistir, senaryo_testleri
    df, fis = simulasyon_calistir(ornek_sayisi, fonksiyon_tipi, graf_entegre)
    senaryo_testleri(fis)
    return df, fis


def sadece_grafikler():
    """Sadece grafikleri uretir (mevcut verilerden)."""
    from fuzzy_system.inference import BulanikCikarimSistemi
    from utils.data_loader import islenmis_veri_yukle
    from visualization.plots import tum_grafikleri_uret
    
    fis = BulanikCikarimSistemi('karisik')
    
    try:
        df = islenmis_veri_yukle("simulasyon_sonuclari.csv")
        risk_degerleri = df['risk_seviyesi'].values if 'risk_seviyesi' in df.columns else None
    except FileNotFoundError:
        risk_degerleri = None
        df = None
    
    tum_grafikleri_uret(fis=fis, risk_degerleri=risk_degerleri)


def main():
    """Ana fonksiyon - komut satiri argumanlarini isler."""
    parser = argparse.ArgumentParser(
        description='Sosyal Aglarda Yanlis Bilgi Riskinin Bulanik Mantik ile Modellenmesi',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--ornek-sayisi', type=int, default=1000,
                       help='Sentetik veri ornek sayisi (varsayilan: 1000)')
    parser.add_argument('--fonksiyon-tipi', type=str, default='karisik',
                       choices=['ucgensel', 'yamuksal', 'karisik'],
                       help='Uyelik fonksiyonu tipi (varsayilan: karisik)')
    parser.add_argument('--graf-yok', action='store_true',
                       help='Facebook graf entegrasyonu yapma')
    parser.add_argument('--sadece-sim', action='store_true',
                       help='Sadece simulasyonu calistir')
    parser.add_argument('--sadece-grs', action='store_true',
                       help='Sadece grafikleri uret')
    
    args = parser.parse_args()
    
    if args.sadece_sim:
        sadece_simulasyon(args.ornek_sayisi, args.fonksiyon_tipi, not args.graf_yok)
    elif args.sadece_grs:
        sadece_grafikler()
    else:
        tam_pipeline_calistir(args.ornek_sayisi, args.fonksiyon_tipi, not args.graf_yok)


if __name__ == "__main__":
    main()
