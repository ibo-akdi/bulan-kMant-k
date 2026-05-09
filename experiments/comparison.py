# -*- coding: utf-8 -*-
"""
Model Karsilastirma Modulu
============================
Bulanik mantik sistemi ile temel dogrusal modeli karsilastirir.
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
from models.baseline import TemelModel, modelleri_karsilastir
from utils.data_loader import islenmis_veri_yukle, veriyi_kaydet, ISENMIS_VERI_DIZINI
from visualization.plots import karsilastirma_grafikleri, CIKTI_DIZINI


def karsilastirma_deneyi_calistir(df=None, fonksiyon_tipi='karisik', kaydet_dizini=None):
    """Tam karsilastirma deneyini calistirir."""
    if kaydet_dizini is None:
        kaydet_dizini = CIKTI_DIZINI
    
    os.makedirs(kaydet_dizini, exist_ok=True)
    
    print("\n" + "#" * 60)
    print("     MODEL KARSILASTIRMA DENEYI")
    print("#" * 60)
    
    # Veri yukle
    if df is None:
        try:
            df = islenmis_veri_yukle("simulasyon_sonuclari.csv")
        except FileNotFoundError:
            df = islenmis_veri_yukle("sentetik_veri.csv")
    
    # MODEL 1: Bulanik Mantik Sistemi
    print("\n-- MODEL 1: Bulanik Mantik Sistemi --")
    fis = BulanikCikarimSistemi(fonksiyon_tipi)
    
    if 'risk_seviyesi' in df.columns:
        bulanik_riskler = df['risk_seviyesi'].values
        print(f"[KARSILASTIRMA] Mevcut risk degerleri kullaniliyor ({len(bulanik_riskler)} ornek)")
    else:
        bulanik_riskler = fis.toplu_hesapla(df)
    
    # MODEL 2: Temel Dogrusal Model
    print("\n-- MODEL 2: Temel Dogrusal Model --")
    temel_model = TemelModel()
    temel_riskler = temel_model.toplu_tahmin(df)
    
    # KARSILASTIRMA
    print("\n-- KARSILASTIRMA ANALIZI --")
    metrikler = modelleri_karsilastir(bulanik_riskler, temel_riskler)
    
    karsilastirma_df = pd.DataFrame({
        'guven_skoru': df['guven_skoru'],
        'paylasim_sikligi': df['paylasim_sikligi'],
        'duygu_sapmasi': df['duygu_sapmasi'],
        'merkezlilik_skoru': df['merkezlilik_skoru'],
        'bulanik_risk': np.round(bulanik_riskler, 4),
        'temel_risk': np.round(temel_riskler, 4),
        'fark': np.round(bulanik_riskler - temel_riskler, 4),
        'mutlak_fark': np.round(np.abs(bulanik_riskler - temel_riskler), 4)
    })
    
    veriyi_kaydet(karsilastirma_df, "karsilastirma_sonuclari.csv")
    
    karsilastirma_grafikleri(
        bulanik_riskler, temel_riskler, metrikler,
        kaydet_yolu=os.path.join(kaydet_dizini, "08_model_karsilastirma.png")
    )
    
    # Ozet
    print("\n" + "=" * 60)
    print("KARSILASTIRMA OZETI")
    print("=" * 60)
    print(f"\n  Bulanik Model:")
    print(f"    Ortalama risk : {bulanik_riskler.mean():.4f}")
    print(f"    Std sapma     : {bulanik_riskler.std():.4f}")
    print(f"\n  Temel Model:")
    print(f"    Ortalama risk : {temel_riskler.mean():.4f}")
    print(f"    Std sapma     : {temel_riskler.std():.4f}")
    print(f"\n  Farklar:")
    print(f"    Ort. mutlak fark : {karsilastirma_df['mutlak_fark'].mean():.4f}")
    print(f"    Maks. fark       : {karsilastirma_df['mutlak_fark'].max():.4f}")
    print("=" * 60)
    
    sonuclar = {
        'bulanik_riskler': bulanik_riskler,
        'temel_riskler': temel_riskler,
        'metrikler': metrikler,
        'karsilastirma_df': karsilastirma_df,
        'fis': fis
    }
    
    return sonuclar


if __name__ == "__main__":
    sonuclar = karsilastirma_deneyi_calistir()
    print("\n[TEST] Karsilastirma modulu basariyla calisti!")
