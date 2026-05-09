# -*- coding: utf-8 -*-
"""
Duyarlilik Analizi Modulu
==========================
Her giris degiskeninin risk ciktisi uzerindeki etkisini analiz eder.
"""

import sys
import numpy as np
import pandas as pd
import os

# Windows konsol encoding duzeltmesi
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from fuzzy_system.inference import BulanikCikarimSistemi
from visualization.plots import duyarlilik_grafikleri, CIKTI_DIZINI


def tek_degisken_duyarliligi(fis, degisken='guven', aralik=None, 
                              n_nokta=100, sabit_degerler=None):
    """Tek bir degiskenin etkisini analiz eder."""
    if sabit_degerler is None:
        sabit_degerler = {
            'guven': 0.5, 'paylasim': 20,
            'duygu': 0.3, 'merkezlilik': 0.5
        }
    
    varsayilan_araliklar = {
        'guven': (0, 1),
        'paylasim': (0, 50),
        'duygu': (-1, 1),
        'merkezlilik': (0, 1)
    }
    
    if aralik is None:
        aralik = varsayilan_araliklar[degisken]
    
    x_degerleri = np.linspace(aralik[0], aralik[1], n_nokta)
    risk_degerleri = []
    
    for x in x_degerleri:
        degerler = sabit_degerler.copy()
        degerler[degisken] = x
        
        risk = fis.hesapla(
            guven=degerler['guven'],
            paylasim=degerler['paylasim'],
            duygu=degerler['duygu'],
            merkezlilik=degerler['merkezlilik']
        )
        risk_degerleri.append(risk)
    
    df = pd.DataFrame({
        degisken: x_degerleri,
        'risk': risk_degerleri
    })
    
    return df


def coklu_duyarlilik_analizi(fis, n_nokta=50):
    """Tum degisken ciftleri icin duyarlilik analizi yapar."""
    print("\n[DUYARLILIK] Coklu duyarlilik analizi basliyor...")
    
    degiskenler = ['guven', 'paylasim', 'duygu', 'merkezlilik']
    araliklar = {
        'guven': (0, 1),
        'paylasim': (0, 50),
        'duygu': (-1, 1),
        'merkezlilik': (0, 1)
    }
    sabit = {'guven': 0.5, 'paylasim': 20, 'duygu': 0.3, 'merkezlilik': 0.5}
    
    sonuclar = {}
    
    for i, d1 in enumerate(degiskenler):
        for j, d2 in enumerate(degiskenler):
            if j <= i:
                continue
            
            print(f"  Analiz: {d1} vs {d2}...")
            x = np.linspace(araliklar[d1][0], araliklar[d1][1], n_nokta)
            y = np.linspace(araliklar[d2][0], araliklar[d2][1], n_nokta)
            Z = np.zeros((n_nokta, n_nokta))
            
            for xi in range(n_nokta):
                for yi in range(n_nokta):
                    degerler = sabit.copy()
                    degerler[d1] = x[xi]
                    degerler[d2] = y[yi]
                    
                    Z[yi, xi] = fis.hesapla(
                        guven=degerler['guven'],
                        paylasim=degerler['paylasim'],
                        duygu=degerler['duygu'],
                        merkezlilik=degerler['merkezlilik']
                    )
            
            sonuclar[f'{d1}_vs_{d2}'] = {
                'x': x, 'y': y, 'Z': Z,
                'd1': d1, 'd2': d2
            }
    
    print(f"[DUYARLILIK] Coklu analiz tamamlandi: {len(sonuclar)} cift")
    return sonuclar


def duyarlilik_raporu(fis, kaydet_dizini=None):
    """Tam duyarlilik analizi raporu uretir."""
    if kaydet_dizini is None:
        kaydet_dizini = CIKTI_DIZINI
    
    os.makedirs(kaydet_dizini, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("DUYARLILIK ANALIZI RAPORU")
    print("=" * 60)
    
    rapor = {}
    
    degiskenler = {
        'guven': 'Guven Skoru',
        'paylasim': 'Paylasim Sikligi',
        'duygu': 'Duygu Sapmasi',
        'merkezlilik': 'Merkezlilik Skoru'
    }
    
    print("\n Tek Degisken Duyarliliklari:")
    print("-" * 40)
    
    for deg, isim in degiskenler.items():
        df = tek_degisken_duyarliligi(fis, deg)
        rapor[deg] = df
        
        risk_min = df['risk'].min()
        risk_max = df['risk'].max()
        risk_aralik = risk_max - risk_min
        
        korelasyon = np.corrcoef(df[deg], df['risk'])[0, 1]
        yon = '+' if korelasyon > 0.1 else ('-' if korelasyon < -0.1 else '=')
        
        print(f"\n  {isim}:")
        print(f"    Risk araligi : [{risk_min:.4f}, {risk_max:.4f}]")
        print(f"    Risk degisimi: {risk_aralik:.4f}")
        print(f"    Korelasyon   : {korelasyon:+.4f} ({yon})")
        
        if abs(korelasyon) > 0.5:
            etki = "GUCLU"
        elif abs(korelasyon) > 0.2:
            etki = "ORTA"
        else:
            etki = "ZAYIF"
        print(f"    Etki duzeyi  : {etki}")
    
    duyarlilik_grafikleri(
        fis,
        kaydet_yolu=os.path.join(kaydet_dizini, "07_duyarlilik_analizi.png")
    )
    
    print("\n" + "=" * 60)
    print("DUYARLILIK ANALIZI TAMAMLANDI")
    print("=" * 60)
    
    return rapor


if __name__ == "__main__":
    fis = BulanikCikarimSistemi('karisik')
    rapor = duyarlilik_raporu(fis)
    print("\n[TEST] Duyarlilik analizi modulu basariyla calisti!")
