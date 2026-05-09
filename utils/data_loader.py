# -*- coding: utf-8 -*-
"""
Veri Yukleme Modulu
====================
Facebook sosyal ag verisini ve islenmis CSV dosyalarini yukler.
NetworkX graf nesnesi olusturur ve merkezlilik skorlarini hesaplar.
"""

import os
import sys
import gzip
import pandas as pd
import networkx as nx
import numpy as np

# Windows konsol encoding duzeltmesi
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


# Proje kök dizini
PROJE_DIZINI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI_DIZINI = os.path.join(PROJE_DIZINI, "data")
HAM_VERI_DIZINI = os.path.join(VERI_DIZINI, "raw")
ISENMIS_VERI_DIZINI = os.path.join(VERI_DIZINI, "processed")


def dizinleri_olustur():
    """Gerekli veri dizinlerini oluşturur."""
    for dizin in [VERI_DIZINI, HAM_VERI_DIZINI, ISENMIS_VERI_DIZINI]:
        os.makedirs(dizin, exist_ok=True)


def twitter_grafini_yukle(dosya_yolu=None):
    """
    Twitter sosyal ağ verisini yükler ve NetworkX graf nesnesi oluşturur.
    
    Parametreler
    ------------
    dosya_yolu : str, opsiyonel
        twitter_combined.txt.gz dosyasının yolu.
        Belirtilmezse proje kök dizininde aranır.
    
    Döndürür
    --------
    G : networkx.Graph
        Yönlendirilmemiş sosyal ağ grafı.
        4039 düğüm, 88234 kenar içerir.
    """
    if dosya_yolu is None:
        # Önce proje kök dizininde ara
        dosya_yolu = os.path.join(PROJE_DIZINI, "twitter_combined.txt.gz")
        if not os.path.exists(dosya_yolu):
            dosya_yolu = os.path.join(HAM_VERI_DIZINI, "twitter_combined.txt.gz")
    
    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(
            f"Twitter veri dosyası bulunamadı: {dosya_yolu}\n"
            "Lütfen 'twitter_combined.txt.gz' dosyasını proje dizinine yerleştirin."
        )
    
    print(f"[VERİ] Twitter graf verisi yükleniyor: {dosya_yolu}")
    
    # Gzip dosyasını oku ve graf oluştur
    G = nx.Graph()
    with gzip.open(dosya_yolu, 'rt') as f:
        for satir in f:
            satirr = satir.strip()
            if satirr and not satirr.startswith('#'):
                parcalar = satirr.split()
                if len(parcalar) >= 2:
                    kaynak = int(parcalar[0])
                    hedef = int(parcalar[1])
                    G.add_edge(kaynak, hedef)
    
    print(f"[VERİ] Graf yüklendi: {G.number_of_nodes()} düğüm, {G.number_of_edges()} kenar")
    return G


def merkezlilik_hesapla(G):
    """
    Graf üzerinde merkezlilik skorlarını hesaplar.
    
    Parametreler
    ------------
    G : networkx.Graph
        Sosyal ağ grafı.
    
    Döndürür
    --------
    df : pandas.DataFrame
        Her düğüm için merkezlilik skorlarını içeren DataFrame.
        Sütunlar: dugum_id, derece_merkezliligi, arasindalik_merkezliligi, merkezlilik_skoru
    """
    print("[VERİ] Merkezlilik skorları hesaplanıyor...")
    
    # Derece merkezliliği (Degree Centrality)
    derece = nx.degree_centrality(G)
    
    # Arasındalık merkezliliği (Betweenness Centrality)
    print("[VERİ] Arasındalık merkezliliği hesaplanıyor (bu biraz zaman alabilir)...")
    arasindalik = nx.betweenness_centrality(G, normalized=True, k=min(500, G.number_of_nodes()))
    
    # DataFrame oluştur
    dugumler = list(G.nodes())
    df = pd.DataFrame({
        'dugum_id': dugumler,
        'derece_merkezliligi': [derece[n] for n in dugumler],
        'arasindalik_merkezliligi': [arasindalik[n] for n in dugumler]
    })
    
    # Birleşik merkezlilik skoru: derece ve arasındalık ortalaması (normalize edilmiş)
    # Her ikisini de [0,1] arasına normalize et
    derece_norm = (df['derece_merkezliligi'] - df['derece_merkezliligi'].min()) / \
                  (df['derece_merkezliligi'].max() - df['derece_merkezliligi'].min() + 1e-10)
    arasindalik_norm = (df['arasindalik_merkezliligi'] - df['arasindalik_merkezliligi'].min()) / \
                       (df['arasindalik_merkezliligi'].max() - df['arasindalik_merkezliligi'].min() + 1e-10)
    
    # Ağırlıklı birleşik skor
    df['merkezlilik_skoru'] = 0.6 * derece_norm + 0.4 * arasindalik_norm
    
    # [0,1] aralığına normalize et
    df['merkezlilik_skoru'] = df['merkezlilik_skoru'].clip(0, 1)
    
    print(f"[VERİ] Merkezlilik skorları hesaplandı: {len(df)} düğüm")
    print(f"       Derece merkezliliği aralığı: [{df['derece_merkezliligi'].min():.4f}, {df['derece_merkezliligi'].max():.4f}]")
    print(f"       Arasındalık merkezliliği aralığı: [{df['arasindalik_merkezliligi'].min():.4f}, {df['arasindalik_merkezliligi'].max():.4f}]")
    print(f"       Birleşik skor aralığı: [{df['merkezlilik_skoru'].min():.4f}, {df['merkezlilik_skoru'].max():.4f}]")
    
    return df


def islenmis_veri_yukle(dosya_adi="sentetik_veri.csv"):
    """
    İşlenmiş CSV verisini yükler.
    
    Parametreler
    ------------
    dosya_adi : str
        İşlenmiş veri dosyasının adı.
    
    Döndürür
    --------
    df : pandas.DataFrame
        İşlenmiş veri.
    """
    dosya_yolu = os.path.join(ISENMIS_VERI_DIZINI, dosya_adi)
    
    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(
            f"İşlenmiş veri dosyası bulunamadı: {dosya_yolu}\n"
            "Önce 'preprocessing.py' ile veri oluşturun."
        )
    
    df = pd.read_csv(dosya_yolu)
    print(f"[VERİ] İşlenmiş veri yüklendi: {len(df)} satır, {len(df.columns)} sütun")
    return df


def simulasyon_sonuclarini_yukle(dosya_adi="simulasyon_sonuclari.csv"):
    """Simülasyon sonuçlarını yükler."""
    dosya_yolu = os.path.join(ISENMIS_VERI_DIZINI, dosya_adi)
    
    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(f"Simülasyon sonuçları bulunamadı: {dosya_yolu}")
    
    df = pd.read_csv(dosya_yolu)
    print(f"[VERİ] Simülasyon sonuçları yüklendi: {len(df)} satır")
    return df


def veriyi_kaydet(df, dosya_adi, dizin=None):
    """
    DataFrame'i CSV olarak kaydeder.
    
    Parametreler
    ------------
    df : pandas.DataFrame
        Kaydedilecek veri.
    dosya_adi : str
        Dosya adı.
    dizin : str, opsiyonel
        Hedef dizin. Belirtilmezse processed/ kullanılır.
    """
    if dizin is None:
        dizin = ISENMIS_VERI_DIZINI
    
    os.makedirs(dizin, exist_ok=True)
    dosya_yolu = os.path.join(dizin, dosya_adi)
    df.to_csv(dosya_yolu, index=False)
    print(f"[VERİ] Veri kaydedildi: {dosya_yolu} ({len(df)} satır)")


if __name__ == "__main__":
    # Test: Twitter grafını yükle ve merkezlilik hesapla
    dizinleri_olustur()
    G = twitter_grafini_yukle()
    df_merkezlilik = merkezlilik_hesapla(G)
    veriyi_kaydet(df_merkezlilik, "merkezlilik_skorlari.csv")
    print("\n[TEST] Veri yükleme modülü başarıyla çalıştı!")
