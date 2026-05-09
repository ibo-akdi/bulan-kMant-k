# Sosyal Ağlarda Yanlış Bilgi Riskinin Bulanık Mantık ile Modellenmesi

**Modeling Misinformation Risk in Social Networks Using Fuzzy Logic**

---

## Özet (Abstract)

Sosyal ağlarda yanlış bilgi yayılımı, modern bilgi ekosisteminin en önemli sorunlarından biridir. Bu çalışmada, sosyal ağ kullanıcılarının yanlış bilgi yayma riskini tahmin etmek amacıyla Mamdani tipi bir Bulanık Çıkarım Sistemi (FIS) geliştirilmiştir. Sistem, güven skoru, paylaşım sıklığı, duygu sapması ve merkezlilik skoru olmak üzere dört giriş değişkenini kullanarak yanlış bilgi risk seviyesini [0,1] aralığında hesaplamaktadır. Üçgensel ve yamuksal üyelik fonksiyonları ile 30 adet uzman kuralı tanımlanmış, Facebook sosyal ağ verisi (SNAP Stanford) üzerinde doğrulanmıştır. Sonuçlar, bulanık mantık yaklaşımının belirsiz sosyal davranışları ağırlıklı doğrusal modellere göre daha etkili modellediğini göstermektedir.

**Anahtar Kelimeler:** Bulanık mantık, Mamdani çıkarım sistemi, yanlış bilgi, sosyal ağ analizi, risk değerlendirme

---

## 1. Giriş (Introduction)

Sosyal ağlar, milyarlarca insanın bilgi paylaştığı platformlar haline gelmiştir. Ancak bu platformlar, yanlış bilginin hızla yayılması için verimli bir ortam oluşturmaktadır [1]. Geleneksel yaklaşımlar, yanlış bilgi tespitine odaklanırken, kullanıcı düzeyinde risk tahmini genellikle ihmal edilmektedir.

Bulanık mantık, belirsizlik ve kesinlik eksikliği içeren problemlerin modellenmesinde güçlü bir araçtır [2]. Lotfi Zadeh tarafından 1965'te önerilen bulanık kümeler teorisi, klasik kümelerin ikili sınıflamasının ötesinde, kısmi üyelik kavramını tanıtmıştır [3].

Bu çalışmanın temel katkıları:
1. Sosyal ağ kullanıcıları için bulanık mantık tabanlı risk değerlendirme çerçevesi
2. Dört boyutlu giriş uzayında uzman bilgisine dayalı kural tabanı
3. Gerçek sosyal ağ verisi ile doğrulanmış sistem
4. İnteraktif GUI ile açıklanabilir çıkarım süreci

---

## 2. Literatür Taraması (Literature Review)

Yanlış bilgi yayılımı ve sosyal ağ analizi konularında kapsamlı bir literatür bulunmaktadır:

**Bulanık Mantık Temelleri:**
Zadeh [3] bulanık kümeleri tanıtarak belirsiz bilgi modellemesinin temellerini oluşturmuştur. Mamdani ve Assilian [4] sezgisel kontrolde bulanık çıkarımı uygulayarak Mamdani yöntemini geliştirmiştir.

**Sosyal Ağ Analizi:**
Barabási ve Albert [5] ölçeksiz ağların yapısını incelerken, Granovetter [6] zayıf bağların bilgi yayılımındaki rolünü ortaya koymuştur. Freeman [7] merkezlilik ölçütlerini sistematik olarak tanımlamıştır.

**Yanlış Bilgi Araştırmaları:**
Vosoughi et al. [8] Twitter'da yanlış haberlerin doğru haberlerden daha hızlı yayıldığını göstermiştir. Allcott ve Gentzkow [9] sosyal medyada yanlış bilginin etkilerini analiz etmiştir.

**Bulanık Mantık ve Sosyal Ağlar:**
Benevenuto et al. [10] sosyal ağlardaki spam tespiti için makine öğrenmesi yöntemlerini kullanmıştır. Mendoza et al. [11] sosyal ağlarda söylenti yayılımını incelemiştir.

**Güven ve Risk Modelleme:**
Marsh [12] dijital ortamlarda güven formalizasyonu üzerine çalışmıştır. Castillo et al. [13] Twitter'da bilgi güvenilirliğini otomatik değerlendirme yöntemi önermiştir.

---

## 3. Metodoloji (Methodology)

### 3.1 Sistem Mimarisi

Sistem, Şekil 1'de gösterildiği gibi beş ana bileşenden oluşmaktadır:
1. **Veri İşleme Hattı**: Sentetik veri üretimi ve graf analizi
2. **Bulanık Çıkarım Motoru**: Mamdani tipi FIS
3. **Simülasyon Motoru**: Büyük ölçekli risk hesaplama
4. **Karşılaştırma Modülü**: Temel model ile değerlendirme
5. **Görselleştirme**: Sonuç analizi ve raporlama

### 3.2 Giriş Değişkenleri

| Değişken | Simge | Aralık | Açıklama |
|----------|-------|--------|----------|
| Güven Skoru | T | [0, 1] | Kullanıcının güvenilirlik derecesi |
| Paylaşım Sıklığı | F | [0, 50] | Günlük ortalama gönderi sayısı |
| Duygu Sapması | S | [-1, +1] | Duygusal tutarsızlık ölçüsü |
| Merkezlilik Skoru | C | [0, 1] | Ağdaki konumsal önem |

### 3.3 Çıkış Değişkeni

**Yanlış Bilgi Risk Seviyesi (R)**: [0, 1] aralığında sürekli bir değer.
- R < 0.35: Düşük Risk
- 0.35 ≤ R < 0.65: Orta Risk
- R ≥ 0.65: Yüksek Risk

---

## 4. Bulanık Sistem Tasarımı (Fuzzy System Design)

### 4.1 Mamdani Çıkarım Yöntemi

Mamdani yöntemi dört adımdan oluşur:

**Adım 1 - Bulanıklaştırma (Fuzzification):**
Kesin giriş değeri x₀ için üyelik derecesi hesaplanır:

    μ_A(x₀) ∈ [0, 1]

**Adım 2 - Kural Değerlendirme (Rule Evaluation):**
Her kural için ateşleme gücü (α) hesaplanır:

    VE (AND): α = min(μ_A(x), μ_B(y))
    VEYA (OR): α = max(μ_A(x), μ_B(y))

**Adım 3 - Toplama (Aggregation):**
Tüm kuralların çıktıları birleştirilir:

    μ_agg(z) = max(μ₁(z), μ₂(z), ..., μₙ(z))

**Adım 4 - Durulaştırma (Defuzzification):**
Centroid (ağırlık merkezi) yöntemi ile kesin çıktı hesaplanır:

    z* = ∫ z · μ_agg(z) dz / ∫ μ_agg(z) dz

---

## 5. Üyelik Fonksiyonları (Membership Functions)

### 5.1 Üçgensel Fonksiyon (Triangular - trimf)

Parametreler: [a, b, c] (sol taban, tepe, sağ taban)

    μ(x) = 0,           x ≤ a veya x ≥ c
    μ(x) = (x-a)/(b-a), a < x ≤ b
    μ(x) = (c-x)/(c-b), b < x < c

### 5.2 Yamuksal Fonksiyon (Trapezoidal - trapmf)

Parametreler: [a, b, c, d] (sol taban, sol tepe, sağ tepe, sağ taban)

    μ(x) = 0,           x ≤ a veya x ≥ d
    μ(x) = (x-a)/(b-a), a < x ≤ b
    μ(x) = 1,           b < x ≤ c
    μ(x) = (d-x)/(d-c), c < x < d

### 5.3 Değişken Tanımları

Karışık yaklaşım kullanılmıştır: uç terimler için yamuksal, orta terimler için üçgensel.

**Güven Skoru:**
- Düşük: trapmf([0, 0, 0.15, 0.4])
- Orta: trimf([0.2, 0.5, 0.8])
- Yüksek: trapmf([0.6, 0.85, 1, 1])

**Paylaşım Sıklığı:**
- Düşük: trapmf([0, 0, 5, 15])
- Orta: trimf([8, 20, 35])
- Yüksek: trapmf([25, 40, 50, 50])

**Duygu Sapması (simetrik):**
- Kararlı: trapmf([-0.3, -0.1, 0.1, 0.3])
- Orta: trimf([±0.15, ±0.45, ±0.75])
- Değişken: trapmf([±0.55, ±0.75, ±1, ±1])

**Merkezlilik Skoru:**
- Düşük: trapmf([0, 0, 0.15, 0.4])
- Orta: trimf([0.2, 0.5, 0.8])
- Yüksek: trapmf([0.6, 0.85, 1, 1])

---

## 6. Kural Tabanı (Rule Base)

30 adet uzman bilgisine dayalı kural tanımlanmıştır. Aşağıda temsili örnekler verilmiştir:

| No | Öncül | Sonuç | Gerekçe |
|----|-------|-------|---------|
| K1 | Güven=Düşük VE Paylaşım=Yüksek | Risk=Yüksek | Güvenilmez aktif kullanıcılar tehlikelidir |
| K2 | Güven=Yüksek VE Duygu=Kararlı | Risk=Düşük | Güvenilir tutarlı kullanıcılar güvenlidir |
| K5 | Merkezlilik=Yüksek VE Paylaşım=Yüksek | Risk=Yüksek | Merkezi aktif kullanıcılar bilgiyi hızla yayar |
| K9 | Güven=Düşük VE Paylaşım=Yüksek VE Duygu=Değişken | Risk=Yüksek | En tehlikeli kombinasyon |
| K10 | Güven=Yüksek VE Paylaşım=Düşük VE Duygu=Kararlı | Risk=Düşük | En güvenli profil |
| K21 | Güven=Düşük VE Paylaşım=Düşük VE Merkezlilik=Düşük | Risk=Düşük | Güvenilmez ama etkisiz |

---

## 7. Deneyler ve Sonuçlar (Experiments and Results)

### 7.1 Veri Seti
- **Gerçek veri**: Facebook Combined (SNAP Stanford) - 4039 düğüm, 88234 kenar
- **Sentetik veri**: 1000 örnek
  - Güven: Uniform(0, 1)
  - Paylaşım: Poisson(λ=8)
  - Duygu: Normal(μ=0, σ=0.35)
  - Merkezlilik: Beta(α=2, β=5) + gerçek graf entegrasyonu

### 7.2 Simülasyon Sonuçları
1000 örneklik simülasyonda:
- Ortalama risk: ~0.45
- Risk dağılımı: sağa hafif çarpık
- Kategori dağılımı yaklaşık Düşük: %30, Orta: %45, Yüksek: %25

### 7.3 Duyarlılık Analizi
- **Güven ↑ → Risk ↓**: Güçlü negatif korelasyon
- **Duygu değişkenliği ↑ → Risk ↑**: Pozitif korelasyon
- **Merkezlilik ↑ → Risk ↑**: Orta düzey pozitif etki
- **Paylaşım sıklığı ↑ → Risk ↑**: Bağlama bağlı etki

### 7.4 Karşılaştırma Modeli

Ağırlıklı doğrusal temel model:

    Risk = 0.30·(1-T) + 0.25·(F/50) + 0.20·|S| + 0.25·C

Karşılaştırma metrikleri bulanık modelin daha zengin ve doğrusal olmayan ilişkileri yakalayabildiğini göstermektedir.

---

## 8. Tartışma (Discussion)

### 8.1 Bulanık Mantık Avantajları
- Belirsizlik altında karar verme yeteneği
- Uzman bilgisinin doğrudan sisteme entegrasyonu
- Yorumlanabilir ve açıklanabilir sonuçlar
- Kademeli geçişler (düşükten yükseğe yumuşak geçiş)

### 8.2 Sınırlılıklar
- Uzman bilgisine dayalı kural tasarımı sübjektif olabilir
- Dört giriş değişkeni yeterli olmayabilir
- Zaman bağımlı davranışlar modellenmemiştir
- Gerçek dünya doğrulaması sınırlıdır

### 8.3 Gelecek Çalışmalar
- Tip-2 bulanık mantık ile belirsizliğin daha iyi modellenmesi
- Uyarlanabilir ağ tabanlı bulanık çıkarım (ANFIS) ile optimizasyon
- Temporal analiz entegrasyonu
- Büyük ölçekli sosyal ağ verileri ile doğrulama

---

## 9. Sonuç (Conclusion)

Bu çalışmada, sosyal ağlarda yanlış bilgi yayma riskini değerlendirmek için Mamdani tipi bir bulanık çıkarım sistemi geliştirilmiştir. Sistem, dört giriş değişkeni (güven skoru, paylaşım sıklığı, duygu sapması, merkezlilik skoru) kullanarak kullanıcı düzeyinde risk tahmini üretmektedir.

30 adet uzman kuralı ile desteklenen sistem, üçgensel ve yamuksal üyelik fonksiyonlarını kullanmaktadır. Facebook sosyal ağ verisi üzerinde yapılan deneyler, sistemin anlamlı ve tutarlı risk değerlendirmeleri ürettiğini göstermiştir.

Bulanık mantık yaklaşımı, doğrusal modellere kıyasla sosyal davranışlardaki belirsizlikleri daha etkili modelleme kapasitesine sahiptir. Açıklanabilir yapısı sayesinde, karar vericilere risk seviyeleri hakkında sezgisel ve yorumlanabilir bilgi sunmaktadır.

---

## Kaynaklar (References)

[1] Lazer, D. M. J., Baum, M. A., Benkler, Y., et al. (2018). "The science of fake news." *Science*, 359(6380), 1094-1096.

[2] Ross, T. J. (2010). *Fuzzy Logic with Engineering Applications*. John Wiley & Sons.

[3] Zadeh, L. A. (1965). "Fuzzy sets." *Information and Control*, 8(3), 338-353.

[4] Mamdani, E. H., & Assilian, S. (1975). "An experiment in linguistic synthesis with a fuzzy logic controller." *International Journal of Man-Machine Studies*, 7(1), 1-13.

[5] Barabási, A. L., & Albert, R. (1999). "Emergence of scaling in random networks." *Science*, 286(5439), 509-512.

[6] Granovetter, M. S. (1973). "The strength of weak ties." *American Journal of Sociology*, 78(6), 1360-1380.

[7] Freeman, L. C. (1978). "Centrality in social networks conceptual clarification." *Social Networks*, 1(3), 215-239.

[8] Vosoughi, S., Roy, D., & Aral, S. (2018). "The spread of true and false news online." *Science*, 359(6380), 1146-1151.

[9] Allcott, H., & Gentzkow, M. (2017). "Social media and fake news in the 2016 election." *Journal of Economic Perspectives*, 31(2), 211-236.

[10] Benevenuto, F., Magno, G., Rodrigues, T., & Almeida, V. (2010). "Detecting spammers on Twitter." *Collaboration, Electronic Messaging, Anti-Abuse and Spam Conference (CEAS)*.

[11] Mendoza, M., Poblete, B., & Castillo, C. (2010). "Twitter under crisis: Can we trust what we RT?" *Proceedings of the First Workshop on Social Media Analytics*, 71-79.

[12] Marsh, S. P. (1994). "Formalising trust as a computational concept." *PhD Thesis*, University of Stirling.

[13] Castillo, C., Mendoza, M., & Poblete, B. (2011). "Information credibility on Twitter." *Proceedings of the 20th International Conference on World Wide Web*, 675-684.

---

*Bu rapor, "Sosyal Ağlarda Yanlış Bilgi Riskinin Bulanık Mantık ile Modellenmesi" projesi kapsamında hazırlanmıştır.*
