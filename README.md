# Sosyal Ağlarda Yanlış Bilgi Riskinin Bulanık Mantık ile Modellenmesi

## 🧠 Proje Açıklaması

Bu proje, sosyal ağ kullanıcılarının yanlış bilgi yayma riskini tahmin etmek amacıyla
**Mamdani tipi Bulanık Çıkarım Sistemi (Fuzzy Inference System - FIS)** geliştirir.

Sistem, belirsizlik içeren sosyal davranışları modelleyerek klasik deterministik yaklaşımlara
alternatif sunar. Facebook sosyal ağ verisi ile entegre çalışır.

## 🎯 Giriş/Çıkış Değişkenleri

| Değişken | Aralık | Açıklama |
|----------|--------|----------|
| Güven Skoru (Trust) | [0, 1] | Kullanıcı güvenilirliği |
| Paylaşım Sıklığı (Frequency) | [0, 50] | Günlük gönderi sayısı |
| Duygu Sapması (Sentiment) | [-1, +1] | Duygusal tutarsızlık |
| Merkezlilik Skoru (Centrality) | [0, 1] | Ağ konumu |
| **Risk Seviyesi** (Çıktı) | **[0, 1]** | **Yanlış bilgi yayma riski** |

## 📦 Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt
```

## 🚀 Çalıştırma

### Tam Pipeline
```bash
python main.py
```

### Sadece Simülasyon
```bash
python main.py --sadece-sim
```

### Sadece Grafikler
```bash
python main.py --sadece-grs
```

### GUI (Streamlit)
```bash
streamlit run gui/app.py
```

### Komut Satırı Seçenekleri
```bash
python main.py --ornek-sayisi 2000      # 2000 örnek
python main.py --fonksiyon-tipi yamuksal # Yamuksal üyelik fonksiyonları
python main.py --graf-yok                # Facebook graf entegrasyonsuz
```

## 📁 Proje Yapısı

```
BulanıkM/
├── data/
│   ├── raw/                          # Ham veriler
│   └── processed/                    # İşlenmiş veriler
│       ├── sentetik_veri.csv
│       ├── simulasyon_sonuclari.csv
│       └── karsilastirma_sonuclari.csv
│
├── models/
│   └── baseline.py                   # Ağırlıklı doğrusal model
│
├── fuzzy_system/
│   ├── membership.py                 # Üyelik fonksiyonları
│   ├── rules.py                      # 25 bulanık kural
│   └── inference.py                  # Mamdani çıkarım motoru
│
├── experiments/
│   ├── simulation.py                 # Simülasyon motoru
│   ├── sensitivity.py                # Duyarlılık analizi
│   └── comparison.py                 # Model karşılaştırma
│
├── gui/
│   └── app.py                        # Streamlit GUI
│
├── utils/
│   ├── data_loader.py                # Veri yükleme
│   └── preprocessing.py              # Ön işleme
│
├── visualization/
│   ├── plots.py                      # Grafik modülü
│   └── output/                       # Üretilen grafikler
│
├── report/
│   └── paper.md                      # Akademik rapor
│
├── twitter_combined.txt.gz          # Twitter sosyal ağ verisi
├── main.py                           # Ana giriş noktası
├── requirements.txt                  # Bağımlılıklar
└── README.md                         # Bu dosya
```

## ⚙️ Sistem Mimarisi

### Bulanık Çıkarım Süreci (Mamdani)
1. **Bulanıklaştırma**: Kesin girişleri üyelik derecelerine dönüştürür
2. **Kural Değerlendirme**: VE→min, VEYA→max operatörleriyle kuralları değerlendirir
3. **Toplama**: Tüm kural çıktılarını max ile birleştirir
4. **Durulaştırma**: Centroid yöntemiyle kesin çıktı üretir

### Üyelik Fonksiyonları
- **Üçgensel (trimf)**: Keskin geçişler için
- **Yamuksal (trapmf)**: Uç değerlerde düz bölgeler için
- **Karışık**: Uçlarda yamuksal, ortada üçgensel (varsayılan)

### Kural Tabanı
25 adet uzman bilgisine dayalı bulanık kural. Tüm değişken kombinasyonlarını kapsar.

## 📊 Çıktılar

- **9+ grafik**: Üyelik fonksiyonları, 3D yüzey, ısı haritası, risk dağılımı, duyarlılık, karşılaştırma
- **CSV sonuçlar**: Simülasyon ve karşılaştırma sonuçları
- **Interaktif GUI**: Streamlit tabanlı web arayüzü

## 🔧 Teknolojiler

- Python 3.10+
- scikit-fuzzy (Mamdani FIS)
- NetworkX (Graf analizi)
- NumPy, Pandas (Veri işleme)
- Matplotlib, Seaborn (Görselleştirme)
- Streamlit (GUI)
- SciPy (İstatistiksel analiz)

## 📄 Veri Kaynakları

- **Twitter Combined**: Stanford SNAP, 81312 düğüm, 1.327.141 kenar
- **Sentetik Veri**: 1000+ örnek (Uniform, Poisson, Normal, Beta dağılımları)
