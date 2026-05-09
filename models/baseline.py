# -*- coding: utf-8 -*-
"""
Temel Karşılaştırma Modeli (Baseline)
=======================================
Bulanık mantık sistemiyle karşılaştırma için ağırlıklı doğrusal model.

Model Formülü
--------------
Risk = w1·(1 - Güven) + w2·norm(Paylaşım) + w3·norm(Duygu) + w4·Merkezlilik

Burada:
- w1, w2, w3, w4: ağırlık katsayıları (toplam = 1)
- norm(Paylaşım) = Paylaşım / 50 (0-50 aralığını 0-1'e dönüştürür)
- norm(Duygu) = |Duygu| (mutlak sapma)

Karşılaştırma Metrikleri
-------------------------
- MSE (Mean Squared Error): Ortalama Karesel Hata
- MAE (Mean Absolute Error): Ortalama Mutlak Hata
- Korelasyon (Pearson)
- Doğruluk (Accuracy): Risk kategorisi eşleşme oranı
- Kesinlik (Precision), Duyarlılık (Recall), F1-Skor
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from scipy.stats import pearsonr


class TemelModel:
    """
    Ağırlıklı doğrusal temel model (Weighted Linear Baseline).
    
    Bulanık mantık sistemiyle karşılaştırma referansı olarak kullanılır.
    """
    
    def __init__(self, w1=0.30, w2=0.25, w3=0.20, w4=0.25):
        """
        Temel modeli başlatır.
        
        Parametreler
        ------------
        w1 : float - Güven ağırlığı (varsayılan: 0.30)
        w2 : float - Paylaşım sıklığı ağırlığı (varsayılan: 0.25)
        w3 : float - Duygu sapması ağırlığı (varsayılan: 0.20)
        w4 : float - Merkezlilik ağırlığı (varsayılan: 0.25)
        """
        # Ağırlıkları normalize et
        toplam = w1 + w2 + w3 + w4
        self.w1 = w1 / toplam
        self.w2 = w2 / toplam
        self.w3 = w3 / toplam
        self.w4 = w4 / toplam
        
        print(f"[TEMEL MODEL] Agirliklar: w1={self.w1:.3f}, w2={self.w2:.3f}, "
              f"w3={self.w3:.3f}, w4={self.w4:.3f}")
    
    def tahmin(self, guven, paylasim, duygu, merkezlilik):
        """
        Tek bir giriş seti için risk tahmini yapar.
        
        Risk = w1·(1-Güven) + w2·(Paylaşım/50) + w3·|Duygu| + w4·Merkezlilik
        """
        risk = (
            self.w1 * (1 - np.clip(guven, 0, 1)) +
            self.w2 * np.clip(paylasim / 50.0, 0, 1) +
            self.w3 * np.abs(np.clip(duygu, -1, 1)) +
            self.w4 * np.clip(merkezlilik, 0, 1)
        )
        return np.clip(risk, 0, 1)
    
    def toplu_tahmin(self, df):
        """
        DataFrame üzerinde toplu risk tahmini yapar.
        
        Parametreler
        ------------
        df : pandas.DataFrame
            Giriş verisi.
        
        Döndürür
        --------
        tahminler : numpy.ndarray
            Tahmin edilen risk değerleri.
        """
        print(f"[TEMEL MODEL] Toplu tahmin: {len(df)} ornek...")
        
        tahminler = np.array([
            self.tahmin(
                satir['guven_skoru'],
                satir['paylasim_sikligi'],
                satir['duygu_sapmasi'],
                satir['merkezlilik_skoru']
            )
            for _, satir in df.iterrows()
        ])
        
        print(f"[TEMEL MODEL] Tahmin araligi: [{tahminler.min():.4f}, {tahminler.max():.4f}]")
        return tahminler


def risk_kategorisi_belirle(risk_degerleri, esikler=(0.35, 0.65)):
    """
    Risk değerlerini kategorilere ayırır.
    
    Parametreler
    ------------
    risk_degerleri : numpy.ndarray
        Risk değerleri [0, 1].
    esikler : tuple
        (düşük_üst, yüksek_alt) eşik değerleri.
    
    Döndürür
    --------
    kategoriler : numpy.ndarray
        0: Düşük, 1: Orta, 2: Yüksek
    """
    kategoriler = np.zeros(len(risk_degerleri), dtype=int)
    kategoriler[risk_degerleri >= esikler[0]] = 1
    kategoriler[risk_degerleri >= esikler[1]] = 2
    return kategoriler


def modelleri_karsilastir(bulanik_riskler, temel_riskler):
    """
    Bulanık ve temel model sonuçlarını karşılaştırır.
    
    Parametreler
    ------------
    bulanik_riskler : numpy.ndarray
        Bulanık mantık sistemi risk çıktıları (referans/ground truth).
    temel_riskler : numpy.ndarray
        Temel model tahminleri.
    
    Döndürür
    --------
    metrikler : dict
        Tüm karşılaştırma metrikleri.
    """
    print("\n" + "=" * 60)
    print("MODEL KARSILASTIRMA SONUCLARI")
    print("=" * 60)
    
    # Surekli metrikler
    mse = mean_squared_error(bulanik_riskler, temel_riskler)
    mae = mean_absolute_error(bulanik_riskler, temel_riskler)
    korelasyon, p_deger = pearsonr(bulanik_riskler, temel_riskler)
    
    print(f"\n Surekli Metrikler:")
    print(f"  MSE (Ort. Karesel Hata)   : {mse:.6f}")
    print(f"  MAE (Ort. Mutlak Hata)    : {mae:.6f}")
    print(f"  Pearson Korelasyonu       : {korelasyon:.6f} (p={p_deger:.2e})")
    print(f"  RMSE (Kok Ort. Kare Hata) : {np.sqrt(mse):.6f}")
    
    # Kategorik metrikler
    bulanik_kat = risk_kategorisi_belirle(bulanik_riskler)
    temel_kat = risk_kategorisi_belirle(temel_riskler)
    
    dogruluk = accuracy_score(bulanik_kat, temel_kat)
    kesinlik = precision_score(bulanik_kat, temel_kat, average='weighted', zero_division=0)
    duyarlilik = recall_score(bulanik_kat, temel_kat, average='weighted', zero_division=0)
    f1 = f1_score(bulanik_kat, temel_kat, average='weighted', zero_division=0)
    
    print(f"\n Kategorik Metrikler (Dusuk/Orta/Yuksek):")
    print(f"  Dogruluk (Accuracy)   : {dogruluk:.4f} ({dogruluk*100:.1f}%)")
    print(f"  Kesinlik (Precision)  : {kesinlik:.4f}")
    print(f"  Duyarlilik (Recall)   : {duyarlilik:.4f}")
    print(f"  F1-Skor              : {f1:.4f}")
    
    # Karisiklik matrisi
    kat_isimleri = ['Dusuk', 'Orta', 'Yuksek']
    print(f"\n Karisiklik Matrisi:")
    km = confusion_matrix(bulanik_kat, temel_kat, labels=[0, 1, 2])
    
    print(f"{'':15s} {'Tahmin':^30s}")
    print(f"{'':15s} {'Dusuk':>10s} {'Orta':>10s} {'Yuksek':>10s}")
    for i, isim in enumerate(kat_isimleri):
        satir = '  '.join(f'{km[i,j]:8d}' for j in range(3))
        print(f"  Gercek {isim:7s}: {satir}")
    
    metrikler = {
        'MSE': mse,
        'MAE': mae,
        'RMSE': np.sqrt(mse),
        'Korelasyon': korelasyon,
        'P_Deger': p_deger,
        'Dogruluk': dogruluk,
        'Kesinlik': kesinlik,
        'Duyarlilik': duyarlilik,
        'F1_Skor': f1,
        'Karisiklik_Matrisi': km
    }
    
    print("\n" + "=" * 60)
    
    return metrikler


if __name__ == "__main__":
    # Test
    model = TemelModel()
    
    # Tek tahmin
    test_senaryolari = [
        (0.2, 35, 0.8, 0.9, "Yuksek Riskli"),
        (0.9, 5, 0.1, 0.2, "Dusuk Riskli"),
        (0.5, 20, 0.4, 0.5, "Orta Riskli"),
    ]
    
    print("\n--- Tek Tahmin Testi ---")
    for guven, paylasim, duygu, merkezlilik, aciklama in test_senaryolari:
        risk = model.tahmin(guven, paylasim, duygu, merkezlilik)
        print(f"  {aciklama:15s}: Risk = {risk:.4f}")
    
    print("\n[TEST] Temel model basariyla calisti!")
