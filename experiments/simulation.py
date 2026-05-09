# -*- coding: utf-8 -*-
"""
Simulasyon Modulu
==================
Bulanik cikarim sistemini buyuk olcekli veri uzerinde calistirir.
Gercek graf verisini sentetik verilerle birlestirerek 
risk tahminleri uretir.
"""

import os
import sys
import numpy as np
import pandas as pd
import time

# Windows konsol encoding duzeltmesi
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from fuzzy_system.inference import BulanikCikarimSistemi
from utils.preprocessing import tam_veri_hatti_calistir
from utils.data_loader import veriyi_kaydet, ISENMIS_VERI_DIZINI, dizinleri_olustur


def simulasyon_calistir(ornek_sayisi=1000, fonksiyon_tipi='karisik', 
                        graf_entegre=True, rastgele_tohum=42):
    """
    Tam simulasyonu calistirir.
    """
    print("\n" + "#" * 60)
    print("     SIMULASYON MOTORU BASLATILIYOR")
    print("#" * 60)
    
    baslangic = time.time()
    dizinleri_olustur()
    
    # ADIM 1: Veri Hazirlama
    print("\n-- ADIM 1: Veri Hazirlama --")
    df = tam_veri_hatti_calistir(
        ornek_sayisi=ornek_sayisi,
        graf_entegre=graf_entegre,
        rastgele_tohum=rastgele_tohum
    )
    
    # ADIM 2: Bulanik Sistem Kurulumu
    print("\n-- ADIM 2: Bulanik Sistem Kurulumu --")
    fis = BulanikCikarimSistemi(fonksiyon_tipi)
    
    # ADIM 3: Risk Hesaplama
    print("\n-- ADIM 3: Risk Hesaplama --")
    riskler = fis.toplu_hesapla(df)
    
    df['risk_seviyesi'] = np.round(riskler, 4)
    
    df['risk_kategorisi'] = pd.cut(
        df['risk_seviyesi'],
        bins=[0, 0.35, 0.65, 1.0],
        labels=['Dusuk', 'Orta', 'Yuksek'],
        include_lowest=True
    )
    
    # ADIM 4: Sonuclari Kaydet
    print("\n-- ADIM 4: Sonuclari Kaydetme --")
    veriyi_kaydet(df, "simulasyon_sonuclari.csv")
    
    # ADIM 5: Ozet Rapor
    sure = time.time() - baslangic
    
    print("\n" + "=" * 60)
    print("     SIMULASYON SONUC RAPORU")
    print("=" * 60)
    print(f"\n  Toplam ornek sayisi    : {len(df)}")
    print(f"  Calisma suresi         : {sure:.1f} saniye")
    print(f"  Uyelik fonksiyonu tipi : {fonksiyon_tipi}")
    print(f"  Graf entegrasyonu     : {'Evet' if graf_entegre else 'Hayir'}")
    
    print(f"\n  Risk Istatistikleri:")
    print(f"  ---------------------")
    print(f"  Minimum risk  : {riskler.min():.4f}")
    print(f"  Maksimum risk : {riskler.max():.4f}")
    print(f"  Ortalama risk : {riskler.mean():.4f}")
    print(f"  Std sapma     : {riskler.std():.4f}")
    print(f"  Medyan risk   : {np.median(riskler):.4f}")
    
    print(f"\n  Risk Dagilimi:")
    print(f"  ---------------")
    kategori_sayilari = df['risk_kategorisi'].value_counts()
    for kat in ['Dusuk', 'Orta', 'Yuksek']:
        sayi = kategori_sayilari.get(kat, 0)
        oran = sayi / len(df) * 100
        bar = '#' * int(oran / 2)
        print(f"  {kat:7s}: {sayi:4d} ({oran:5.1f}%) {bar}")
    
    print("\n" + "#" * 60)
    print("     SIMULASYON TAMAMLANDI")
    print("#" * 60 + "\n")
    
    return df, fis


def senaryo_testleri(fis):
    """
    Onceden tanimlanmis senaryolar uzerinde test calistirir.
    """
    print("\n" + "=" * 60)
    print("SENARYO TESTLERI")
    print("=" * 60)
    
    senaryolar = [
        {'ad': 'Guvenilir Akademisyen', 'guven': 0.95, 'paylasim': 3, 'duygu': 0.05, 'merkezlilik': 0.3},
        {'ad': 'Aktif Haber Kaynagi', 'guven': 0.8, 'paylasim': 40, 'duygu': 0.2, 'merkezlilik': 0.9},
        {'ad': 'Supheli Bot Hesap', 'guven': 0.05, 'paylasim': 48, 'duygu': 0.9, 'merkezlilik': 0.4},
        {'ad': 'Duygusal Aktivist', 'guven': 0.4, 'paylasim': 25, 'duygu': 0.85, 'merkezlilik': 0.6},
        {'ad': 'Sessiz Gozlemci', 'guven': 0.6, 'paylasim': 1, 'duygu': 0.1, 'merkezlilik': 0.15},
        {'ad': 'Etkileyici Trol', 'guven': 0.1, 'paylasim': 35, 'duygu': 0.75, 'merkezlilik': 0.85},
        {'ad': 'Ortalama Kullanici', 'guven': 0.5, 'paylasim': 10, 'duygu': 0.3, 'merkezlilik': 0.5},
        {'ad': 'Yasli Kullanici', 'guven': 0.7, 'paylasim': 2, 'duygu': 0.15, 'merkezlilik': 0.2},
        {'ad': 'Viral Icerik Uretici', 'guven': 0.3, 'paylasim': 45, 'duygu': 0.6, 'merkezlilik': 0.75},
        {'ad': 'Komplo Teorisyeni', 'guven': 0.1, 'paylasim': 30, 'duygu': 0.95, 'merkezlilik': 0.5},
    ]
    
    sonuclar = []
    for s in senaryolar:
        risk = fis.hesapla(s['guven'], s['paylasim'], s['duygu'], s['merkezlilik'])
        
        if risk < 0.35:
            kategori = '[DUSUK]'
        elif risk < 0.65:
            kategori = '[ORTA]'
        else:
            kategori = '[YUKSEK]'
        
        sonuclar.append({
            'Senaryo': s['ad'],
            'Guven': s['guven'],
            'Paylasim': s['paylasim'],
            'Duygu': s['duygu'],
            'Merkezlilik': s['merkezlilik'],
            'Risk': round(risk, 4),
            'Kategori': kategori
        })
        
        print(f"  {s['ad']:25s}: Risk = {risk:.4f} {kategori}")
    
    df_sonuclar = pd.DataFrame(sonuclar)
    print("\n" + "=" * 60)
    
    return df_sonuclar


if __name__ == "__main__":
    df_sonuclar, fis = simulasyon_calistir(ornek_sayisi=1000)
    senaryo_testleri(fis)
    print("\n[TEST] Simulasyon modulu basariyla calisti!")
