# -*- coding: utf-8 -*-
"""
Bulanik Cikarim Motoru
========================
Mamdani tipi bulanik cikarim sistemini kurar ve calistirir.

Mamdani Yontemi Adimlari
------------------------
1. Bulaniklastirma (Fuzzification):
   Kesin giris degerlerini uyelik derecelerine donusturur.

2. Kural Degerlendirme (Rule Evaluation):
   VE (AND) -> min operatoru
   VEYA (OR) -> max operatoru

3. Toplama (Aggregation):
   Tum kurallarin cikti uyelik fonksiyonlari birlestirilir.
   mu_agg(z) = max(mu_1(z), mu_2(z), ..., mu_n(z))

4. Durulastirma (Defuzzification):
   Centroid (agirlik merkezi) yontemi:
   z* = integral z * mu_agg(z) dz / integral mu_agg(z) dz
"""

import sys
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import warnings

# Windows konsol encoding duzeltmesi
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from fuzzy_system.membership import degiskenleri_olustur, uyelik_fonksiyonlarini_tanimla
from fuzzy_system.rules import kurallari_olustur


class BulanikCikarimSistemi:
    """
    Mamdani tipi Bulanik Cikarim Sistemi (Fuzzy Inference System - FIS).
    
    Sosyal ag kullanicilarinin yanlis bilgi yayma riskini tahmin eder.
    
    Kullanim
    --------
    >>> fis = BulanikCikarimSistemi()
    >>> risk = fis.hesapla(guven=0.3, paylasim=30, duygu=0.7, merkezlilik=0.8)
    >>> print(f"Risk: {risk:.4f}")
    """
    
    def __init__(self, fonksiyon_tipi='karisik', aktif_girdiler=None):
        """
        Bulanik cikarim sistemini baslatir.
        
        Parametreler
        ------------
        fonksiyon_tipi : str
            Uyelik fonksiyonu tipi: 'ucgensel', 'yamuksal', veya 'karisik'.
        aktif_girdiler : list, opsiyonel
            Baslangicta aktif olan degiskenlerin listesi. Eger None ise
            tum 4 degisken aktif kabul edilir.
        """
        self.fonksiyon_tipi = fonksiyon_tipi
        if aktif_girdiler is None:
            self.aktif_girdiler = ['guven', 'paylasim', 'duygu', 'merkezlilik']
        else:
            self.aktif_girdiler = aktif_girdiler
            
        self._sistem_kur()
        
    def aktif_girdileri_ayarla(self, aktif_liste):
        """
        Hesaplamalara dahil edilecek degiskenleri secer ve kontrol sistemini 
        buna gore dinamik olarak yeniden derler.
        """
        if not aktif_liste:
            warnings.warn("En az 1 girdi secilmelidir. Varsayilan tum girdiler kullanilacak.")
            self.aktif_girdiler = ['guven', 'paylasim', 'duygu', 'merkezlilik']
        else:
            self.aktif_girdiler = aktif_liste
            
        self._sistem_kur()
    
    def _sistem_kur(self):
        """Bulanik sistemi kurar."""
        print(f"[FIS] Bulanik cikarim sistemi kuruluyor (tip: {self.fonksiyon_tipi})...")
        
        # 1. Degiskenleri olustur
        self.degiskenler = degiskenleri_olustur()
        
        # 2. Uyelik fonksiyonlarini tanimla
        self.degiskenler = uyelik_fonksiyonlarini_tanimla(
            self.degiskenler, self.fonksiyon_tipi
        )
        
        # 3. Kurallari olustur (aktif olanlari dinamik on-the-fly kirparak)
        self.kurallar, self.kural_aciklamalari = kurallari_olustur(
            self.degiskenler, 
            aktif_degiskenler=self.aktif_girdiler
        )
        
        # 4. Kontrol sistemi olustur
        if len(self.kurallar) > 0:
            self.kontrol_sistemi = ctrl.ControlSystem(self.kurallar)
        else:
            self.kontrol_sistemi = None
            print("[FIS] Uyari: Secilen girdilerle aktif kalan hic kural yok!")
        
        print(f"[FIS] Sistem hazir: {len(self.kurallar)} kural, "
              f"tip: {self.fonksiyon_tipi}")
    
    def hesapla(self, guven, paylasim, duygu, merkezlilik):
        """
        Tek bir giris seti icin risk seviyesini hesaplar.
        
        Parametreler
        ------------
        guven : float - Guven skoru [0, 1].
        paylasim : float - Paylasim sikligi [0, 50].
        duygu : float - Duygu sapmasi [-1, +1].
        merkezlilik : float - Merkezlilik skoru [0, 1].
        
        Dondurur
        --------
        risk : float - Hesaplanan risk seviyesi [0, 1].
        """
        try:
            if self.kontrol_sistemi is None:
                return 0.5  # Gecerli kural olmadiginda varsayilan deger
                
            # Her hesaplamada yeni simulasyon olustur (state reset sorunu icin)
            sim = ctrl.ControlSystemSimulation(self.kontrol_sistemi)
            
            if 'guven' in self.aktif_girdiler:
                sim.input['guven_skoru'] = np.clip(float(guven), 0.001, 0.999)
                
            if 'paylasim' in self.aktif_girdiler:
                sim.input['paylasim_sikligi'] = np.clip(float(paylasim), 0.1, 49.9)
                
            if 'duygu' in self.aktif_girdiler:
                sim.input['duygu_sapmasi'] = np.clip(float(duygu), -0.999, 0.999)
                
            if 'merkezlilik' in self.aktif_girdiler:
                sim.input['merkezlilik_skoru'] = np.clip(float(merkezlilik), 0.001, 0.999)
            
            sim.compute()
            
            risk = sim.output['risk_seviyesi']
            return np.clip(risk, 0, 1)
            
        except Exception as e:
            warnings.warn(f"Bulanik cikarim hatasi (g={guven}, p={paylasim}, "
                         f"d={duygu}, m={merkezlilik}): {e}")
            return 0.5
    
    def toplu_hesapla(self, df):
        """
        DataFrame uzerinde toplu risk hesaplamasi yapar.
        """
        print(f"[FIS] Toplu hesaplama basliyor: {len(df)} ornek...")
        
        riskler = np.zeros(len(df))
        basarili = 0
        hatali = 0
        
        for i in range(len(df)):
            satir = df.iloc[i]
            risk = self.hesapla(
                guven=satir['guven_skoru'],
                paylasim=satir['paylasim_sikligi'],
                duygu=satir['duygu_sapmasi'],
                merkezlilik=satir['merkezlilik_skoru']
            )
            riskler[i] = risk
            
            if risk != 0.5:
                basarili += 1
            else:
                hatali += 1
            
            if (i + 1) % 200 == 0 or (i + 1) == len(df):
                print(f"       Ilerleme: {i+1}/{len(df)} "
                      f"({(i+1)/len(df)*100:.1f}%)")
        
        print(f"[FIS] Toplu hesaplama tamamlandi: "
              f"{basarili} basarili, {hatali} hatali")
        print(f"       Risk araligi: [{riskler.min():.4f}, {riskler.max():.4f}]")
        print(f"       Ortalama risk: {riskler.mean():.4f}")
        
        return riskler
    
    def kural_ateslemelerini_al(self, guven, paylasim, duygu, merkezlilik):
        """
        Verilen girisler icin aktif her degiskenin uyelik derecelerini hesaplar.
        """
        g = self.degiskenler['guven']
        p = self.degiskenler['paylasim']
        d = self.degiskenler['duygu']
        m = self.degiskenler['merkezlilik']
        
        uyelikler = {}
        
        if 'guven' in self.aktif_girdiler:
            uyelikler['guven'] = {}
            for terim in g.terms:
                uyelikler['guven'][terim] = float(fuzz.interp_membership(
                    g.universe, g[terim].mf, guven))
        
        if 'paylasim' in self.aktif_girdiler:
            uyelikler['paylasim'] = {}
            for terim in p.terms:
                uyelikler['paylasim'][terim] = float(fuzz.interp_membership(
                    p.universe, p[terim].mf, paylasim))
        
        if 'duygu' in self.aktif_girdiler:
            uyelikler['duygu'] = {}
            for terim in d.terms:
                uyelikler['duygu'][terim] = float(fuzz.interp_membership(
                    d.universe, d[terim].mf, duygu))
        
        if 'merkezlilik' in self.aktif_girdiler:
            uyelikler['merkezlilik'] = {}
            for terim in m.terms:
                uyelikler['merkezlilik'][terim] = float(fuzz.interp_membership(
                    m.universe, m[terim].mf, merkezlilik))
        
        return uyelikler
    
    def ara_sonuclari_al(self, guven, paylasim, duygu, merkezlilik):
        """
        Adim adim cikarim ara sonuclarini dondurur.
        Aciklanabilir AI modu icin kullanilir.
        """
        risk = self.hesapla(guven, paylasim, duygu, merkezlilik)
        uyelikler = self.kural_ateslemelerini_al(guven, paylasim, duygu, merkezlilik)
        
        if risk < 0.35:
            kategori = 'DUSUK'
            renk = '[DUSUK]'
        elif risk < 0.65:
            kategori = 'ORTA'
            renk = '[ORTA]'
        else:
            kategori = 'YUKSEK'
            renk = '[YUKSEK]'
        
        sonuclar = {
            'girisler': {
                'guven_skoru': guven,
                'paylasim_sikligi': paylasim,
                'duygu_sapmasi': duygu,
                'merkezlilik_skoru': merkezlilik
            },
            'uyelik_dereceleri': uyelikler,
            'risk_skoru': risk,
            'risk_kategorisi': kategori,
            'risk_renk': renk,
            'kural_aciklamalari': self.kural_aciklamalari
        }
        
        return sonuclar
    
    def adim_adim_goster(self, guven, paylasim, duygu, merkezlilik):
        """
        Cikarim surecini adim adim konsola yazdirir.
        """
        sonuclar = self.ara_sonuclari_al(guven, paylasim, duygu, merkezlilik)
        
        print("\n" + "=" * 70)
        print("     BULANIK CIKARIM SURECI - ADIM ADIM GOSTERIM")
        print("=" * 70)
        
        # Adim 1: Girisler
        print("\n ADIM 1: GIRIS DEGERLERI")
        print("-" * 40)
        g = sonuclar['girisler']
        if 'guven' in self.aktif_girdiler:
            print(f"  Guven Skoru      : {g['guven_skoru']:.4f}")
        if 'paylasim' in self.aktif_girdiler:
            print(f"  Paylasim Sikligi : {g['paylasim_sikligi']:.1f} gonderi/gun")
        if 'duygu' in self.aktif_girdiler:
            print(f"  Duygu Sapmasi    : {g['duygu_sapmasi']:.4f}")
        if 'merkezlilik' in self.aktif_girdiler:
            print(f"  Merkezlilik Skoru : {g['merkezlilik_skoru']:.4f}")
        
        # Adim 2: Bulaniklastirma
        print("\n ADIM 2: BULANIKLASTIRMA (Fuzzification)")
        print("-" * 40)
        
        turkce_terimler = {
            'dusuk': 'Dusuk', 'orta': 'Orta', 'yuksek': 'Yuksek',
            'kararli': 'Kararli', 'degisken': 'Degisken'
        }
        turkce_degiskenler = {
            'guven': 'Guven', 'paylasim': 'Paylasim',
            'duygu': 'Duygu', 'merkezlilik': 'Merkezlilik'
        }
        
        for deg_adi, terimler in sonuclar['uyelik_dereceleri'].items():
            deg_turkce = turkce_degiskenler.get(deg_adi, deg_adi)
            print(f"\n  {deg_turkce}:")
            for terim, derece in terimler.items():
                terim_turkce = turkce_terimler.get(terim, terim)
                bar = '#' * int(derece * 20) + '.' * (20 - int(derece * 20))
                print(f"    {terim_turkce:10s}: mu = {derece:.4f} |{bar}|")
        
        # Adim 3
        print("\n ADIM 3: KURAL DEGERLENDIRME")
        print("-" * 40)
        print(f"  Toplam kural sayisi: {len(self.kurallar)}")
        print(f"  VE (AND) operatoru : min")
        print(f"  VEYA (OR) operatoru: max")
        
        # Adim 4
        print("\n ADIM 4: TOPLAMA (Aggregation)")
        print("-" * 40)
        print(f"  Yontem: Maksimum (max)")
        
        # Adim 5
        print("\n ADIM 5: DURULASTIRMA (Defuzzification)")
        print("-" * 40)
        print(f"  Yontem: Agirlik Merkezi (Centroid)")
        print(f"  z* = integral z * mu_agg(z) dz / integral mu_agg(z) dz")
        
        # Sonuc
        risk = sonuclar['risk_skoru']
        kat = sonuclar['risk_kategorisi']
        renk = sonuclar['risk_renk']
        
        print("\n" + "=" * 70)
        print(f"  {renk} SONUC: Risk Seviyesi = {risk:.4f} ({kat})")
        print("=" * 70 + "\n")
        
        return sonuclar


def sistemi_olustur(fonksiyon_tipi='karisik'):
    """Bulanik cikarim sistemi fabrika fonksiyonu."""
    return BulanikCikarimSistemi(fonksiyon_tipi)


if __name__ == "__main__":
    fis = BulanikCikarimSistemi('karisik')
    
    print("\n--- Tek Hesaplama Testi ---")
    test_senaryolari = [
        (0.2, 35, 0.8, 0.9, "Yuksek Riskli Profil"),
        (0.9, 5, 0.1, 0.2, "Dusuk Riskli Profil"),
        (0.5, 20, 0.4, 0.5, "Orta Riskli Profil"),
        (0.1, 45, 0.9, 0.8, "Maksimum Riskli Profil"),
        (0.95, 2, 0.05, 0.1, "Minimum Riskli Profil"),
    ]
    
    for guven, paylasim, duygu, merkezlilik, aciklama in test_senaryolari:
        risk = fis.hesapla(guven, paylasim, duygu, merkezlilik)
        kat = 'DUSUK' if risk < 0.35 else ('ORTA' if risk < 0.65 else 'YUKSEK')
        print(f"  {aciklama:25s}: g={guven:.2f} p={paylasim:2.0f} "
              f"d={duygu:.2f} m={merkezlilik:.2f} -> Risk={risk:.4f} ({kat})")
    
    print("\n--- Adim Adim Gosterim ---")
    fis.adim_adim_goster(guven=0.2, paylasim=35, duygu=0.8, merkezlilik=0.9)
    
    print("\n[TEST] Bulanik cikarim motoru basariyla calisti!")
