# -*- coding: utf-8 -*-
"""
Üyelik Fonksiyonları Modülü
============================
Bulanık mantık sistemi için üyelik fonksiyonlarını tanımlar.
Her giriş/çıkış değişkeni için üçgensel (trimf) ve yamuksal (trapmf) 
üyelik fonksiyonları kullanılır.

Değişkenler
-----------
1. Güven Skoru (Trust Score) ∈ [0, 1]
   - Düşük, Orta, Yüksek
2. Paylaşım Sıklığı (Posting Frequency) ∈ [0, 50]
   - Düşük, Orta, Yüksek
3. Duygu Sapması (Sentiment Deviation) ∈ [-1, +1]
   - Kararlı (Stable), Orta (Moderate), Değişken (Volatile)
4. Merkezlilik Skoru (Centrality Score) ∈ [0, 1]
   - Düşük, Orta, Yüksek
5. Risk Seviyesi (Risk Level) ∈ [0, 1]
   - Düşük, Orta, Yüksek

Üyelik Fonksiyon Türleri
-------------------------
- Üçgensel (Triangular - trimf): 3 parametre [a, b, c]
  μ(x) = max(min((x-a)/(b-a), (c-x)/(c-b)), 0)
  
- Yamuksal (Trapezoidal - trapmf): 4 parametre [a, b, c, d]
  μ(x) = max(min((x-a)/(b-a), 1, (d-x)/(d-c)), 0)
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


def degiskenleri_olustur():
    """
    Bulanık sistem için giriş ve çıkış değişkenlerini oluşturur.
    
    Döndürür
    --------
    degiskenler : dict
        'guven', 'paylasim', 'duygu', 'merkezlilik', 'risk' anahtarlarıyla
        Antecedent/Consequent nesneleri.
    """
    # Evrensel kümeler (Universe of Discourse)
    guven = ctrl.Antecedent(np.linspace(0, 1, 1001), 'guven_skoru')
    paylasim = ctrl.Antecedent(np.linspace(0, 50, 1001), 'paylasim_sikligi')
    duygu = ctrl.Antecedent(np.linspace(-1, 1, 1001), 'duygu_sapmasi')
    merkezlilik = ctrl.Antecedent(np.linspace(0, 1, 1001), 'merkezlilik_skoru')
    risk = ctrl.Consequent(np.linspace(0, 1, 1001), 'risk_seviyesi')
    
    return {
        'guven': guven,
        'paylasim': paylasim,
        'duygu': duygu,
        'merkezlilik': merkezlilik,
        'risk': risk
    }


def uyelik_fonksiyonlarini_tanimla(degiskenler, fonksiyon_tipi='karisik'):
    """
    Tüm değişkenler için üyelik fonksiyonlarını tanımlar.
    
    Parametreler
    ------------
    degiskenler : dict
        degiskenleri_olustur() fonksiyonundan dönen sözlük.
    fonksiyon_tipi : str
        'ucgensel' (trimf), 'yamuksal' (trapmf), veya 'karisik' (ikisinin karışımı).
    
    Döndürür
    --------
    degiskenler : dict
        Üyelik fonksiyonları tanımlanmış değişkenler.
    """
    guven = degiskenler['guven']
    paylasim = degiskenler['paylasim']
    duygu = degiskenler['duygu']
    merkezlilik = degiskenler['merkezlilik']
    risk = degiskenler['risk']
    
    if fonksiyon_tipi == 'ucgensel':
        _ucgensel_uyelik(guven, paylasim, duygu, merkezlilik, risk)
    elif fonksiyon_tipi == 'yamuksal':
        _yamuksal_uyelik(guven, paylasim, duygu, merkezlilik, risk)
    else:  # karisik (varsayılan)
        _karisik_uyelik(guven, paylasim, duygu, merkezlilik, risk)
    
    return degiskenler


def _ucgensel_uyelik(guven, paylasim, duygu, merkezlilik, risk):
    """
    Tüm değişkenler için üçgensel (triangular) üyelik fonksiyonları.
    
    Üçgensel Fonksiyon: trimf([a, b, c])
    ─────────────────────────────────────
    μ(x) = 0          , x ≤ a veya x ≥ c
    μ(x) = (x-a)/(b-a), a < x ≤ b
    μ(x) = (c-x)/(c-b), b < x < c
    """
    # ═══ GÜVEN SKORU [0, 1] ═══
    # Düşük güven: sol uçta yoğun, 0.4'e kadar azalır
    guven['dusuk'] = fuzz.trimf(guven.universe, [0, 0, 0.4])
    # Orta güven: 0.2-0.8 arası, tepe 0.5
    guven['orta'] = fuzz.trimf(guven.universe, [0.2, 0.5, 0.8])
    # Yüksek güven: 0.6'dan başlar, sağ uçta yoğun
    guven['yuksek'] = fuzz.trimf(guven.universe, [0.6, 1, 1])
    
    # ═══ PAYLAŞIM SIKLIĞI [0, 50] ═══
    # Düşük: 0-15 arası
    paylasim['dusuk'] = fuzz.trimf(paylasim.universe, [0, 0, 15])
    # Orta: 8-35 arası, tepe 20
    paylasim['orta'] = fuzz.trimf(paylasim.universe, [8, 20, 35])
    # Yüksek: 25-50 arası
    paylasim['yuksek'] = fuzz.trimf(paylasim.universe, [25, 50, 50])
    
    # ═══ DUYGU SAPMASI [-1, +1] ═══
    # Kararlı: sapma düşük, merkeze yakın
    duygu['kararli'] = fuzz.trimf(duygu.universe, [-0.4, 0, 0.4])
    # Orta: orta düzeyde sapma (pozitif veya negatif)
    duygu['orta'] = fuzz.trimf(duygu.universe, [0.2, 0.5, 0.8])
    # Değişken: yüksek sapma
    duygu['degisken'] = fuzz.trimf(duygu.universe, [0.5, 1, 1])
    
    # Negatif taraftaki orta ve değişken
    duygu_orta_neg = fuzz.trimf(duygu.universe, [-0.8, -0.5, -0.2])
    duygu_degisken_neg = fuzz.trimf(duygu.universe, [-1, -1, -0.5])
    
    # Simetrik birleştirme: |sapma| olarak değerlendiriyoruz
    duygu['orta'] = np.maximum(duygu['orta'].mf, duygu_orta_neg)
    duygu['degisken'] = np.maximum(duygu['degisken'].mf, duygu_degisken_neg)
    
    # ═══ MERKEZLİLİK SKORU [0, 1] ═══
    merkezlilik['dusuk'] = fuzz.trimf(merkezlilik.universe, [0, 0, 0.4])
    merkezlilik['orta'] = fuzz.trimf(merkezlilik.universe, [0.2, 0.5, 0.8])
    merkezlilik['yuksek'] = fuzz.trimf(merkezlilik.universe, [0.6, 1, 1])
    
    # ═══ RİSK SEVİYESİ [0, 1] ═══
    risk['dusuk'] = fuzz.trimf(risk.universe, [0, 0, 0.4])
    risk['orta'] = fuzz.trimf(risk.universe, [0.2, 0.5, 0.8])
    risk['yuksek'] = fuzz.trimf(risk.universe, [0.6, 1, 1])


def _yamuksal_uyelik(guven, paylasim, duygu, merkezlilik, risk):
    """
    Tüm değişkenler için yamuksal (trapezoidal) üyelik fonksiyonları.
    
    Yamuksal Fonksiyon: trapmf([a, b, c, d])
    ──────────────────────────────────────────
    μ(x) = 0            , x ≤ a veya x ≥ d
    μ(x) = (x-a)/(b-a)  , a < x ≤ b
    μ(x) = 1            , b < x ≤ c
    μ(x) = (d-x)/(d-c)  , c < x < d
    """
    # ═══ GÜVEN SKORU [0, 1] ═══
    guven['dusuk'] = fuzz.trapmf(guven.universe, [0, 0, 0.2, 0.45])
    guven['orta'] = fuzz.trapmf(guven.universe, [0.25, 0.4, 0.6, 0.75])
    guven['yuksek'] = fuzz.trapmf(guven.universe, [0.55, 0.8, 1, 1])
    
    # ═══ PAYLAŞIM SIKLIĞI [0, 50] ═══
    paylasim['dusuk'] = fuzz.trapmf(paylasim.universe, [0, 0, 5, 15])
    paylasim['orta'] = fuzz.trapmf(paylasim.universe, [10, 18, 28, 35])
    paylasim['yuksek'] = fuzz.trapmf(paylasim.universe, [28, 38, 50, 50])
    
    # ═══ DUYGU SAPMASI [-1, +1] ═══
    duygu['kararli'] = fuzz.trapmf(duygu.universe, [-0.3, -0.1, 0.1, 0.3])
    
    duygu_orta_poz = fuzz.trapmf(duygu.universe, [0.15, 0.35, 0.55, 0.75])
    duygu_orta_neg = fuzz.trapmf(duygu.universe, [-0.75, -0.55, -0.35, -0.15])
    duygu['orta'] = np.maximum(duygu_orta_poz, duygu_orta_neg)
    
    duygu_degisken_poz = fuzz.trapmf(duygu.universe, [0.55, 0.75, 1, 1])
    duygu_degisken_neg = fuzz.trapmf(duygu.universe, [-1, -1, -0.75, -0.55])
    duygu['degisken'] = np.maximum(duygu_degisken_poz, duygu_degisken_neg)
    
    # ═══ MERKEZLİLİK SKORU [0, 1] ═══
    merkezlilik['dusuk'] = fuzz.trapmf(merkezlilik.universe, [0, 0, 0.2, 0.45])
    merkezlilik['orta'] = fuzz.trapmf(merkezlilik.universe, [0.25, 0.4, 0.6, 0.75])
    merkezlilik['yuksek'] = fuzz.trapmf(merkezlilik.universe, [0.55, 0.8, 1, 1])
    
    # ═══ RİSK SEVİYESİ [0, 1] ═══
    risk['dusuk'] = fuzz.trapmf(risk.universe, [0, 0, 0.2, 0.45])
    risk['orta'] = fuzz.trapmf(risk.universe, [0.25, 0.4, 0.6, 0.75])
    risk['yuksek'] = fuzz.trapmf(risk.universe, [0.55, 0.8, 1, 1])


def _karisik_uyelik(guven, paylasim, duygu, merkezlilik, risk):
    """
    Karışık üyelik fonksiyonları: uç değerler için yamuksal, orta için üçgensel.
    Bu yaklaşım, uç terimlerin düz bölgeleri ile daha doğal modellemeler sağlar.
    """
    # ═══ GÜVEN SKORU [0, 1] ═══
    # Düşük: yamuksal (sol uçta düz bölge)
    guven['dusuk'] = fuzz.trapmf(guven.universe, [0, 0, 0.15, 0.4])
    # Orta: üçgensel (tek tepe noktası)
    guven['orta'] = fuzz.trimf(guven.universe, [0.2, 0.5, 0.8])
    # Yüksek: yamuksal (sağ uçta düz bölge)
    guven['yuksek'] = fuzz.trapmf(guven.universe, [0.6, 0.85, 1, 1])
    
    # ═══ PAYLAŞIM SIKLIĞI [0, 50] ═══
    paylasim['dusuk'] = fuzz.trapmf(paylasim.universe, [0, 0, 5, 15])
    paylasim['orta'] = fuzz.trimf(paylasim.universe, [8, 20, 35])
    paylasim['yuksek'] = fuzz.trapmf(paylasim.universe, [25, 40, 50, 50])
    
    # ═══ DUYGU SAPMASI [-1, +1] ═══
    # Kararlı: merkeze yakın, düz bölge
    duygu['kararli'] = fuzz.trapmf(duygu.universe, [-0.3, -0.1, 0.1, 0.3])
    
    # Orta: simetrik, orta şiddette sapma
    duygu_orta_poz = fuzz.trimf(duygu.universe, [0.15, 0.45, 0.75])
    duygu_orta_neg = fuzz.trimf(duygu.universe, [-0.75, -0.45, -0.15])
    duygu['orta'] = np.maximum(duygu_orta_poz, duygu_orta_neg)
    
    # Değişken: simetrik, yüksek sapma (uçlarda yamuksal)
    duygu_degisken_poz = fuzz.trapmf(duygu.universe, [0.55, 0.75, 1, 1])
    duygu_degisken_neg = fuzz.trapmf(duygu.universe, [-1, -1, -0.75, -0.55])
    duygu['degisken'] = np.maximum(duygu_degisken_poz, duygu_degisken_neg)
    
    # ═══ MERKEZLİLİK SKORU [0, 1] ═══
    merkezlilik['dusuk'] = fuzz.trapmf(merkezlilik.universe, [0, 0, 0.15, 0.4])
    merkezlilik['orta'] = fuzz.trimf(merkezlilik.universe, [0.2, 0.5, 0.8])
    merkezlilik['yuksek'] = fuzz.trapmf(merkezlilik.universe, [0.6, 0.85, 1, 1])
    
    # ═══ RİSK SEVİYESİ [0, 1] ═══
    risk['dusuk'] = fuzz.trapmf(risk.universe, [0, 0, 0.15, 0.4])
    risk['orta'] = fuzz.trimf(risk.universe, [0.2, 0.5, 0.8])
    risk['yuksek'] = fuzz.trapmf(risk.universe, [0.6, 0.85, 1, 1])


def uyelik_fonksiyonlarini_ciz(degiskenler, kaydet_yolu=None):
    """
    Tüm değişkenlerin üyelik fonksiyonlarını çizer.
    
    Parametreler
    ------------
    degiskenler : dict
        Üyelik fonksiyonları tanımlanmış değişkenler.
    kaydet_yolu : str, opsiyonel
        Grafik dosyasının kaydedileceği yol.
    """
    turkce_isimler = {
        'guven': ('Güven Skoru', '[0, 1]'),
        'paylasim': ('Paylaşım Sıklığı', '[0, 50] gönderi/gün'),
        'duygu': ('Duygu Sapması', '[-1, +1]'),
        'merkezlilik': ('Merkezlilik Skoru', '[0, 1]'),
        'risk': ('Risk Seviyesi', '[0, 1]')
    }
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('Üyelik Fonksiyonları', fontsize=16, fontweight='bold', y=0.98)
    
    renkler = {'dusuk': '#2ecc71', 'orta': '#f39c12', 'yuksek': '#e74c3c',
               'kararli': '#2ecc71', 'degisken': '#e74c3c'}
    
    for idx, (anahtar, degisken) in enumerate(degiskenler.items()):
        satir, sutun = divmod(idx, 2)
        ax = axes[satir, sutun]
        
        isim, birim = turkce_isimler.get(anahtar, (anahtar, ''))
        
        for terim in degisken.terms:
            renk = renkler.get(terim, '#3498db')
            terim_turkce = _terim_cevirisi(terim)
            ax.plot(degisken.universe, degisken[terim].mf,
                    linewidth=2.5, label=terim_turkce, color=renk)
            ax.fill_between(degisken.universe, degisken[terim].mf,
                           alpha=0.15, color=renk)
        
        ax.set_title(f'{isim} {birim}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Değer', fontsize=10)
        ax.set_ylabel('Üyelik Derecesi μ(x)', fontsize=10)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.05, 1.15)
    
    # Son alt grafı gizle (5 değişken, 6 alan)
    axes[2, 1].set_visible(False)
    
    plt.tight_layout()
    
    if kaydet_yolu:
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Üyelik fonksiyonları kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def uyelik_tiplerini_karsilastir(kaydet_yolu=None):
    """
    Üçgensel ve yamuksal üyelik fonksiyonlarını karşılaştırır.
    
    Aynı değişken (Güven Skoru) için her iki tipi yan yana gösterir.
    
    Parametreler
    ------------
    kaydet_yolu : str, opsiyonel
        Grafik dosyasının kaydedileceği yol.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Üyelik Fonksiyonu Tiplerinin Karşılaştırması (Güven Skoru)',
                 fontsize=14, fontweight='bold')
    
    x = np.linspace(0, 1, 1001)
    tipler = ['Üçgensel (trimf)', 'Yamuksal (trapmf)', 'Karışık']
    
    renkler = ['#2ecc71', '#f39c12', '#e74c3c']
    etiketler = ['Düşük', 'Orta', 'Yüksek']
    
    # Üçgensel
    ucgensel = [
        fuzz.trimf(x, [0, 0, 0.4]),
        fuzz.trimf(x, [0.2, 0.5, 0.8]),
        fuzz.trimf(x, [0.6, 1, 1])
    ]
    
    # Yamuksal
    yamuksal = [
        fuzz.trapmf(x, [0, 0, 0.2, 0.45]),
        fuzz.trapmf(x, [0.25, 0.4, 0.6, 0.75]),
        fuzz.trapmf(x, [0.55, 0.8, 1, 1])
    ]
    
    # Karışık
    karisik = [
        fuzz.trapmf(x, [0, 0, 0.15, 0.4]),
        fuzz.trimf(x, [0.2, 0.5, 0.8]),
        fuzz.trapmf(x, [0.6, 0.85, 1, 1])
    ]
    
    tum_tipler = [ucgensel, yamuksal, karisik]
    
    for i, (tip_verileri, tip_adi) in enumerate(zip(tum_tipler, tipler)):
        ax = axes[i]
        for j, (mf, etiket) in enumerate(zip(tip_verileri, etiketler)):
            ax.plot(x, mf, linewidth=2.5, label=etiket, color=renkler[j])
            ax.fill_between(x, mf, alpha=0.15, color=renkler[j])
        
        ax.set_title(tip_adi, fontsize=12, fontweight='bold')
        ax.set_xlabel('Güven Skoru', fontsize=10)
        ax.set_ylabel('Üyelik Derecesi μ(x)', fontsize=10)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.05, 1.15)
    
    plt.tight_layout()
    
    if kaydet_yolu:
        plt.savefig(kaydet_yolu, dpi=150, bbox_inches='tight')
        print(f"[GÖRSELLEŞTİRME] Karşılaştırma grafiği kaydedildi: {kaydet_yolu}")
    
    plt.close()
    return fig


def _terim_cevirisi(terim):
    """Terim adlarını Türkçe'ye çevirir."""
    ceviriler = {
        'dusuk': 'Düşük',
        'orta': 'Orta',
        'yuksek': 'Yüksek',
        'kararli': 'Kararlı',
        'degisken': 'Değişken'
    }
    return ceviriler.get(terim, terim.capitalize())


if __name__ == "__main__":
    import os
    
    # Test: Karışık üyelik fonksiyonları
    degiskenler = degiskenleri_olustur()
    degiskenler = uyelik_fonksiyonlarini_tanimla(degiskenler, 'karisik')
    
    # Dizin oluştur
    cikti_dizini = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "visualization", "output")
    os.makedirs(cikti_dizini, exist_ok=True)
    
    # Üyelik fonksiyonlarını çiz
    uyelik_fonksiyonlarini_ciz(
        degiskenler,
        os.path.join(cikti_dizini, "uyelik_fonksiyonlari.png")
    )
    
    # Karşılaştırma
    uyelik_tiplerini_karsilastir(
        os.path.join(cikti_dizini, "uyelik_tipi_karsilastirmasi.png")
    )
    
    print("\n[TEST] Üyelik fonksiyonları modülü başarıyla çalıştı!")
