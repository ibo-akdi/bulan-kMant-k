# SOSYAL AĞLARDA YANLIŞ BİLGİ RİSKİNİN BULANIK MANTIK İLE MODELLENMESİ 
## Uçtan Uca Proje Dokümantasyonu ve Bütünleşik Analiz Raporu

Bu doküman, projeye başlandığı ilk andan itibaren gerçekleştirilen **tüm mimari kararları, yazılım geliştirmeleri, kural oluşturma aşamalarını, matematiksel hesaplamaları ve hata giderim süreçlerini** "noktası virgülüne kadar" barındıran eksiksiz, tek parça sistem kılavuzudur.

---

### 1. PROJENİN AMACI VE YAPISI
Sosyal ağlarda dezenformasyon ve yanlış bilgi yayılımı, genellikle klasik "Makine Öğrenmesi (Siyah Kutu)" yöntemleriyle tespit edilmeye çalışılır. Bu projedeki temel amaç, "Açıklanabilir Yapay Zeka (XAI)" adımlarını temel alan, uzman kuralları ile desteklenmiş ve sosyal davranışlardaki "belirsizlikleri (uncertainty)" yönetebilen bir **Mamdani Tipi Bulanık Çıkarım Sistemi (Fuzzy Inference System - FIS)** geliştirmektir.

Sistem, baştan sona modüler bir Python altyapısı olarak (OOP - Nesne Yönelimli Programlama mantığıyla) inşa edilmiştir.

### 2. KULLANILAN VERİ BİLİMİ YAKLAŞIMI VE VERİ SETİ (Ağ Topolojisi)
Proje tamamen kurgusal/sanal veriler yerine **gerçek bağlantı haritaları** üzerinden simüle edilmiştir. 
Kullanılan Veri: Piyasada standart olan **Stanford SNAP Twitter Veri Seti (`twitter_combined.txt.gz`)**.

**NetworkX ile Veri İşleme Aşamaları:**
- Projeye dahil edilen dosya parse edilmiş ve 81312 gerçek kullanıcı (Node) ile 1.327.141 bağlantısı (Edge) graf formunda modellenmiştir.
- Bu graf üzerinden, kullanıcıların ağda ne kadar "Merkezi" olduklarını matematikselleştiren **Merkezlilik Skoru (Centrality Score)** hesaplanmıştır.
- Merkezlilik Skoru; "Derece Merkezliliği (Degree Centrality - çok arkadaşı olma durumu)" ve "Arasındalık Merkezliliği (Betweenness Centrality - bilgi köprüsü olma durumu)" formüllerinin ağırlıklı birleştirilmesi ve ardından `[0, 1]` aralığına normalize edilmesi (Min-Max scaler) ile bulunmuştur.
- Bu gerçek ağ konumu verisi üzerine; **Güven Skoru** (Uniform dağılım), **Paylaşım Sıklığı** (Poisson dağılımı), ve **Duygu Sapması** (Normal dağılım) davranışsal sentetik sentetik verilerle birleştirilerek nihai "Hibrit Analiz Veri Seti" (`data/processed/sentetik_veri.csv`) oluşturulmuştur.

---

### 3. BULANIK ÇIKARIM SİSTEMİ (MAMDANI FIS) MİMARİSİ
Sistem, problemin doğası gereği esneklik sunan "Mamdani" çıkarım yapısına sahiptir. Kütüphane olarak `scikit-fuzzy` kullanılmıştır.

#### 3.1. Giriş Değişkenleri (Antecedents)
Toplam 4 adet boyut (özellik) tanımlanmıştır:
1.  **Güven Skoru (Trust Score):** `[0, 1]` aralığındadır. Değerleme: `Düşük`, `Orta`, `Yüksek`.
2.  **Paylaşım Sıklığı (Posting Frequency):** `[0, 50]` aralığındadır (Günlük gönderi). Değerleme: `Düşük`, `Orta`, `Yüksek`.
3.  **Duygu Sapması (Sentiment Deviation):** `[-1, +1]` aralığındadır (0 Kararlı ruh halini temsil eder). Değerleme: `Kararlı`, `Orta`, `Değişken`.
4.  **Merkezlilik Skoru (Centrality Score):** `[0, 1]` aralığındadır (Twitter verisinden gelir). Değerleme: `Düşük`, `Orta`, `Yüksek`.

*Önemli Tasarım Kararı:* Üyelik fonksiyonlarında (Membership Functions) uç sınırların dışarı taşmasını engellemek için `trapezoidal (trapmf - yamuksal)` fonksiyonlar kullanırken, orta bölgelerdeki dengeli geçişi sağlamak için `triangular (trimf - üçgensel)` fonksiyonlar kullandığımız **KARIŞIK (Hybrid)** bir bulanık uzay kurgulanmıştır.

#### 3.2. Çıkış Değişkeni (Consequent)
1.  **Yanlış Bilgi Yayma Riski:** `[0, 1]` aralığındadır.
    -   Risk < 0.35 : **Düşük Risk**
    -   0.35 ≤ Risk < 0.65: **Orta Risk**
    -   Risk ≥ 0.65: **Yüksek Risk**

---

### 4. DİNAMİK YAPI VE 30 UZMAN KURALI (RULE BASE)
Sistemde uzman görüşü temsiliyle toplam **30 Kural** yaratılmıştır. Ancak projedeki en büyük teknik inovasyonlardan biri **Dinamik Kural Motoru (Kısmi Senaryo Analizi)** özelliğidir.

**Dinamik Kural Motoru (Dynamic Rule Compiler):**
Scikit-fuzzy'de normalde bir sistem başlatıldığında 4 girdinin tamamına değer girmezseniz sistem çökmesine veya hatalı çalışmasına (ValueError) neden olur. Sistemimize, kullanıcının seçmediği bir girdiyi hesaba katmaması için (örn: "Duygu sapması umurumda değil, sadece Güvene göre hesapla"); o girdiyi içeren kuralı tamamen kırparak "on-the-fly" (anında) kuralları yeniden baştan derleyen eşsiz bir fonksiyon entegre edilmiştir. Sadece aktif girdiler ile kalan rule öncülleri yeniden `&` (VE) operatörüyle derlenir.

**30 Kuralın Listesi ve Gerekçeleri:**
1.  *Düşük güven + Yüksek paylaşım → Yüksek risk:* Güvenilirliği düşük kişilerin yoğun paylaşımı tehlikelidir.
2.  *Yüksek güven + Kararlı duygu → Düşük risk:* Güvenilir ve tutarlı kullanıcılar doğru bilgi paylaşır.
3.  *Düşük güven + Değişken duygu → Yüksek risk:* Düşük güven ve yüksek duygusal sapma dezenformasyon işaretidir.
4.  *Yüksek güven + Düşük paylaşım → Düşük risk:* Güvenilir ve seçici paylaşımcılar güvenli kabul edilir.
5.  *Yüksek merkezlilik + Yüksek paylaşım → Yüksek risk:* Merkezi konumdaki yoğun paylaşımcılar bilgiyi çok hızlı yayar.
6.  *Düşük merkezlilik + Düşük paylaşım → Düşük risk:* Çevresel konumdaki az paylaşımcıların etkisi sınırlıdır.
7.  *Yüksek merkezlilik + Değişken duygu → Yüksek risk:* Merkezdeki duygusal kullanıcılar geniş çapta provokatif etki yaratır.
8.  *Yüksek merkezlilik + Düşük güven → Yüksek risk:* Etkili ama güvenilmez kullanıcılar ciddi tehdit oluşturur.
9.  *Düşük güven + Yüksek paylaşım + Değişken duygu → Yüksek risk:* En tehlikeli profil (Troll); güvenilmez, aktif, duygusal.
10. *Yüksek güven + Düşük paylaşım + Kararlı duygu → Düşük risk:* En güvenli profil; güvenilir, temkinli, tutarlı.
11. *Orta güven + Orta paylaşım + Orta duygu → Orta risk:* Ortalama profil zımni risk taşır.
12. *Düşük güven + Yüksek merkezlilik + Yüksek paylaşım → Yüksek risk:* Süper yayıcı profildir.
13. *Yüksek güven + Yüksek merkezlilik + Kararlı duygu → Düşük risk:* Güvenilir etki merkezi pozitif bilgi hattı oluşturur.
14. *Orta güven + Yüksek paylaşım → Orta risk:* Orta güvenle aktivite artarsa potansiyel risk teşkil eder.
15. *Düşük güven + Orta paylaşım → Orta risk:* Düşük güvene rağmen pasiflik riski bir kademe baskılar.
16. *Orta güven + Değişken duygu → Orta risk:* Psikolojik değişkenlik şüphe uyandırır.
17. *Yüksek güven + Yüksek paylaşım → Orta risk:* Güvenilir bile olsa aşırı gönderi spame kayabilir, izlenmelidir.
18. *Orta merkezlilik + Orta paylaşım → Orta risk:* Standart doneler, standart risk üretir.
19. *Düşük merkezlilik + Yüksek güven → Düşük risk:* Ağdışı konum, yüksek güvenile birleşince tamamen risksizdir.
20. *Orta merkezlilik + Değişken duygu + Düşük güven → Yüksek risk:* Nispeten etkili bir profilin dengesizliği sızıntı yapabilir.
21. *Düşük güven + Düşük paylaşım + Düşük merkezlilik → Düşük risk:* Güvenilmez ama hem izole hem pasif olduğunda tehlikesizdir.
22. *Orta güven + Düşük paylaşım + Kararlı duygu → Düşük risk:* Orta kademe dengeli kullanım riski düşürür.
23. *Yüksek merkezlilik + Orta paylaşım + Orta duygu → Orta risk:* Ağda çok güçlü ama standart kullanım izlenmelidir.
24. *Düşük güven + Orta merkezlilik + Değişken duygu + Yüksek paylaşım → Yüksek risk:* Çoklu risk faktörü kombinasyonu tehlikelidir.
25. *Yüksek güven + Yüksek merkezlilik + Yüksek paylaşım + Kararlı duygu → Orta risk:* Güvenli fenomenler de hata yapabilir.
**(Varsayılan Geniş Kapsamlı Kurallar)**
26. *Orta güven + Kararlı duygu → Düşük risk:* Stabilite riski düşürür.
27. *Düşük merkezlilik + Kararlı duygu → Düşük risk:* Yalıtılmış kullanıcı mantıklıyken risksizdir.
28. *Orta güven + Düşük merkezlilik → Düşük risk:* Sönümlü etki.
29. *Düşük güven + Düşük paylaşım → Düşük risk:* Paylaşım yoksa zarar da yoktur.
30. *Orta merkezlilik + Orta duygu → Orta risk:* Sistemin varsayılan kararıdır.

---

### 5. YAZILIMSAL ZORLUKLAR (DEBUGGING) VE HATA GİDERİMLERİ
Geliştirme sürecinde üstesinden gelinen Majör Engeller:

1. **Scikit-Fuzzy State Reset (Durum Kaybı) Bug'ı:**
   - *Sorun:* Arayüzdeki slider oynatıldığında veya `hesapla()` metodu üst üste ikinci kez çağrıldığında `KeyError: risk_seviyesi` fırlatılıyordu çünkü `scikit-fuzzy` simulasyon objesi dahili bellek akışını (state) temizlemiyordu.
   - *Çözüm:* Her hesaplama çağrısında global değil, metot içi lokal ve "taze" bir `ctrl.ControlSystemSimulation(self.kontrol_sistemi)` baştan üretilerek bu bellek sızıntısı kalıcı olarak engellendi. Olası taşmaları önlemek adına girdilere `0.001 - 0.999` min-max sınırları (clip) uygulandı.

2. **Windows Uyumsuzluğu ve Unicode Hataları (cp1254):**
   - *Sorun:* Deneylerin konsol çıktıları Windows işletim sistemi üzerinde `cp1254` kodlaması sebebiyle (Emoji veya kutu çizim karakterlerinde) `UnicodeEncodeError` vererek sistemi çökertebiliyordu.
   - *Çözüm:* Sınıfların en başına `sys.stdout.reconfigure(encoding='utf-8')` komutu sistem çapında uygulandı ve semboller ASCII uyumlu versiyonlarına düşürülerek stabilite garantilendi. Görüntüler (Matplotlib) için Türkçe karakter sorunu `DejaVu Sans` fontu setlenerek ve `.use("Agg")` (GUI bloklanmaması için) kullanılarak çözüldü.

---

### 6. DENEYLER VE MATEMATİKSEL İSTATİSTİKLER (EXPERIMENTS)

#### Bulanık Mantık ile Doğrusal Metot (Temel Model) Karşılaştırması
Sistemin becerisini değerlendirebilmek için "Temel Ağırlıklı Doğrusal Bir Model" de projeye dahil edildi.
(Model: `Risk = 0.30*(1-Güven) + 0.25*(Paylaşım/50) + 0.20*(|Duygu|) + 0.25*(Merkezlilik)`)

*Çıkan Benchmark Sonuçları (1000 örnek için):*
-   Ortalama Bulanık Risk: 0.1967
-   Bulanık vs Lineer MAE (Ortalama Mutlak Hata) Farkı: 0.081
-   Sınıflandırma Doğruluğu (Accuracy): %85.9 (Düşük/Orta/Yüksek kümeleme)
-   Duyarlılık (Recall): 0.85
-   *Çıkarım:* Deterministik ağırlıklı model dümdüz bir tahminde bulunurken; Bulanık mantık (özellikle Troll diye tabir edilen yüksek aktiviteli ekstrem kullanıcıları) non-lineer (doğrusal olmayan esnek) olarak çok daha nokta atışı tespit edebilmiştir.

#### Duyarlılık Analizleri
-   Güven azaldıkça riskin exponansiyel (ani ivmeyle) arttığı gözlemlendi.
-   Duygu sapması 0 (Kararlı) noktasındayken sistem yatay seyretti, kutuplara doğru Risk parabolik olarak yükseldi.

Tüm bu grafikler, 3D (3 Boyutlu) dağılım yüzeyleri, korelasyon ısı haritaları, Karışıklık Matrisleri (Confusion Matrix) çizilip otomatik olarak Python scripti ile `.png` olarak `visualization/output` klasörü içerisine basılacak altyapı hazırlanmıştır.

---

### 7. UYGULAMA ARAYÜZÜ (STREAMLIT GUI) MİMARİSİ
Son kullanıcı ve akademisyenler için çok katmanlı, 5 sekmeli profesyonel bir Dashboard yazıldı: `gui/app.py`

- **Sol Menü (Sidebar):** Giriş parametreleri için kaydırıcılar, rastgele veri üretim butonu, "Açıklanabilir XAI" modu açma-kapama tuşu.
- **Kısmi Senaryo Modülü (Onay Kutuları):** İstenen boyutların (örn. Duygu) tikini kaldırarak Bulanık Sistem Hesaplamasından çıkartılmasını sağlayan (Rules Compilation in runtime) kilit paneli.
- **Sekme 1: Sonuç Paneli:** Risk Seviyesini, Kategorisini, Model Karşılaştırmasını verir. XAI (Açıklanabilir) mod açıksa arka planda dönen `Adım Adım Üyelik Derecesi Matrislerini` matematiksel oranlarıyla beraber loglar.
- **Sekme 2: Kural İnceleme:** Tanımlanan 30 kuralın okunaklı listesi. O an giren (aktif) değerlerin hangi kuralların alt uçlarını "ateşlediğini (Rule Activation)" bar grafiğiyle canlı gösterir. 
- **Sekme 3: Görselleştirme:** Dinamik olarak X ve Y eksenlerinin seçilip (Örn: Güvene Karşı Merkezlilik Skoru) 3D Surface Plot çıkarılmasını veya Heatmap (Isı Haritası) çizilmesini ve üyelik fonksiyon limitlerinin görülmesini sağlar.
- **Sekme 4: Duyarlılık:** Seçilen tek bir değişkende 100 farklı nokta taranarak, diğer 3 değişken sabit tutulmak kaydıyla "Şu an Güven Skorumu 1 birim artırsam Riskim oransal olarak nereye tırmanırdı?" analizi.
- **Sekme 5: Toplu Analiz & CSV Upload:** Sistemi büyük veri üzerinde sınamak için CSV okuyucu konulmuştur. Kendiniz oluşturduğunuz dosyayı verip binlerce satır verinin toplu risk değerlendirmesini tek tıkla yaptırıp `risk_sonuclar.csv` formatına alabileceğiniz pipeline entegre edilmiştir. Ayrıca "Rastgele Üretim" testleriyle sistem içi histogram analizi dahi simüle edilebilmektedir. 

---
*(Belgenin Sonu)*
