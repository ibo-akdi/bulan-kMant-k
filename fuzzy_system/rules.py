# -*- coding: utf-8 -*-
"""
Kural Tabani Modulu
====================
Mamdani bulanik cikarim sistemi icin kural tabanini tanimlar.
Dinamik girdi secimini (kismi senaryo analizi) desteklemesi icin kurallar
aktif degiskenlere gore (on-the-fly) insa edilecek sekilde yapilandirilmistir.
"""

from skfuzzy import control as ctrl
import pandas as pd


def kurallari_olustur(degiskenler, aktif_degiskenler=None):
    """
    Bulanik kural tabanini olusturur. Girdisi kapatilmis degiskenleri
    otomatik olarak kurallardan ayiklar (kirpar).
    
    Parametreler
    ------------
    degiskenler : dict
        Uyelik fonksiyonlari tanimlanmis degiskenler.
    aktif_degiskenler : list, opsiyonel
        Sistemde kullanilacak (aktif olan) degiskenlerin isim (key) listesi.
        Belirtilmezse tum degiskenler aktif sayilir.
    
    Dondurur
    --------
    kurallar : list
        ctrl.Rule nesnelerinin listesi.
    kural_aciklamalari : list
        Her kural icin aciklama metni.
    """
    if aktif_degiskenler is None:
        aktif_degiskenler = ['guven', 'paylasim', 'duygu', 'merkezlilik']
        
    r = degiskenler['risk']
    kurallar = []
    kural_aciklamalari = []
    
    # Aciklamada anlasilabilirlik icin Turkce terim karsiliklari
    tr_isimler = {
        'guven': 'Guven', 'paylasim': 'Paylasim', 
        'duygu': 'Duygu', 'merkezlilik': 'Merkezlilik'
    }
    tr_terimler = {
        'dusuk': 'Dusuk', 'orta': 'Orta', 'yuksek': 'Yuksek',
        'kararli': 'Kararli', 'degisken': 'Degisken'
    }
    
    def kural_ekle(oncul_listesi, sonuc, gerekce):
        # Sadece aktif_degiskenler'e dahil olan onculleri filtrele
        gecerli_onculler = []
        gecerli_tanimlar = []
        
        for deg_adi, terim in oncul_listesi:
            if deg_adi in aktif_degiskenler:
                gecerli_onculler.append(degiskenler[deg_adi][terim])
                isim = tr_isimler[deg_adi]
                term_tr = tr_terimler[terim]
                gecerli_tanimlar.append(f"{isim}={term_tr}")
                
        # Eger kuraldaki TUM girisler kapatilmissa bu kural sistemden dusurulecek
        if not gecerli_onculler:
            return
            
        # Kalan onculleri "VE" (AND) ile birlestir
        kombine = gecerli_onculler[0]
        for onc in gecerli_onculler[1:]:
            kombine = kombine & onc
            
        kural_obj = ctrl.Rule(kombine, sonuc)
        kurallar.append(kural_obj)
        
        # Dinamik kural aciklamasi (ornek: Guven=Dusuk VE Paylasim=Yuksek -> Yuksek risk)
        oncul_metni = " VE ".join(gecerli_tanimlar)
        # sonuc stringini cikaralim (orn: r['yuksek'].label -> get term text)
        # we know 'sonuc' is an Antecedent term, so `sonuc.term.label` works, but easier to just parse the repr.
        sonuc_terim = [k for k, v in r.terms.items() if v == sonuc][0]
        sonuc_metni = f"Risk={tr_terimler[sonuc_terim]}"
        
        tam_aciklama = f"{oncul_metni} -> {sonuc_metni}: {gerekce}"
        kural_aciklamalari.append(tam_aciklama)

    # ═══════════════════════════════════════════════════════════════
    # HAM KURAL TANIMLARI
    # Format: kural_ekle([ ('deg_adi', 'terim'), ... ], sonuc_terim, gerekce)
    # ═══════════════════════════════════════════════════════════════

    # Kural 1
    kural_ekle(
        [('guven', 'dusuk'), ('paylasim', 'yuksek')], 
        r['yuksek'], "Guvenilirligi dusuk kisilerin yogun paylasimi tehlikelidir."
    )
    
    # Kural 2
    kural_ekle(
        [('guven', 'yuksek'), ('duygu', 'kararli')],
        r['dusuk'], "Guvenilir ve tutarli kullanicilar dogru bilgi paylasir."
    )
    
    # Kural 3
    kural_ekle(
        [('guven', 'dusuk'), ('duygu', 'degisken')],
        r['yuksek'], "Dusuk guven + yuksek duygusal sapma yanlis bilgi gostergesidir."
    )
    
    # Kural 4
    kural_ekle(
        [('guven', 'yuksek'), ('paylasim', 'dusuk')],
        r['dusuk'], "Guvenilir ve secici paylasimcilar guvenli kabul edilir."
    )
    
    # Kural 5
    kural_ekle(
        [('merkezlilik', 'yuksek'), ('paylasim', 'yuksek')],
        r['yuksek'], "Merkezi konumdaki yogun paylasimcilar bilgiyi hizla yayar."
    )
    
    # Kural 6
    kural_ekle(
        [('merkezlilik', 'dusuk'), ('paylasim', 'dusuk')],
        r['dusuk'], "Cevresel konumdaki az paylasimcilarin etkisi sinirlidir."
    )
    
    # Kural 7
    kural_ekle(
        [('merkezlilik', 'yuksek'), ('duygu', 'degisken')],
        r['yuksek'], "Merkezdeki duygusal kullanicilar genis capta provokatif etki yaratir."
    )
    
    # Kural 8
    kural_ekle(
        [('merkezlilik', 'yuksek'), ('guven', 'dusuk')],
        r['yuksek'], "Etkili ama guvenilmez kullanicilar ciddi tehdit olusturur."
    )
    
    # Kural 9
    kural_ekle(
        [('guven', 'dusuk'), ('paylasim', 'yuksek'), ('duygu', 'degisken')],
        r['yuksek'], "En tehlikeli profil: guvenilmez, aktif ve duygusal."
    )
    
    # Kural 10
    kural_ekle(
        [('guven', 'yuksek'), ('paylasim', 'dusuk'), ('duygu', 'kararli')],
        r['dusuk'], "En guvenli profil: guvenilir, temkinli ve tutarli."
    )
    
    # Kural 11
    kural_ekle(
        [('guven', 'orta'), ('paylasim', 'orta'), ('duygu', 'orta')],
        r['orta'], "Ortalama profil orta duzeyde risk tasir."
    )
    
    # Kural 12
    kural_ekle(
        [('guven', 'dusuk'), ('merkezlilik', 'yuksek'), ('paylasim', 'yuksek')],
        r['yuksek'], "Super yayici profil: guvenilmez, merkezi ve cok aktif."
    )
    
    # Kural 13
    kural_ekle(
        [('guven', 'yuksek'), ('merkezlilik', 'yuksek'), ('duygu', 'kararli')],
        r['dusuk'], "Guvenilir etki merkezi pozitif bilgi hatti ustlenir."
    )
    
    # Kural 14
    kural_ekle(
        [('guven', 'orta'), ('paylasim', 'yuksek')],
        r['orta'], "Orta guven ile yuksek aktivite belirsiz/orta risk olusturur."
    )
    
    # Kural 15
    kural_ekle(
        [('guven', 'dusuk'), ('paylasim', 'orta')],
        r['orta'], "Dusuk guven ama kismen pasif olma durumu riskin derecesini dusurur."
    )
    
    # Kural 16
    kural_ekle(
        [('guven', 'orta'), ('duygu', 'degisken')],
        r['orta'], "Orta guven ile psikolojik degiskenlik birlesimi suphelidir."
    )
    
    # Kural 17
    kural_ekle(
        [('guven', 'yuksek'), ('paylasim', 'yuksek')],
        r['orta'], "Guvenilir ama cok asiri aktif kullanicilar kismi izleme gerektirir."
    )
    
    # Kural 18
    kural_ekle(
        [('merkezlilik', 'orta'), ('paylasim', 'orta')],
        r['orta'], "Ortalama algoritmik guc standart risk uretir."
    )
    
    # Kural 19
    kural_ekle(
        [('merkezlilik', 'dusuk'), ('guven', 'yuksek')],
        r['dusuk'], "Ag disi konum ve guvenilirlik risksiz sonuc uretir."
    )
    
    # Kural 20
    kural_ekle(
        [('merkezlilik', 'orta'), ('duygu', 'degisken'), ('guven', 'dusuk')],
        r['yuksek'], "Nispeten etkili bir konumda dengesiz bir profil yayilim riski dogurur."
    )
    
    # Kural 21
    kural_ekle(
        [('guven', 'dusuk'), ('paylasim', 'dusuk'), ('merkezlilik', 'dusuk')],
        r['dusuk'], "Guvenilmez olsa da hem pasif hem izole profiller zararsizdir."
    )
    
    # Kural 22
    kural_ekle(
        [('guven', 'orta'), ('paylasim', 'dusuk'), ('duygu', 'kararli')],
        r['dusuk'], "Dengeli orta-olcek profiller tehdit icermez."
    )
    
    # Kural 23
    kural_ekle(
        [('merkezlilik', 'yuksek'), ('paylasim', 'orta'), ('duygu', 'orta')],
        r['orta'], "Agda cok guclu ama standart kullanim yapan biri izlenmelidir."
    )
    
    # Kural 24
    kural_ekle(
        [('guven', 'dusuk'), ('merkezlilik', 'orta'), ('duygu', 'degisken'), ('paylasim', 'yuksek')],
        r['yuksek'], "Dortlu risk faktoru birlesimi kritiklik arz eder."
    )
    
    # Kural 25
    kural_ekle(
        [('guven', 'yuksek'), ('merkezlilik', 'yuksek'), ('paylasim', 'yuksek'), ('duygu', 'kararli')],
        r['orta'], "Guvenli super kullanicilar asiri kullanimda kismi hata yapabilir."
    )
    
    # Kural 26
    kural_ekle(
        [('guven', 'orta'), ('duygu', 'kararli')],
        r['dusuk'], "Guven olcuulebilir bir dengedeyken duygusal karar stabilitedir."
    )
    
    # Kural 27
    kural_ekle(
        [('merkezlilik', 'dusuk'), ('duygu', 'kararli')],
        r['dusuk'], "Yalitilmis kullanici mantikli davrandiginda risksizdir."
    )
    
    # Kural 28
    kural_ekle(
        [('guven', 'orta'), ('merkezlilik', 'dusuk')],
        r['dusuk'], "Orta guven ve dusuk erisim riski absorbe eder."
    )
    
    # Kural 29
    kural_ekle(
        [('guven', 'dusuk'), ('paylasim', 'dusuk')],
        r['dusuk'], "Tehlikeli profil paylasim yapmadigi muddetce etkisizdir."
    )
    
    # Kural 30
    kural_ekle(
        [('merkezlilik', 'orta'), ('duygu', 'orta')],
        r['orta'], "Varsayilan ortalama sosyal ag profili."
    )
    
    # Eger hic kural kalmadiysa (guvenlik icin) bir default kural ekleyelim
    if len(kurallar) == 0:
        # En kotu ihtimalle, ciktinin minimum seviyesi gibi default
        # Kullanici HICBIR degisken secmemisse
        pass # Bu durumu inferende ele alacagiz (kontrol mekanizmasiyla)
    else:
        print(f"[KURALLAR] Dinamik derleme: {len(kurallar)} kural olusturuldu (Ayiklanan ve aktif kalan)")
        
    return kurallar, kural_aciklamalari


def kural_tablosu_olustur(kural_aciklamalari):
    """
    Kurallari tablo formatinda gosterir.
    """
    veriler = []
    
    for i, aciklama in enumerate(kural_aciklamalari, 1):
        try:
            kural_metni, gerekce = aciklama.split(': ', 1)
        except ValueError:
            kural_metni = aciklama
            gerekce = ""
            
        if ' -> ' in kural_metni:
            oncul, sonuc = kural_metni.rsplit(' -> ', 1)
        else:
            oncul = kural_metni
            sonuc = ''
        
        veriler.append({
            'Kural No': f'K{i}',
            'Oncul (EGER)': oncul.replace(' VE ', '\nVE '),
            'Sonuc (O HALDE)': sonuc,
            'Gerekce': gerekce
        })
    
    df = pd.DataFrame(veriler)
    return df

