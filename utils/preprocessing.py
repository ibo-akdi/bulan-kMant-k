# -*- coding: utf-8 -*-
"""
Veri On Isleme Modulu
======================
Sentetik veri uretimi ve on isleme fonksiyonlarini icerir.
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

# Windows konsol encoding duzeltmesi
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from utils.data_loader import (
    twitter_grafini_yukle,
    merkezlilik_hesapla,
    veriyi_kaydet,
    dizinleri_olustur,
    ISENMIS_VERI_DIZINI
)


def sentetik_veri_uret(ornek_sayisi=1000, rastgele_tohum=42):
    """
    Sentetik kullanıcı verisi üretir.
    
    Parametreler
    ------------
    ornek_sayisi : int
        Üretilecek örnek sayısı (varsayılan: 1000).
    rastgele_tohum : int
        Tekrarlanabilirlik için rastgele tohum değeri.
    
    Döndürür
    --------
    df : pandas.DataFrame
        Sentetik kullanıcı verisi.
        Sütunlar: kullanici_id, guven_skoru, paylasim_sikligi, 
                  duygu_sapmasi, merkezlilik_skoru
    
    Dağılımlar
    ----------
    - Güven Skoru (Trust): Uniform(0, 1)
    - Paylaşım Sıklığı (Frequency): Poisson(λ=8), [0, 50] aralığında
    - Duygu Sapması (Sentiment Deviation): Normal(μ=0, σ=0.35), [-1, +1] aralığında
    - Merkezlilik Skoru (Centrality): Beta(α=2, β=5), [0, 1] aralığında
    """
    np.random.seed(rastgele_tohum)
    
    print(f"[ÖNİŞLEM] {ornek_sayisi} adet sentetik veri üretiliyor...")
    
    # 1. Güven Skoru: Uniform(0, 1)
    guven = np.random.uniform(0, 1, ornek_sayisi)
    
    # 2. Paylaşım Sıklığı: Poisson(λ=8), maksimum 50
    paylasim = np.random.poisson(lam=8, size=ornek_sayisi)
    paylasim = np.clip(paylasim, 0, 50).astype(float)
    
    # 3. Duygu Sapması: Normal(μ=0, σ=0.35), [-1, +1] aralığında
    duygu = np.random.normal(loc=0, scale=0.35, size=ornek_sayisi)
    duygu = np.clip(duygu, -1, 1)
    
    # 4. Merkezlilik Skoru: Beta(α=2, β=5) - sağa çarpık dağılım
    merkezlilik = np.random.beta(a=2, b=5, size=ornek_sayisi)
    
    df = pd.DataFrame({
        'kullanici_id': range(1, ornek_sayisi + 1),
        'guven_skoru': np.round(guven, 4),
        'paylasim_sikligi': paylasim,
        'duygu_sapmasi': np.round(duygu, 4),
        'merkezlilik_skoru': np.round(merkezlilik, 4)
    })
    
    print(f"[ÖNİŞLEM] Sentetik veri üretildi: {len(df)} örnek")
    _veri_istatistiklerini_yazdir(df)
    
    return df


def graf_merkezliligini_entegre_et(df_sentetik, df_merkezlilik):
    """
    Sentetik veriye gerçek graf merkezlilik skorlarını entegre eder.
    
    Rastgele düğümlerden merkezlilik skorları alınarak sentetik verinin
    merkezlilik_skoru sütunu güncellenir.
    
    Parametreler
    ------------
    df_sentetik : pandas.DataFrame
        Sentetik kullanıcı verisi.
    df_merkezlilik : pandas.DataFrame
        Graf merkezlilik skorları.
    
    Döndürür
    --------
    df : pandas.DataFrame
        Güncellenmiş sentetik veri.
    """
    print("[ÖNİŞLEM] Gerçek graf merkezlilik skorları entegre ediliyor...")
    
    # Gerçek graftan rastgele merkezlilik skorları al
    n = len(df_sentetik)
    gercek_skorlar = df_merkezlilik['merkezlilik_skoru'].values
    
    # Rastgele örnekle (tekrarlı)
    secilen_indeksler = np.random.choice(len(gercek_skorlar), size=n, replace=True)
    df_sentetik = df_sentetik.copy()
    df_sentetik['merkezlilik_skoru'] = np.round(gercek_skorlar[secilen_indeksler], 4)
    
    # Graftan alınan düğüm ID'lerini de kaydet
    dugum_idler = df_merkezlilik['dugum_id'].values
    df_sentetik['graf_dugum_id'] = dugum_idler[secilen_indeksler]
    
    print(f"[ÖNİŞLEM] Merkezlilik skorları güncellendi")
    print(f"       Yeni merkezlilik aralığı: [{df_sentetik['merkezlilik_skoru'].min():.4f}, "
          f"{df_sentetik['merkezlilik_skoru'].max():.4f}]")
    
    return df_sentetik


def veriyi_normalize_et(df):
    """
    Verideki sütunları bulanık sistem girişleri için uygun aralıklara normalize eder.
    
    Parametreler
    ------------
    df : pandas.DataFrame
        Ham veya sentetik veri.
    
    Döndürür
    --------
    df : pandas.DataFrame
        Normalize edilmiş veri.
    """
    df = df.copy()
    
    # Güven skoru zaten [0,1] aralığında
    df['guven_skoru'] = df['guven_skoru'].clip(0, 1)
    
    # Paylaşım sıklığı [0, 50] aralığında kalmalı
    df['paylasim_sikligi'] = df['paylasim_sikligi'].clip(0, 50)
    
    # Duygu sapması [-1, +1] aralığında
    df['duygu_sapmasi'] = df['duygu_sapmasi'].clip(-1, 1)
    
    # Merkezlilik skoru [0, 1] aralığında
    df['merkezlilik_skoru'] = df['merkezlilik_skoru'].clip(0, 1)
    
    return df


def tam_veri_hatti_calistir(ornek_sayisi=1000, graf_entegre=True, rastgele_tohum=42):
    """
    Tam veri işleme hattını çalıştırır.
    
    1. Sentetik veri üretir
    2. Facebook grafından merkezlilik hesaplar (opsiyonel)
    3. Merkezlilik skorlarını entegre eder
    4. Normalize eder
    5. İşlenmiş veriyi kaydeder
    
    Parametreler
    ------------
    ornek_sayisi : int
        Üretilecek örnek sayısı.
    graf_entegre : bool
        True ise gerçek graf merkezlilik skorlarını kullanır.
    rastgele_tohum : int
        Rastgele tohum değeri.
    
    Döndürür
    --------
    df : pandas.DataFrame
        İşlenmiş ve kaydedilmiş veri.
    """
    dizinleri_olustur()
    
    print("=" * 60)
    print("VERİ İŞLEME HATTI BAŞLATILIYOR")
    print("=" * 60)
    
    # 1. Sentetik veri üret
    df = sentetik_veri_uret(ornek_sayisi, rastgele_tohum)
    
    # 2. Graf entegrasyonu
    if graf_entegre:
        try:
            G = twitter_grafini_yukle()
            df_merkezlilik = merkezlilik_hesapla(G)
            veriyi_kaydet(df_merkezlilik, "merkezlilik_skorlari.csv")
            
            # 3. Merkezlilik skorlarını entegre et
            df = graf_merkezliligini_entegre_et(df, df_merkezlilik)
        except FileNotFoundError as e:
            print(f"[UYARI] Graf verisi bulunamadı: {e}")
            print("[UYARI] Sentetik merkezlilik skorları kullanılacak.")
    
    # 4. Normalize et
    df = veriyi_normalize_et(df)
    
    # 5. Kaydet
    veriyi_kaydet(df, "sentetik_veri.csv")
    
    print("\n" + "=" * 60)
    print("VERİ İŞLEME HATTI TAMAMLANDI")
    print("=" * 60)
    
    return df


def _veri_istatistiklerini_yazdir(df):
    """Veri istatistiklerini konsola yazdırır."""
    sayisal_sutunlar = ['guven_skoru', 'paylasim_sikligi', 'duygu_sapmasi', 'merkezlilik_skoru']
    mevcut_sutunlar = [s for s in sayisal_sutunlar if s in df.columns]
    
    print("\n  --- Veri İstatistikleri ---")
    for sutun in mevcut_sutunlar:
        print(f"  {sutun:25s}: min={df[sutun].min():8.4f}, "
              f"ort={df[sutun].mean():8.4f}, "
              f"max={df[sutun].max():8.4f}, "
              f"std={df[sutun].std():8.4f}")
    print()


if __name__ == "__main__":
    df = tam_veri_hatti_calistir(ornek_sayisi=1000, graf_entegre=True)
    print("\n[TEST] Veri ön işleme modülü başarıyla çalıştı!")
    print(df.head(10).to_string())
