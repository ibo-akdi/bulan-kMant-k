# -*- coding: utf-8 -*-
"""
Matematiksel Formül Oluşturucu (LaTeX)
=====================================
Bulanık mantık üyelik fonksiyonları için parçalı matematik (piecewise) 
fonksiyonların LaTeX kodlarını üretir ve Matplotlib kullanarak
siyah arkaplanlı formül resimleri (PNG) olarak kaydeder.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Matplotlib varsayılan font ayarları
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['mathtext.fontset'] = 'cm' # Computer Modern (Standart LaTeX fontu)

def get_trimf_latex(symbol, a, b, c, for_matplotlib=False):
    """Üçgensel üyelik fonksiyonu için LaTeX stringi üretir."""
    def fmt(val):
        return f"{val:g}"
        
    lines = []
    
    if a == b:
        # Sadece sağ düşen omuz
        lines.append(rf"1 & x \le {fmt(a)}")
        lines.append(rf"\frac{{{fmt(c)} - x}}{{{fmt(c-b)}}} & {fmt(b)} < x \le {fmt(c)}")
        lines.append(rf"0 & x > {fmt(c)}")
    elif b == c:
        # Sadece sol çıkan omuz
        lines.append(rf"0 & x \le {fmt(a)}")
        lines.append(rf"\frac{{x - {fmt(a)}}}{{{fmt(b-a)}}} & {fmt(a)} < x \le {fmt(b)}")
        lines.append(rf"1 & x > {fmt(b)}")
    else:
        # Normal üçgen
        lines.append(rf"0 & x \le {fmt(a)}")
        lines.append(rf"\frac{{x - {fmt(a)}}}{{{fmt(b-a)}}} & {fmt(a)} < x \le {fmt(b)}")
        lines.append(rf"\frac{{{fmt(c)} - x}}{{{fmt(c-b)}}} & {fmt(b)} < x \le {fmt(c)}")
        lines.append(rf"0 & x > {fmt(c)}")
        
    if for_matplotlib:
        cases_str = " \\\\ \n".join(lines)
        latex_str = rf"$\mu_{{{symbol}}}(x) = \left\{{ \begin{{array}}{{ll}} {cases_str} \end{{array}} \right.$"
    else:
        cases_str = " \\\\ \n".join(lines)
        latex_str = rf"\mu_{{{symbol}}}(x) = \begin{{cases}} {cases_str} \end{{cases}}"
        
    return latex_str


def get_trapmf_latex(symbol, a, b, c, d, for_matplotlib=False):
    """Yamuksal üyelik fonksiyonu için LaTeX stringi üretir."""
    def fmt(val):
        return f"{val:g}"
        
    lines = []
    
    if a == b and c == d:
        # Kesin aralık
        lines.append(rf"1 & {fmt(a)} \le x \le {fmt(c)}")
        lines.append(rf"0 & \text{{diğer}}")
        
    elif a == b: 
        # Sol omuz (Baştan 1 başlar)
        lines.append(rf"1 & x \le {fmt(c)}")
        lines.append(rf"\frac{{{fmt(d)} - x}}{{{fmt(d-c)}}} & {fmt(c)} < x \le {fmt(d)}")
        lines.append(rf"0 & x > {fmt(d)}")
        
    elif c == d: 
        # Sağ omuz (Sonda 1 olarak kalır)
        lines.append(rf"0 & x \le {fmt(a)}")
        lines.append(rf"\frac{{x - {fmt(a)}}}{{{fmt(b-a)}}} & {fmt(a)} < x \le {fmt(b)}")
        lines.append(rf"1 & x > {fmt(b)}")
        
    else: 
        # Normal yamuk
        lines.append(rf"0 & x \le {fmt(a)}")
        lines.append(rf"\frac{{x - {fmt(a)}}}{{{fmt(b-a)}}} & {fmt(a)} < x \le {fmt(b)}")
        lines.append(rf"1 & {fmt(b)} < x \le {fmt(c)}")
        lines.append(rf"\frac{{{fmt(d)} - x}}{{{fmt(d-c)}}} & {fmt(c)} < x \le {fmt(d)}")
        lines.append(rf"0 & x > {fmt(d)}")

    if for_matplotlib:
        cases_str = " \\\\ \n".join(lines)
        latex_str = rf"$\mu_{{{symbol}}}(x) = \left\{{ \begin{{array}}{{ll}} {cases_str} \end{{array}} \right.$"
    else:
        cases_str = " \\\\ \n".join(lines)
        latex_str = rf"\mu_{{{symbol}}}(x) = \begin{{cases}} {cases_str} \end{{cases}}"
        
    return latex_str


def save_formula_image(latex_str, label_text, file_path):
    """
    Siyah arkaplanlı matematiksel formül resmi üretir.
    Gönderdiğiniz örnek resim stiline (%100 benzetilmiş) göre tasarlandı.
    """
    fig = plt.figure(figsize=(10, 4), facecolor='#111111')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_facecolor('#111111')
    
    # Sol üste başlık (Örn: "Düşük (Yamuk Fonksiyon - trap(0, 0, 25, 45)):")
    ax.text(0.05, 0.85, label_text, color='white', fontsize=18, fontweight='bold',
            transform=ax.transAxes, ha='left', va='center')
    
    # Ortaya formül
    ax.text(0.65, 0.4, latex_str, color='white', fontsize=26,
            transform=ax.transAxes, ha='center', va='center')
    
    # Klasör yoksa oluştur
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    plt.savefig(file_path, facecolor=fig.get_facecolor(), edgecolor='none', 
                dpi=200, bbox_inches='tight', pad_inches=0.3)
    plt.close()


def tum_formulleri_uret(cikti_dizini=None):
    """
    Sistemdeki değişkenlerin formül resimlerini üretir.
    """
    if cikti_dizini is None:
        cikti_dizini = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "output", "formulas"
        )
        
    os.makedirs(cikti_dizini, exist_ok=True)
    print(f"[FORMÜLLER] Resimler {cikti_dizini} dizinine üretiliyor...")
    
    # Tanımlar (BulanikCikarimSistemi - karisik tipe gore)
    # GUVEN SKORU
    # Dusuk: trapmf(0, 0, 0.15, 0.4)
    # Orta: trimf(0.2, 0.5, 0.8)
    # Yuksek: trapmf(0.6, 0.85, 1, 1)
    # Sembol: G
    
    save_formula_image(
        get_trapmf_latex('G', 0, 0, 0.15, 0.4, for_matplotlib=True),
        "Güven Düşük (Yamuk Fonksiyon - trap(0, 0, 0.15, 0.4)):",
        os.path.join(cikti_dizini, "guven_dusuk.png")
    )
    save_formula_image(
        get_trimf_latex('G', 0.2, 0.5, 0.8, for_matplotlib=True),
        "Güven Orta (Üçgen Fonksiyon - tri(0.2, 0.5, 0.8)):",
        os.path.join(cikti_dizini, "guven_orta.png")
    )
    save_formula_image(
        get_trapmf_latex('G', 0.6, 0.85, 1, 1, for_matplotlib=True),
        "Güven Yüksek (Yamuk Fonksiyon - trap(0.6, 0.85, 1, 1)):",
        os.path.join(cikti_dizini, "guven_yuksek.png")
    )
    
    # PAYLASIM SIKLIGI
    # Sembol: P
    save_formula_image(
        get_trapmf_latex('P', 0, 0, 5, 15, for_matplotlib=True),
        "Paylaşım Düşük (Yamuk Fonksiyon - trap(0, 0, 5, 15)):",
        os.path.join(cikti_dizini, "paylasim_dusuk.png")
    )
    save_formula_image(
        get_trimf_latex('P', 8, 20, 35, for_matplotlib=True),
        "Paylaşım Orta (Üçgen Fonksiyon - tri(8, 20, 35)):",
        os.path.join(cikti_dizini, "paylasim_orta.png")
    )
    save_formula_image(
        get_trapmf_latex('P', 25, 40, 50, 50, for_matplotlib=True),
        "Paylaşım Yüksek (Yamuk Fonksiyon - trap(25, 40, 50, 50)):",
        os.path.join(cikti_dizini, "paylasim_yuksek.png")
    )

    # DUYGU SAPMASI
    # Sembol: D
    save_formula_image(
        get_trapmf_latex('S', -1, -1, -0.6, -0.3, for_matplotlib=True),
        "Duygu Negatif Değişken (Yamuk - trap(-1, -1, -0.6, -0.3)):",
        os.path.join(cikti_dizini, "duygu_neg_degisken.png")
    )
    # Karisik tipteki Duygu tanimini baz alarak:
    save_formula_image(
        get_trapmf_latex('S', -0.3, -0.1, 0.1, 0.3, for_matplotlib=True),
        "Duygu Kararlı (Yamuk - trap(-0.3, -0.1, 0.1, 0.3)):",
        os.path.join(cikti_dizini, "duygu_kararli.png")
    )
    
    # MERKEZLILIK
    # Sembol: C
    save_formula_image(
        get_trapmf_latex('C', 0, 0, 0.15, 0.4, for_matplotlib=True),
        "Merkezlilik Düşük (Yamuk - trap(0, 0, 0.15, 0.4)):",
        os.path.join(cikti_dizini, "merkezlilik_dusuk.png")
    )
    save_formula_image(
        get_trimf_latex('C', 0.2, 0.5, 0.8, for_matplotlib=True),
        "Merkezlilik Orta (Üçgen - tri(0.2, 0.5, 0.8)):",
        os.path.join(cikti_dizini, "merkezlilik_orta.png")
    )
    save_formula_image(
        get_trapmf_latex('C', 0.6, 0.85, 1, 1, for_matplotlib=True),
        "Merkezlilik Yüksek (Yamuk - trap(0.6, 0.85, 1, 1)):",
        os.path.join(cikti_dizini, "merkezlilik_yuksek.png")
    )
    
    print("[FORMÜLLER] Tüm resimler başarıyla oluşturuldu!")


if __name__ == "__main__":
    tum_formulleri_uret()
