# -*- coding: utf-8 -*-
"""
Görselleştirme Modülü
======================
Bulanık mantık sistemi için tüm grafik ve görsel çıktıları üretir.

Üretilen Grafikler
-------------------
1. Üyelik fonksiyonu grafikleri
2. 3D yüzey grafikleri (surface plot)
3. Isı haritaları (heatmap)
4. Risk dağılımı histogramı
5. Giriş-çıkış örnekleri
6. Duyarlılık analizi grafikleri
7. Model karşılaştırma grafikleri
8. Kural aktivasyon diyagramları
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# Matplotlib Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Seaborn stili
sns.set_style("whitegrid")
sns.set_palette("husl")

# Varsayılan çıktı dizini
CIKTI_DIZINI = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "visualization", "output"
)


def _dizin_kontrol(kaydet_yolu):
    """Dosya yolunun dizinini oluşturur."""
    if kaydet_yolu:
        os.makedirs(os.path.dirname(kaydet_yolu), exist_ok=True)


def yuzey_grafigi_3d(fis, degisken1='guven_skoru', degisken2='paylasim_sikligi',
                     sabit_degerler=None, cozunurluk=30, kaydet_yolu=None):
    """
    İki giriş değişkeni için 3D yüzey grafiği oluşturur.
    
    Parametreler
    ------------
    fis : BulanikCikarimSistemi
        Bulanık çıkarım sistemi nesnesi.
    degisken1, degisken2 : str
        X ve Y eksenlerindeki değişken adları.
    sabit_degerler : dict, opsiyonel
        Sabit tutulan diğer değişkenlerin değerleri.
    cozunurluk : int
        Her eksen için nokta sayısı.
    kaydet_yolu : str, opsiyonel
        Grafik dosyasının kaydedileceği yol.
    """
    if sabit_degerler is None:
        sabit_degerler = {
            'guven_skoru': 0.5,
            'paylasim_sikligi': 20,
            'duygu_sapmasi': 0.3,
            'merkezlilik_skoru': 0.5
        }
    
    # Değişken aralıkları
    araliklar = {
        'guven_skoru': (0, 1),
        'paylasim_sikligi': (0, 50),
        'duygu_sapmasi': (-1, 1),
        'merkezlilik_skoru': (0, 1)
    }
    
    turkce_isimler = {
        'guven_skoru': 'Güven Skoru',
        'paylasim_sikligi': 'Paylaşım Sıklığı',
        'duygu_sapmasi': 'Duygu Sapması',
        'merkezlilik_skoru': 'Merkezlilik Skoru'
    }
    
    x_aralik = araliklar[degisken1]
    y_aralik = araliklar[degisken2]
    
    x = np.linspace(x_aralik[0], x_aralik[1], cozunurluk)
    y = np.linspace(y_aralik[0], y_aralik[1], cozunurluk)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    print(f"[GÖRSELLEŞTİRME] 3D yüzey grafiği oluşturuluyor: "
          f"{turkce_isimler[degisken1]} vs {turkce_isimler[degisken2]}...")
    
    for i in range(cozunurluk):
        for j in range(cozunurluk):
            girisler = sabit_degerler.copy()
            girisler[degisken1] = X[i, j]
            girisler[degisken2] = Y[i, j]
            
            Z[i, j] = fis.hesapla(
                guven=girisler['guven_skoru'],
                paylasim=girisler['paylasim_sikligi'],
                duygu=girisler['duygu_sapmasi'],
                merkezlilik=girisler['merkezlilik_skoru']
            )
    
    # 3D grafik
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, Z, cmap='RdYlGn_r', alpha=0.85,
                          edgecolor='none', antialiased=True)
    
    ax.set_xlabel(turkce_isimler[degisken1], fontsize=11, labelpad=10)
    ax.set_ylabel(turkce_isimler[degisken2], fontsize=11, labelpad=10)
    ax.set_zlabel('Risk Seviyesi', fontsize=11, labelpad=10)
    ax.set_title(f'Yanlış Bilgi Risk Yüzeyi\n{turkce_isimler[degisken1]} vs {turkce_isimler[degisken2]}',
                fontsize=13, fontweight='bold', pad=20)
    
    fig.colorbar(surf, ax=ax, shrink=0.6, label='Risk Seviyesi')
    ax.view_init(elev=25, azim=45)
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] 3D grafik kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def isi_haritasi(fis, degisken1='guven_skoru', degisken2='merkezlilik_skoru',
                 sabit_degerler=None, cozunurluk=40, kaydet_yolu=None):
    """
    İki giriş değişkeni için ısı haritası oluşturur.
    
    Parametreler
    ------------
    fis : BulanikCikarimSistemi
    degisken1, degisken2 : str
    sabit_degerler : dict
    cozunurluk : int
    kaydet_yolu : str
    """
    if sabit_degerler is None:
        sabit_degerler = {
            'guven_skoru': 0.5,
            'paylasim_sikligi': 20,
            'duygu_sapmasi': 0.3,
            'merkezlilik_skoru': 0.5
        }
    
    araliklar = {
        'guven_skoru': (0, 1),
        'paylasim_sikligi': (0, 50),
        'duygu_sapmasi': (-1, 1),
        'merkezlilik_skoru': (0, 1)
    }
    
    turkce_isimler = {
        'guven_skoru': 'Güven Skoru',
        'paylasim_sikligi': 'Paylaşım Sıklığı',
        'duygu_sapmasi': 'Duygu Sapması',
        'merkezlilik_skoru': 'Merkezlilik Skoru'
    }
    
    x_aralik = araliklar[degisken1]
    y_aralik = araliklar[degisken2]
    
    x = np.linspace(x_aralik[0], x_aralik[1], cozunurluk)
    y = np.linspace(y_aralik[0], y_aralik[1], cozunurluk)
    Z = np.zeros((len(y), len(x)))
    
    print(f"[GÖRSELLEŞTİRME] Isı haritası oluşturuluyor: "
          f"{turkce_isimler[degisken1]} vs {turkce_isimler[degisken2]}...")
    
    for i in range(len(y)):
        for j in range(len(x)):
            girisler = sabit_degerler.copy()
            girisler[degisken1] = x[j]
            girisler[degisken2] = y[i]
            
            Z[i, j] = fis.hesapla(
                guven=girisler['guven_skoru'],
                paylasim=girisler['paylasim_sikligi'],
                duygu=girisler['duygu_sapmasi'],
                merkezlilik=girisler['merkezlilik_skoru']
            )
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(Z, extent=[x_aralik[0], x_aralik[1], y_aralik[0], y_aralik[1]],
                   origin='lower', cmap='RdYlGn_r', aspect='auto', interpolation='bilinear')
    
    plt.colorbar(im, ax=ax, label='Risk Seviyesi')
    
    ax.set_xlabel(turkce_isimler[degisken1], fontsize=12)
    ax.set_ylabel(turkce_isimler[degisken2], fontsize=12)
    ax.set_title(f'Risk Isı Haritası\n{turkce_isimler[degisken1]} vs {turkce_isimler[degisken2]}',
                fontsize=13, fontweight='bold')
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Isı haritası kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def risk_dagilimi(risk_degerleri, baslik="Yanlış Bilgi Risk Dağılımı", kaydet_yolu=None):
    """
    Risk değerlerinin dağılımını histogram ve KDE ile gösterir.
    
    Parametreler
    ------------
    risk_degerleri : numpy.ndarray
        Risk değerleri.
    baslik : str
        Grafik başlığı.
    kaydet_yolu : str
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram + KDE
    ax1 = axes[0]
    ax1.hist(risk_degerleri, bins=40, density=True, alpha=0.6, color='#3498db',
            edgecolor='white', label='Histogram')
    
    # KDE çizgisi
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(risk_degerleri)
    x_kde = np.linspace(0, 1, 200)
    ax1.plot(x_kde, kde(x_kde), 'r-', linewidth=2.5, label='KDE')
    
    # Bölge renklendirme
    ax1.axvspan(0, 0.35, alpha=0.1, color='green', label='Düşük Risk')
    ax1.axvspan(0.35, 0.65, alpha=0.1, color='orange', label='Orta Risk')
    ax1.axvspan(0.65, 1, alpha=0.1, color='red', label='Yüksek Risk')
    
    ax1.set_xlabel('Risk Seviyesi', fontsize=11)
    ax1.set_ylabel('Yoğunluk', fontsize=11)
    ax1.set_title(baslik, fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Kutu grafiği (Box Plot)
    ax2 = axes[1]
    bp = ax2.boxplot(risk_degerleri, vert=True, widths=0.5,
                    patch_artist=True, 
                    boxprops=dict(facecolor='#3498db', alpha=0.6),
                    medianprops=dict(color='red', linewidth=2))
    
    ax2.set_ylabel('Risk Seviyesi', fontsize=11)
    ax2.set_title('Risk Kutu Grafiği', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # İstatistikler
    istatistik_metin = (
        f"n = {len(risk_degerleri)}\n"
        f"Ort = {np.mean(risk_degerleri):.3f}\n"
        f"Std = {np.std(risk_degerleri):.3f}\n"
        f"Min = {np.min(risk_degerleri):.3f}\n"
        f"Max = {np.max(risk_degerleri):.3f}"
    )
    ax2.text(1.3, np.median(risk_degerleri), istatistik_metin,
            fontsize=9, verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Risk dağılımı kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def giris_cikis_ornekleri(fis, kaydet_yolu=None):
    """
    Çeşitli giriş senaryoları ve çıktıları gösteren grafik oluşturur.
    """
    senaryolar = [
        {'ad': 'Güvenilir Pasif', 'guven': 0.9, 'paylasim': 5, 'duygu': 0.1, 'merkezlilik': 0.2},
        {'ad': 'Güvenilmez Aktif', 'guven': 0.1, 'paylasim': 40, 'duygu': 0.8, 'merkezlilik': 0.7},
        {'ad': 'Ortalama Kullanıcı', 'guven': 0.5, 'paylasim': 15, 'duygu': 0.3, 'merkezlilik': 0.5},
        {'ad': 'Etki Merkezi', 'guven': 0.7, 'paylasim': 30, 'duygu': 0.2, 'merkezlilik': 0.9},
        {'ad': 'Trol Hesap', 'guven': 0.05, 'paylasim': 48, 'duygu': 0.95, 'merkezlilik': 0.6},
        {'ad': 'Sessiz Güvenilir', 'guven': 0.95, 'paylasim': 2, 'duygu': 0.05, 'merkezlilik': 0.1},
        {'ad': 'Duygusal Paylaşımcı', 'guven': 0.4, 'paylasim': 25, 'duygu': 0.85, 'merkezlilik': 0.4},
        {'ad': 'Süper Yayıcı', 'guven': 0.15, 'paylasim': 45, 'duygu': 0.7, 'merkezlilik': 0.95},
    ]
    
    isimler = []
    riskler = []
    renkler = []
    
    for s in senaryolar:
        risk = fis.hesapla(s['guven'], s['paylasim'], s['duygu'], s['merkezlilik'])
        isimler.append(s['ad'])
        riskler.append(risk)
        
        if risk < 0.35:
            renkler.append('#2ecc71')
        elif risk < 0.65:
            renkler.append('#f39c12')
        else:
            renkler.append('#e74c3c')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    y_pos = np.arange(len(isimler))
    bars = ax.barh(y_pos, riskler, color=renkler, edgecolor='white', height=0.6)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(isimler, fontsize=10)
    ax.set_xlabel('Risk Seviyesi', fontsize=12)
    ax.set_title('Kullanıcı Profili Senaryoları ve Risk Seviyeleri',
                fontsize=13, fontweight='bold')
    ax.set_xlim(0, 1)
    
    # Bölge çizgileri
    ax.axvline(x=0.35, color='green', linestyle='--', alpha=0.5, label='Düşük/Orta sınır')
    ax.axvline(x=0.65, color='red', linestyle='--', alpha=0.5, label='Orta/Yüksek sınır')
    
    # Risk değerlerini barların üzerine yaz
    for bar, risk in zip(bars, riskler):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
               f'{risk:.3f}', va='center', fontsize=10, fontweight='bold')
    
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Giriş-çıkış örnekleri kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def duyarlilik_grafikleri(fis, kaydet_yolu=None):
    """
    Tek değişken duyarlılık analizi grafikleri oluşturur.
    Her değişken tek tek değiştirilirken diğerleri sabit tutulur.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Duyarlılık Analizi: Tek Değişken Etkisi',
                fontsize=14, fontweight='bold', y=1.02)
    
    sabit = {'guven': 0.5, 'paylasim': 20, 'duygu': 0.3, 'merkezlilik': 0.5}
    n_nokta = 100
    
    # 1. Güven Skoru Etkisi
    ax = axes[0, 0]
    x = np.linspace(0, 1, n_nokta)
    y = [fis.hesapla(xi, sabit['paylasim'], sabit['duygu'], sabit['merkezlilik']) for xi in x]
    ax.plot(x, y, 'b-', linewidth=2.5, color='#2980b9')
    ax.fill_between(x, y, alpha=0.15, color='#2980b9')
    ax.set_xlabel('Güven Skoru', fontsize=11)
    ax.set_ylabel('Risk Seviyesi', fontsize=11)
    ax.set_title('Güven ↑ → Risk ?', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    # 2. Paylaşım Sıklığı Etkisi (farklı güven seviyeleri)
    ax = axes[0, 1]
    x = np.linspace(0, 50, n_nokta)
    for guven_degeri, renk, etiket in [(0.2, '#e74c3c', 'Düşük Güven (0.2)'),
                                         (0.5, '#f39c12', 'Orta Güven (0.5)'),
                                         (0.8, '#2ecc71', 'Yüksek Güven (0.8)')]:
        y = [fis.hesapla(guven_degeri, xi, sabit['duygu'], sabit['merkezlilik']) for xi in x]
        ax.plot(x, y, linewidth=2, color=renk, label=etiket)
    
    ax.set_xlabel('Paylaşım Sıklığı (gönderi/gün)', fontsize=11)
    ax.set_ylabel('Risk Seviyesi', fontsize=11)
    ax.set_title('Sabit Güven → Paylaşım Etkisi', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    # 3. Duygu Sapması Etkisi
    ax = axes[1, 0]
    x = np.linspace(-1, 1, n_nokta)
    y = [fis.hesapla(sabit['guven'], sabit['paylasim'], xi, sabit['merkezlilik']) for xi in x]
    ax.plot(x, y, 'r-', linewidth=2.5, color='#c0392b')
    ax.fill_between(x, y, alpha=0.15, color='#c0392b')
    ax.set_xlabel('Duygu Sapması', fontsize=11)
    ax.set_ylabel('Risk Seviyesi', fontsize=11)
    ax.set_title('Duygu Değişkenliği → Risk ?', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    # 4. Merkezlilik Skoru Etkisi
    ax = axes[1, 1]
    x = np.linspace(0, 1, n_nokta)
    y = [fis.hesapla(sabit['guven'], sabit['paylasim'], sabit['duygu'], xi) for xi in x]
    ax.plot(x, y, 'g-', linewidth=2.5, color='#27ae60')
    ax.fill_between(x, y, alpha=0.15, color='#27ae60')
    ax.set_xlabel('Merkezlilik Skoru', fontsize=11)
    ax.set_ylabel('Risk Seviyesi', fontsize=11)
    ax.set_title('Merkezlilik ↑ → Risk ?', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Duyarlılık grafikleri kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def karsilastirma_grafikleri(bulanik_riskler, temel_riskler, metrikler, kaydet_yolu=None):
    """
    Bulanık model ve temel model karşılaştırma grafikleri oluşturur.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Bulanık Mantık vs Temel Model Karşılaştırması',
                fontsize=14, fontweight='bold', y=1.02)
    
    # 1. Scatter plot
    ax = axes[0, 0]
    ax.scatter(bulanik_riskler, temel_riskler, alpha=0.3, s=10, color='#3498db')
    ax.plot([0, 1], [0, 1], 'r--', linewidth=1.5, label='Mükemmel eşleşme')
    ax.set_xlabel('Bulanık Mantık Riski', fontsize=11)
    ax.set_ylabel('Temel Model Riski', fontsize=11)
    ax.set_title(f'Tahmin Karşılaştırması (r={metrikler["Korelasyon"]:.3f})',
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # 2. Fark dağılımı
    ax = axes[0, 1]
    farklar = bulanik_riskler - temel_riskler
    ax.hist(farklar, bins=40, density=True, alpha=0.6, color='#9b59b6', edgecolor='white')
    ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5)
    ax.set_xlabel('Fark (Bulanık - Temel)', fontsize=11)
    ax.set_ylabel('Yoğunluk', fontsize=11)
    ax.set_title(f'Tahmin Farkları Dağılımı (MAE={metrikler["MAE"]:.4f})',
                fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 3. Metrik karşılaştırma bar grafiği
    ax = axes[1, 0]
    metrik_isimleri = ['Doğruluk', 'Kesinlik', 'Duyarlılık', 'F1-Skor']
    metrik_degerleri = [
        metrikler['Dogruluk'],
        metrikler['Kesinlik'],
        metrikler['Duyarlilik'],
        metrikler['F1_Skor']
    ]
    
    renkler = ['#2ecc71', '#3498db', '#e67e22', '#e74c3c']
    bars = ax.bar(metrik_isimleri, metrik_degerleri, color=renkler, 
                 edgecolor='white', width=0.6)
    
    for bar, deger in zip(bars, metrik_degerleri):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
               f'{deger:.3f}', ha='center', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Değer', fontsize=11)
    ax.set_title('Kategorik Performans Metrikleri', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.15)
    ax.grid(True, axis='y', alpha=0.3)
    
    # 4. Karışıklık matrisi ısı haritası
    ax = axes[1, 1]
    km = metrikler['Karisiklik_Matrisi']
    kat_isimleri = ['Düşük', 'Orta', 'Yüksek']
    
    sns.heatmap(km, annot=True, fmt='d', cmap='Blues', ax=ax,
               xticklabels=kat_isimleri, yticklabels=kat_isimleri)
    ax.set_xlabel('Temel Model Tahmini', fontsize=11)
    ax.set_ylabel('Bulanık Mantık (Gerçek)', fontsize=11)
    ax.set_title('Karışıklık Matrisi', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Karşılaştırma grafikleri kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def kural_aktivasyon_diyagrami(fis, guven, paylasim, duygu, merkezlilik, kaydet_yolu=None):
    """
    Belirli girişler için kural aktivasyon diyagramı oluşturur.
    """
    uyelikler = fis.kural_ateslemelerini_al(guven, paylasim, duygu, merkezlilik)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Kural Aktivasyon Diyagramı\n'
                f'(g={guven:.2f}, p={paylasim:.0f}, d={duygu:.2f}, m={merkezlilik:.2f})',
                fontsize=14, fontweight='bold', y=1.02)
    
    turkce_degiskenler = {
        'guven': ('Güven Skoru', guven),
        'paylasim': ('Paylaşım Sıklığı', paylasim),
        'duygu': ('Duygu Sapması', duygu),
        'merkezlilik': ('Merkezlilik Skoru', merkezlilik)
    }
    
    renkler = {'dusuk': '#2ecc71', 'orta': '#f39c12', 'yuksek': '#e74c3c',
               'kararli': '#2ecc71', 'degisken': '#e74c3c'}
    
    turkce_terimler = {
        'dusuk': 'Düşük', 'orta': 'Orta', 'yuksek': 'Yüksek',
        'kararli': 'Kararlı', 'degisken': 'Değişken'
    }
    
    for idx, (deg_adi, terimler) in enumerate(uyelikler.items()):
        satir, sutun = divmod(idx, 2)
        ax = axes[satir, sutun]
        
        isim, deger = turkce_degiskenler[deg_adi]
        
        terim_isimleri = [turkce_terimler.get(t, t) for t in terimler.keys()]
        degerler = list(terimler.values())
        bar_renkleri = [renkler.get(t, '#3498db') for t in terimler.keys()]
        
        bars = ax.bar(terim_isimleri, degerler, color=bar_renkleri, 
                     edgecolor='white', width=0.5)
        
        for bar, d in zip(bars, degerler):
            if d > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       f'{d:.3f}', ha='center', fontsize=10, fontweight='bold')
        
        ax.set_title(f'{isim} = {deger:.2f}', fontsize=12, fontweight='bold')
        ax.set_ylabel('Üyelik Derecesi μ(x)', fontsize=10)
        ax.set_ylim(0, 1.15)
        ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if kaydet_yolu:
        _dizin_kontrol(kaydet_yolu)
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Kural aktivasyon diyagramı kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def tum_grafikleri_uret(fis, risk_degerleri=None, bulanik_riskler=None,
                        temel_riskler=None, metrikler=None, cikti_dizini=None):
    """
    Tüm grafikleri üretir ve kaydeder.
    
    Parametreler
    ------------
    fis : BulanikCikarimSistemi
    risk_degerleri : numpy.ndarray
    bulanik_riskler : numpy.ndarray
    temel_riskler : numpy.ndarray
    metrikler : dict
    cikti_dizini : str
    """
    if cikti_dizini is None:
        cikti_dizini = CIKTI_DIZINI
    
    os.makedirs(cikti_dizini, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("TÜM GRAFİKLER ÜRETİLİYOR")
    print("=" * 60)
    
    # 1. Üyelik fonksiyonları
    from fuzzy_system.membership import uyelik_fonksiyonlarini_ciz, uyelik_tiplerini_karsilastir
    uyelik_fonksiyonlarini_ciz(
        fis.degiskenler,
        os.path.join(cikti_dizini, "01_uyelik_fonksiyonlari.png")
    )
    
    # 2. Üyelik tipi karşılaştırması
    uyelik_tiplerini_karsilastir(
        os.path.join(cikti_dizini, "02_uyelik_tipi_karsilastirmasi.png")
    )
    
    # 3. 3D yüzey grafikleri
    yuzey_ciftleri = [
        ('guven_skoru', 'paylasim_sikligi'),
        ('guven_skoru', 'merkezlilik_skoru'),
        ('paylasim_sikligi', 'merkezlilik_skoru'),
    ]
    
    for i, (d1, d2) in enumerate(yuzey_ciftleri, 1):
        yuzey_grafigi_3d(
            fis, d1, d2,
            kaydet_yolu=os.path.join(cikti_dizini, f"03_yuzey_3d_{i}.png")
        )
    
    # 4. Isı haritaları
    isi_ciftleri = [
        ('guven_skoru', 'merkezlilik_skoru'),
        ('guven_skoru', 'paylasim_sikligi'),
    ]
    
    for i, (d1, d2) in enumerate(isi_ciftleri, 1):
        isi_haritasi(
            fis, d1, d2,
            kaydet_yolu=os.path.join(cikti_dizini, f"04_isi_haritasi_{i}.png")
        )
    
    # 5. Risk dağılımı
    if risk_degerleri is not None:
        risk_dagilimi(
            risk_degerleri,
            kaydet_yolu=os.path.join(cikti_dizini, "05_risk_dagilimi.png")
        )
    
    # 6. Giriş-çıkış örnekleri
    giris_cikis_ornekleri(
        fis,
        kaydet_yolu=os.path.join(cikti_dizini, "06_giris_cikis_ornekleri.png")
    )
    
    # 7. Duyarlılık grafikleri
    duyarlilik_grafikleri(
        fis,
        kaydet_yolu=os.path.join(cikti_dizini, "07_duyarlilik_analizi.png")
    )
    
    # 8. Karşılaştırma grafikleri
    if bulanik_riskler is not None and temel_riskler is not None and metrikler is not None:
        karsilastirma_grafikleri(
            bulanik_riskler, temel_riskler, metrikler,
            kaydet_yolu=os.path.join(cikti_dizini, "08_model_karsilastirma.png")
        )
    
    # 9. Kural aktivasyon diyagramı
    kural_aktivasyon_diyagrami(
        fis, guven=0.3, paylasim=35, duygu=0.7, merkezlilik=0.8,
        kaydet_yolu=os.path.join(cikti_dizini, "09_kural_aktivasyon.png")
    )
    
    print("\n" + "=" * 60)
    print(f"TÜM GRAFİKLER ÜRETİLDİ: {cikti_dizini}")
    print("=" * 60)


if __name__ == "__main__":
    from fuzzy_system.inference import BulanikCikarimSistemi
    
    fis = BulanikCikarimSistemi('karisik')
    
    # Test grafikleri
    os.makedirs(CIKTI_DIZINI, exist_ok=True)
    
    duyarlilik_grafikleri(
        fis,
        kaydet_yolu=os.path.join(CIKTI_DIZINI, "test_duyarlilik.png")
    )
    
    giris_cikis_ornekleri(
        fis,
        kaydet_yolu=os.path.join(CIKTI_DIZINI, "test_ornekler.png")
    )
    
    print("\n[TEST] Görselleştirme modülü başarıyla çalıştı!")
