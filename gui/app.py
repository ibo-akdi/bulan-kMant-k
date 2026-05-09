# -*- coding: utf-8 -*-
"""
Streamlit GUI Uygulaması
=========================
Sosyal Ağlarda Yanlış Bilgi Riskinin Bulanık Mantık ile Modellenmesi
için interaktif web arayüzü.

Çalıştırma: streamlit run gui/app.py
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Proje kök dizinini Python path'e ekle
PROJE_DIZINI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJE_DIZINI)

import streamlit as st
import skfuzzy as fuzz

from fuzzy_system.inference import BulanikCikarimSistemi
from fuzzy_system.rules import kural_tablosu_olustur
from models.baseline import TemelModel


# ═══════════════════════════════════════════════════════════
# SAYFA YAPILANDIRMASI
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Bulanık Mantık - Yanlış Bilgi Risk Analizi",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS stilleri
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .risk-card {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .risk-low {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
    }
    .risk-medium {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: white;
    }
    .risk-high {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
    }
    .metric-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# DURUM YÖNETİMİ
# ═══════════════════════════════════════════════════════════

@st.cache_resource
def sistemi_yukle():
    """Bulanık çıkarım sistemini yükler ve önbelleğe alır."""
    fis = BulanikCikarimSistemi('karisik')
    temel = TemelModel()
    return fis, temel


# Sistemi yükle
fis, temel_model = sistemi_yukle()


# ═══════════════════════════════════════════════════════════
# BAŞLIK
# ═══════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
    <h1>🧠 Bulanık Mantık ile Yanlış Bilgi Risk Analizi</h1>
    <p>Sosyal Ağlarda Yanlış Bilgi Yayma Riskinin Mamdani Tipi FIS ile Modellenmesi</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# KENAR ÇUBUĞU - GİRİŞ PANELİ
# ═══════════════════════════════════════════════════════════

st.sidebar.header("📥 Giriş Parametreleri")

st.sidebar.markdown("**✅ Kullanılacak Girdiler (Kısmi Analiz)**")
use_guven = st.sidebar.checkbox("Güven Skoru", value=True)
use_paylasim = st.sidebar.checkbox("Paylaşım Sıklığı", value=True)
use_duygu = st.sidebar.checkbox("Duygu Sapması", value=True)
use_merkezlilik = st.sidebar.checkbox("Merkezlilik Skoru", value=True)

aktifler = []
if use_guven: aktifler.append('guven')
if use_paylasim: aktifler.append('paylasim')
if use_duygu: aktifler.append('duygu')
if use_merkezlilik: aktifler.append('merkezlilik')

# Sistemi secilen girdilere gore guncelle
fis.aktif_girdileri_ayarla(aktifler)

st.sidebar.markdown("---")

sozel_giris_modu = st.sidebar.checkbox("🔠 Sözel (Sıfat) Giriş Modu", value=False, help="Sayısal kaydırıcılar yerine bulanık terimleri seçerek (Düşük, Orta vb.) giriş yapmanızı sağlar.")

if sozel_giris_modu:
    st.sidebar.info("Aşağıdaki terimler arka planda ilgili bulanık kümenin zirve değerine dönüştürülerek hesaplanır.")
    
    map_guven = {"Düşük": 0.15, "Orta": 0.50, "Yüksek": 0.85}
    sec_guven = st.sidebar.selectbox("🛡️ Güven Skoru", list(map_guven.keys()), index=1, disabled=not use_guven)
    guven = map_guven[sec_guven]
    
    map_paylasim = {"Düşük": 5.0, "Orta": 20.0, "Yüksek": 40.0}
    sec_paylasim = st.sidebar.selectbox("📝 Paylaşım Sıklığı", list(map_paylasim.keys()), index=1, disabled=not use_paylasim)
    paylasim = map_paylasim[sec_paylasim]
    
    map_duygu = {"Değişken (Negatif)": -0.85, "Orta (Negatif)": -0.45, "Kararlı": 0.0, "Orta (Pozitif)": 0.45, "Değişken (Pozitif)": 0.85}
    sec_duygu = st.sidebar.selectbox("💭 Duygu Sapması", list(map_duygu.keys()), index=2, disabled=not use_duygu)
    duygu = map_duygu[sec_duygu]
    
    map_merkezlilik = {"Düşük": 0.15, "Orta": 0.50, "Yüksek": 0.85}
    sec_merkezlilik = st.sidebar.selectbox("🌐 Merkezlilik Skoru", list(map_merkezlilik.keys()), index=1, disabled=not use_merkezlilik)
    merkezlilik = map_merkezlilik[sec_merkezlilik]

else:
    # Rastgele veri üretme butonu
    if st.sidebar.button("🎲 Rastgele Veri Üret", use_container_width=True):
        st.session_state['guven'] = float(np.random.uniform(0, 1))
        st.session_state['paylasim'] = float(np.random.randint(0, 50))
        st.session_state['duygu'] = float(np.random.uniform(-1, 1))
        st.session_state['merkezlilik'] = float(np.random.uniform(0, 1))

    # Slider'lar
    guven = st.sidebar.slider(
        "🛡️ Güven Skoru",
        min_value=0.0, max_value=1.0,
        value=st.session_state.get('guven', 0.5),
        step=0.01,
        help="Kullanıcının güvenilirlik skoru. 0=Güvenilmez, 1=Tamamen Güvenilir",
        disabled=not use_guven
    )

    paylasim = st.sidebar.slider(
        "📝 Paylaşım Sıklığı (gönderi/gün)",
        min_value=0.0, max_value=50.0,
        value=st.session_state.get('paylasim', 15.0),
        step=1.0,
        help="Günlük ortalama paylaşım sayısı",
        disabled=not use_paylasim
    )

    duygu = st.sidebar.slider(
        "💭 Duygu Sapması",
        min_value=-1.0, max_value=1.0,
        value=st.session_state.get('duygu', 0.2),
        step=0.01,
        help="Duygusal sapma. 0=Kararlı, ±1=Çok Değişken",
        disabled=not use_duygu
    )

    merkezlilik = st.sidebar.slider(
        "🌐 Merkezlilik Skoru",
        min_value=0.0, max_value=1.0,
        value=st.session_state.get('merkezlilik', 0.5),
        step=0.01,
        help="Sosyal ağdaki merkezlilik konumu. 0=Çevresel, 1=Merkezi",
        disabled=not use_merkezlilik
    )

st.sidebar.markdown("---")
st.sidebar.markdown("**⚙️ Sistem Ayarları**")
aciklanabilir_mod = st.sidebar.checkbox("🔍 Açıklanabilir AI Modu", value=True)


# ═══════════════════════════════════════════════════════════
# ANA İÇERİK
# ═══════════════════════════════════════════════════════════

# Risk hesapla
risk = fis.hesapla(guven, paylasim, duygu, merkezlilik)
temel_risk = temel_model.tahmin(guven, paylasim, duygu, merkezlilik)

# Risk kategorisi
if risk < 0.35:
    kategori = "DÜŞÜK"
    renk_sinif = "risk-low"
    emoji = "🟢"
elif risk < 0.65:
    kategori = "ORTA"
    renk_sinif = "risk-medium"
    emoji = "🟡"
else:
    kategori = "YÜKSEK"
    renk_sinif = "risk-high"
    emoji = "🔴"


# ══════════════════════════════════════
# SEKMELER
# ══════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sonuç Paneli",
    "🔍 Kural İnceleme",
    "📈 Görselleştirme",
    "⚡ Duyarlılık",
    "📁 Toplu Analiz"
])


# ═══════════════════════════════════════════════════════════
# SEKME 1: SONUÇ PANELİ
# ═══════════════════════════════════════════════════════════

with tab1:
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="risk-card {renk_sinif}">
            <h2>{emoji} Risk Seviyesi: {risk:.4f}</h2>
            <h3>Kategori: {kategori}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("🧠 Bulanık Model", f"{risk:.4f}")
        st.metric("📐 Temel Model", f"{temel_risk:.4f}")
    
    with col3:
        fark = risk - temel_risk
        st.metric("Fark", f"{fark:+.4f}")
        st.metric("Model Farkı", f"{abs(fark)*100:.1f}%")
    
    st.markdown("---")
    
    # Giriş özeti
    st.subheader("📥 Giriş Değerleri Özeti")
    giris_col1, giris_col2, giris_col3, giris_col4 = st.columns(4)
    
    with giris_col1:
        st.metric("🛡️ Güven", f"{guven:.2f}")
    with giris_col2:
        st.metric("📝 Paylaşım", f"{paylasim:.0f}/gün")
    with giris_col3:
        st.metric("💭 Duygu", f"{duygu:+.2f}")
    with giris_col4:
        st.metric("🌐 Merkezlilik", f"{merkezlilik:.2f}")
    
    # Açıklanabilir AI Modu
    if aciklanabilir_mod:
        st.markdown("---")
        st.subheader("🔍 Açıklanabilir AI - Adım Adım Çıkarım")
        
        sonuclar = fis.ara_sonuclari_al(guven, paylasim, duygu, merkezlilik)
        
        # Bulanıklaştırma adımı
        st.markdown("**📌 Adım 1: Bulanıklaştırma (Fuzzification)**")
        
        turkce_degiskenler = {
            'guven': 'Güven Skoru',
            'paylasim': 'Paylaşım Sıklığı',
            'duygu': 'Duygu Sapması',
            'merkezlilik': 'Merkezlilik Skoru'
        }
        turkce_terimler = {
            'dusuk': 'Düşük', 'orta': 'Orta', 'yuksek': 'Yüksek',
            'kararli': 'Kararlı', 'degisken': 'Değişken'
        }
        
        uyelik_verileri = []
        for deg_adi, terimler in sonuclar['uyelik_dereceleri'].items():
            for terim, derece in terimler.items():
                uyelik_verileri.append({
                    'Değişken': turkce_degiskenler.get(deg_adi, deg_adi),
                    'Terim': turkce_terimler.get(terim, terim),
                    'Üyelik Derecesi': f"{derece:.4f}",
                    'Görsel': '█' * int(derece * 20) + '░' * (20 - int(derece * 20))
                })
        
        st.dataframe(
            pd.DataFrame(uyelik_verileri),
            use_container_width=True,
            hide_index=True
        )
        
        # Çıkarım adımları
        st.markdown("""
        **⚙️ Adım 2-3: Kural Değerlendirme ve Toplama**
        - VE (AND) operatörü: **min** (minimum)
        - VEYA (OR) operatörü: **max** (maksimum)
        - Toplama yöntemi: **max** (maksimum)
        
        **📌 Adım 4: Durulaştırma (Defuzzification)**
        - Yöntem: **Ağırlık Merkezi (Centroid)**
        - Formül: z* = ∫ z · μ_agg(z) dz / ∫ μ_agg(z) dz
        """)


# ═══════════════════════════════════════════════════════════
# SEKME 2: KURAL İNCELEME
# ═══════════════════════════════════════════════════════════

with tab2:
    st.subheader("📜 Bulanık Kural Tabanı")
    
    # Kural tablosu
    tablo = kural_tablosu_olustur(fis.kural_aciklamalari)
    st.dataframe(tablo, use_container_width=True, hide_index=True)
    
    st.markdown(f"**Toplam: {len(fis.kurallar)} kural**")
    
    # Kural aktivasyonları
    st.markdown("---")
    st.subheader("🎯 Mevcut Girişler İçin Üyelik Dereceleri")
    
    uyelikler = fis.kural_ateslemelerini_al(guven, paylasim, duygu, merkezlilik)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    turkce_degiskenler_degerler = {
        'guven': ('Güven Skoru', guven),
        'paylasim': ('Paylaşım Sıklığı', paylasim),
        'duygu': ('Duygu Sapması', duygu),
        'merkezlilik': ('Merkezlilik Skoru', merkezlilik)
    }
    
    renkler = {'dusuk': '#2ecc71', 'orta': '#f39c12', 'yuksek': '#e74c3c',
               'kararli': '#2ecc71', 'degisken': '#e74c3c'}
    
    for idx, (deg_adi, terimler) in enumerate(uyelikler.items()):
        satir, sutun = divmod(idx, 2)
        ax = axes[satir, sutun]
        isim, deger = turkce_degiskenler_degerler[deg_adi]
        
        terim_isimleri = [turkce_terimler.get(t, t) for t in terimler.keys()]
        degerler = list(terimler.values())
        bar_renkleri = [renkler.get(t, '#3498db') for t in terimler.keys()]
        
        bars = ax.bar(terim_isimleri, degerler, color=bar_renkleri, edgecolor='white')
        for bar, d in zip(bars, degerler):
            if d > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       f'{d:.3f}', ha='center', fontsize=10, fontweight='bold')
        
        ax.set_title(f'{isim} = {deger:.2f}', fontweight='bold')
        ax.set_ylabel('μ(x)')
        ax.set_ylim(0, 1.15)
        ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


# ═══════════════════════════════════════════════════════════
# SEKME 3: GÖRSELLEŞTİRME
# ═══════════════════════════════════════════════════════════

with tab3:
    gorsel_secim = st.selectbox(
        "Görselleştirme Seçin:",
        ["Üyelik Fonksiyonları", "3D Yüzey Grafiği", "Isı Haritası"]
    )
    
    if gorsel_secim == "Üyelik Fonksiyonları":
        st.subheader("📐 Üyelik Fonksiyonları")
        
        fig, axes = plt.subplots(3, 2, figsize=(14, 12))
        renkler_uyelik = {'dusuk': '#2ecc71', 'orta': '#f39c12', 'yuksek': '#e74c3c',
                          'kararli': '#2ecc71', 'degisken': '#e74c3c'}
        
        turkce_degisken_bilgileri = {
            'guven': ('Güven Skoru', '[0, 1]'),
            'paylasim': ('Paylaşım Sıklığı', '[0, 50]'),
            'duygu': ('Duygu Sapması', '[-1, +1]'),
            'merkezlilik': ('Merkezlilik Skoru', '[0, 1]'),
            'risk': ('Risk Seviyesi', '[0, 1]')
        }
        
        for idx, (anahtar, degisken) in enumerate(fis.degiskenler.items()):
            satir, sutun = divmod(idx, 2)
            ax = axes[satir, sutun]
            isim, birim = turkce_degisken_bilgileri.get(anahtar, (anahtar, ''))
            
            for terim in degisken.terms:
                renk = renkler_uyelik.get(terim, '#3498db')
                terim_tr = turkce_terimler.get(terim, terim.capitalize())
                ax.plot(degisken.universe, degisken[terim].mf,
                       linewidth=2.5, label=terim_tr, color=renk)
                ax.fill_between(degisken.universe, degisken[terim].mf,
                               alpha=0.15, color=renk)
            
            ax.set_title(f'{isim} {birim}', fontweight='bold')
            ax.set_ylabel('μ(x)')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(-0.05, 1.15)
        
        axes[2, 1].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.markdown("---")
        st.subheader("🧮 Matematiksel Gösterimler (Formüller)")
        st.markdown("Yukarıda gördüğünüz üyelik fonksiyonlarının resmi matematiksel, parçalı `(piecewise)` denklem şemaları aşağıda verilmiştir:")
        
        try:
            from visualization.formulas import get_trimf_latex, get_trapmf_latex
            
            with st.expander("🛡️ Güven Skoru Fonksiyonları | Sembol: G(x)", expanded=False):
                st.latex(get_trapmf_latex('G_{Düşük}', 0, 0, 0.15, 0.4))
                st.latex(get_trimf_latex('G_{Orta}', 0.2, 0.5, 0.8))
                st.latex(get_trapmf_latex('G_{Yüksek}', 0.6, 0.85, 1, 1))

            with st.expander("📝 Paylaşım Sıklığı Fonksiyonları | Sembol: P(x)", expanded=False):
                st.latex(get_trapmf_latex('P_{Düşük}', 0, 0, 5, 15))
                st.latex(get_trimf_latex('P_{Orta}', 8, 20, 35))
                st.latex(get_trapmf_latex('P_{Yüksek}', 25, 40, 50, 50))
                
            with st.expander("💭 Duygu Sapması Fonksiyonları | Sembol: S(x)", expanded=False):
                st.latex(get_trapmf_latex('S_{Kararlı}', -0.3, -0.1, 0.1, 0.3))
                st.markdown("Duygu sapması pozitif ve negatif simetrik iki ayrı omuzdan oluşur:")
                st.latex(get_trimf_latex('S_{Orta}', 0.15, 0.45, 0.75))
                st.latex(get_trapmf_latex('S_{Değişken}', 0.55, 0.75, 1, 1))
                
            with st.expander("🌐 Merkezlilik Skoru Fonksiyonları | Sembol: C(x)", expanded=False):
                st.latex(get_trapmf_latex('C_{Düşük}', 0, 0, 0.15, 0.4))
                st.latex(get_trimf_latex('C_{Orta}', 0.2, 0.5, 0.8))
                st.latex(get_trapmf_latex('C_{Yüksek}', 0.6, 0.85, 1, 1))
                
        except Exception as e:
            st.warning(f"Formüller yüklenemedi: {e}")
    
    elif gorsel_secim == "3D Yüzey Grafiği":
        st.subheader("🏔️ 3D Risk Yüzeyi")
        
        eksen_secenekleri = {
            'Güven Skoru': 'guven_skoru',
            'Paylaşım Sıklığı': 'paylasim_sikligi', 
            'Duygu Sapması': 'duygu_sapmasi',
            'Merkezlilik Skoru': 'merkezlilik_skoru'
        }
        
        col1, col2 = st.columns(2)
        with col1:
            eksen_x = st.selectbox("X Ekseni:", list(eksen_secenekleri.keys()), index=0)
        with col2:
            eksen_y = st.selectbox("Y Ekseni:", list(eksen_secenekleri.keys()), index=3)
        
        cozunurluk = st.slider("Çözünürlük:", 10, 40, 25)
        
        if st.button("3D Grafik Oluştur", type="primary"):
            with st.spinner("3D yüzey hesaplanıyor..."):
                from visualization.plots import yuzey_grafigi_3d
                fig = yuzey_grafigi_3d(
                    fis,
                    eksen_secenekleri[eksen_x],
                    eksen_secenekleri[eksen_y],
                    cozunurluk=cozunurluk
                )
                st.pyplot(fig)
                plt.close()
    
    elif gorsel_secim == "Isı Haritası":
        st.subheader("🌡️ Risk Isı Haritası")
        
        eksen_secenekleri = {
            'Güven Skoru': 'guven_skoru',
            'Paylaşım Sıklığı': 'paylasim_sikligi',
            'Duygu Sapması': 'duygu_sapmasi',
            'Merkezlilik Skoru': 'merkezlilik_skoru'
        }
        
        col1, col2 = st.columns(2)
        with col1:
            hm_x = st.selectbox("X Ekseni:", list(eksen_secenekleri.keys()), index=0, key='hm_x')
        with col2:
            hm_y = st.selectbox("Y Ekseni:", list(eksen_secenekleri.keys()), index=3, key='hm_y')
        
        if st.button("Isı Haritası Oluştur", type="primary"):
            with st.spinner("Isı haritası hesaplanıyor..."):
                from visualization.plots import isi_haritasi
                fig = isi_haritasi(
                    fis,
                    eksen_secenekleri[hm_x],
                    eksen_secenekleri[hm_y],
                    cozunurluk=35
                )
                st.pyplot(fig)
                plt.close()


# ═══════════════════════════════════════════════════════════
# SEKME 4: DUYARLILIK ANALİZİ
# ═══════════════════════════════════════════════════════════

with tab4:
    st.subheader("⚡ Duyarlılık Analizi")
    
    if st.button("Duyarlılık Grafiklerini Oluştur", type="primary"):
        with st.spinner("Duyarlılık analizi yapılıyor..."):
            from visualization.plots import duyarlilik_grafikleri
            fig = duyarlilik_grafikleri(fis)
            st.pyplot(fig)
            plt.close()
    
    st.markdown("---")
    st.subheader("🔬 Detaylı Tek Değişken Analizi")
    
    secilen_degisken = st.selectbox(
        "Analiz edilecek değişken:",
        ['Güven Skoru', 'Paylaşım Sıklığı', 'Duygu Sapması', 'Merkezlilik Skoru']
    )
    
    degisken_esle = {
        'Güven Skoru': ('guven', 0, 1),
        'Paylaşım Sıklığı': ('paylasim', 0, 50),
        'Duygu Sapması': ('duygu', -1, 1),
        'Merkezlilik Skoru': ('merkezlilik', 0, 1)
    }
    
    deg_adi, deg_min, deg_max = degisken_esle[secilen_degisken]
    
    n_nokta = 100
    x_values = np.linspace(deg_min, deg_max, n_nokta)
    risk_values = []
    
    sabit = {'guven': guven, 'paylasim': paylasim, 'duygu': duygu, 'merkezlilik': merkezlilik}
    
    for x in x_values:
        degerler = sabit.copy()
        degerler[deg_adi] = x
        r = fis.hesapla(degerler['guven'], degerler['paylasim'],
                       degerler['duygu'], degerler['merkezlilik'])
        risk_values.append(r)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_values, risk_values, 'b-', linewidth=2.5, color='#2980b9')
    ax.fill_between(x_values, risk_values, alpha=0.15, color='#2980b9')
    ax.axhline(y=0.35, color='green', linestyle='--', alpha=0.5, label='Düşük/Orta sınır')
    ax.axhline(y=0.65, color='red', linestyle='--', alpha=0.5, label='Orta/Yüksek sınır')
    
    # Mevcut değer işareti
    mevcut_deger = sabit[deg_adi]
    mevcut_risk = fis.hesapla(sabit['guven'], sabit['paylasim'], sabit['duygu'], sabit['merkezlilik'])
    ax.plot(mevcut_deger, mevcut_risk, 'ro', markersize=12, label=f'Mevcut: {mevcut_deger:.2f}')
    
    ax.set_xlabel(secilen_degisken, fontsize=12)
    ax.set_ylabel('Risk Seviyesi', fontsize=12)
    ax.set_title(f'{secilen_degisken} Duyarlılık Analizi', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


# ═══════════════════════════════════════════════════════════
# SEKME 5: TOPLU ANALİZ
# ═══════════════════════════════════════════════════════════

with tab5:
    st.subheader("📁 CSV Dosyası ile Toplu Analiz")
    
    yuklenen_dosya = st.file_uploader(
        "CSV dosyası yükleyin (sütunlar: guven_skoru, paylasim_sikligi, duygu_sapmasi, merkezlilik_skoru)",
        type=['csv']
    )
    
    if yuklenen_dosya is not None:
        df = pd.read_csv(yuklenen_dosya)
        st.write(f"Yüklenen veri: {len(df)} satır")
        st.dataframe(df.head(10))
        
        gerekli_sutunlar = ['guven_skoru', 'paylasim_sikligi', 'duygu_sapmasi', 'merkezlilik_skoru']
        if all(s in df.columns for s in gerekli_sutunlar):
            if st.button("Toplu Risk Hesapla", type="primary"):
                with st.spinner("Risk hesaplanıyor..."):
                    riskler = fis.toplu_hesapla(df)
                    df['risk_seviyesi'] = np.round(riskler, 4)
                    df['risk_kategorisi'] = pd.cut(
                        df['risk_seviyesi'],
                        bins=[0, 0.35, 0.65, 1.0],
                        labels=['Düşük', 'Orta', 'Yüksek'],
                        include_lowest=True
                    )
                    
                    st.success(f"✅ {len(df)} örnek için risk hesaplandı!")
                    st.dataframe(df)
                    
                    # Risk dağılımı
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.hist(riskler, bins=30, density=True, alpha=0.6, color='#3498db',
                           edgecolor='white')
                    ax.set_xlabel('Risk Seviyesi')
                    ax.set_ylabel('Yoğunluk')
                    ax.set_title('Toplu Analiz - Risk Dağılımı')
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                    
                    # İndirme butonu
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Sonuçları İndir (CSV)",
                        csv,
                        "risk_sonuclari.csv",
                        "text/csv"
                    )
        else:
            st.error(f"❌ Gerekli sütunlar bulunamadı: {gerekli_sutunlar}")
    
    st.markdown("---")
    st.subheader("🎲 Rastgele Toplu Veri Üretimi")
    
    n_rastgele = st.number_input("Örnek sayısı:", min_value=10, max_value=5000, value=100, step=10)
    
    if st.button("Rastgele Veri Üret ve Analiz Et"):
        with st.spinner(f"{n_rastgele} örnek üretiliyor..."):
            np.random.seed(None)
            df_rastgele = pd.DataFrame({
                'guven_skoru': np.round(np.random.uniform(0, 1, n_rastgele), 4),
                'paylasim_sikligi': np.random.poisson(8, n_rastgele).clip(0, 50).astype(float),
                'duygu_sapmasi': np.round(np.random.normal(0, 0.35, n_rastgele).clip(-1, 1), 4),
                'merkezlilik_skoru': np.round(np.random.beta(2, 5, n_rastgele), 4)
            })
            
            riskler = fis.toplu_hesapla(df_rastgele)
            df_rastgele['risk_seviyesi'] = np.round(riskler, 4)
            df_rastgele['risk_kategorisi'] = pd.cut(
                df_rastgele['risk_seviyesi'],
                bins=[0, 0.35, 0.65, 1.0],
                labels=['Düşük', 'Orta', 'Yüksek'],
                include_lowest=True
            )
            
            st.success(f"✅ {n_rastgele} örnek üretildi ve analiz edildi!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ortalama Risk", f"{riskler.mean():.4f}")
            with col2:
                st.metric("Min Risk", f"{riskler.min():.4f}")
            with col3:
                st.metric("Max Risk", f"{riskler.max():.4f}")
            
            st.dataframe(df_rastgele.head(20))
            
            # Dağılım grafiği
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(riskler, bins=30, density=True, alpha=0.6, color='#9b59b6',
                   edgecolor='white')
            ax.axvspan(0, 0.35, alpha=0.1, color='green')
            ax.axvspan(0.35, 0.65, alpha=0.1, color='orange')
            ax.axvspan(0.65, 1, alpha=0.1, color='red')
            ax.set_xlabel('Risk Seviyesi')
            ax.set_ylabel('Yoğunluk')
            ax.set_title('Rastgele Veri - Risk Dağılımı')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()


# ═══════════════════════════════════════════════════════════
# ALT BİLGİ
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>🧠 Sosyal Ağlarda Yanlış Bilgi Riskinin Bulanık Mantık ile Modellenmesi</p>
    <p>Mamdani Tipi Bulanık Çıkarım Sistemi | Python + scikit-fuzzy + Streamlit</p>
</div>
""", unsafe_allow_html=True)
