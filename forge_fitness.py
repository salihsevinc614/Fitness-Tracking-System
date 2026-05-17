# Forge Fitness - Masaustu uygulamasi (Tkinter ile)
# Salihbabapiro - Bilgisayar Programciligi Projesi
# Pencere seklinde acilan fitness ve beslenme takip uygulamasi.

import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime


# ============================================================
# RENK PALETI - Neon yesil, neon mavi, neon sari teması
# ============================================================

ARKA_PLAN    = "#0a0a0f"        # neredeyse siyah, neon icin guzel kontrast
KART_RENK    = "#15151f"        # kartlarin arka plani
NEON_YESIL   = "#39ff14"
NEON_MAVI    = "#00ffff"
NEON_SARI    = "#ffff00"
KIRMIZI      = "#ff3860"
BEYAZ        = "#ffffff"


# Yazi tipleri (buyuk ve okunakli olsun diye)
BASLIK_FONT  = ("Impact", 36, "bold")
ALTBAS_FONT  = ("Verdana", 16, "bold")
NORMAL_FONT  = ("Verdana", 14)
BUYUK_FONT   = ("Verdana", 18, "bold")
DEV_FONT     = ("Impact", 48, "bold")
BUTON_FONT   = ("Verdana", 13, "bold")


# Verinin saklanacagi dosya
DOSYA = "forge_kullanici.json"


# ============================================================
# KULLANICI VERISI ICIN YARDIMCI FONKSIYONLAR
# ============================================================

def kullaniciyi_yukle():
    # Dosya varsa kullanici bilgilerini yukle
    if not os.path.exists(DOSYA):
        return None
    try:
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def kullaniciyi_kaydet(kullanici):
    # JSON dosyasina yaz
    try:
        with open(DOSYA, "w", encoding="utf-8") as f:
            json.dump(kullanici, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Hata", f"Kayit sorunu: {e}")


# ============================================================
# HESAPLAMA FONKSIYONLARI
# ============================================================

def vki_hesapla(kilo, boy):
    # boy cm cinsinden geliyor, metreye cevirip hesapla
    boy_m = boy / 100
    return round(kilo / (boy_m * boy_m), 2)


def vki_yorumla(vki):
    # WHO standartlarina gore
    if vki < 18.5:
        return ("ZARGANASIN!", "Daha cok protein ve saglikli karbonhidrat tuket. Kas yapmaya odaklan.", KIRMIZI)
    elif vki < 25:
        return ("NORMAL KILODASIN!", "Harika bir aralikta! Bu dengeyi koru.", NEON_YESIL)
    elif vki < 30:
        return ("FAZLA KILOLUSUN! ŞİŞKO PATATES, YARIM KİLO PATATES", "Kardiyo ve dengeli beslenmeye dikkat etmelisin.", NEON_SARI)
    else:
        return ("YAGLISIN!", "Saglik icin acilen beslenme + spor programina baslamalisin.", KIRMIZI)


def gunluk_kalori_hesapla(kullanici):
    # Mifflin-St Jeor formulu
    kilo = kullanici["kilo"]
    boy = kullanici["boy"]
    yas = kullanici["yas"]
    cinsiyet = kullanici["cinsiyet"]
    
    if cinsiyet == "E":
        bmr = 10 * kilo + 6.25 * boy - 5 * yas + 5
    else:
        bmr = 10 * kilo + 6.25 * boy - 5 * yas - 161
    
    # Orta aktivite (haftada 3-5 gun spor)
    gunluk = bmr * 1.55
    
    # Hedefe gore ayarla
    hedef = kullanici["hedef"]
    if hedef == "kilo_verme":
        gunluk -= 400
    elif hedef == "guc_kazanma":
        gunluk += 350
    
    return round(gunluk)


# ============================================================
# SABIT VERILER - Antreman, beslenme ve tarifler
# ============================================================

ANTREMAN_PROGRAMI = {
    "kilo_verme": [
        "Pazartesi  >>  30 dk kosu + 20 dk HIIT",
        "Sali       >>  Tum vucut agirlik (12-15 tekrar)",
        "Carsamba   >>  45 dk hizli yuruyus + plank",
        "Persembe   >>  Bisiklet veya yuzme 40 dk",
        "Cuma       >>  Devre antremani (squat, push-up, burpee)",
        "Cumartesi  >>  Aktif dinlenme (esneme, yoga)",
        "Pazar      >>  Tam dinlenme"
    ],
    "boy_uzatma": [
        "Pazartesi  >>  Sabah esneme + barfix asili kalma 3x30sn",
        "Sali       >>  Yuzme 40 dk (en cok yardim eden spor)",
        "Carsamba   >>  Yoga ve omurga esnetme",
        "Persembe   >>  Basketbol veya voleybol (sicramalar)",
        "Cuma       >>  Barfix asili + ip atlama",
        "Cumartesi  >>  Yuzme veya bisiklet",
        "Pazar      >>  Esneme rutini"
    ],
    "kondisyon": [
        "Pazartesi  >>  5 km kosu (orta tempo)",
        "Sali       >>  HIIT 25 dk + core",
        "Carsamba   >>  Bisiklet 1 saat",
        "Persembe   >>  Interval kosu (1dk hizli, 2dk yavas)",
        "Cuma       >>  Yuzme veya kurek 45 dk",
        "Cumartesi  >>  Uzun mesafe kosu (8-10 km)",
        "Pazar      >>  Hafif yuruyus"
    ],
    "guc_kazanma": [
        "Pazartesi  >>  Gogus + triceps (bench press, dips)",
        "Sali       >>  Sirt + biceps (deadlift, barfix)",
        "Carsamba   >>  Dinlenme",
        "Persembe   >>  Bacak (squat, lunge, leg press)",
        "Cuma       >>  Omuz + karin (military press, plank)",
        "Cumartesi  >>  Tam vucut yuksek hacim",
        "Pazar      >>  Dinlenme + protein agirlikli beslenme"
    ],
    "hiz_kazanma": [
        "Pazartesi  >>  Sprint 10x100m + esneme",
        "Sali       >>  Pliometrik (kutu sicramasi, broad jump)",
        "Carsamba   >>  Bacak gucu (squat, lunge)",
        "Persembe   >>  Tepe kosulari 8x",
        "Cuma       >>  Ceviklik merdiveni + slalom",
        "Cumartesi  >>  Uzun kosu + sprint kombosu",
        "Pazar      >>  Dinlenme"
    ],
    "dovus_sporlari": [
        "Pazartesi  >>  Boks teknikleri + kum torbasi 30 dk",
        "Sali       >>  Yer calisma (gures, BJJ) + esneme",
        "Carsamba   >>  Kondisyon + ip atlama 15 dk",
        "Persembe   >>  Tekme teknikleri (Muay Thai)",
        "Cuma       >>  Sparring (yumusak tempo)",
        "Cumartesi  >>  Core + grip kuvveti",
        "Pazar      >>  Yoga ve esneme"
    ]
}


BESLENME_MENULERI = {
    "kilo_verme": {
        "Kahvalti":   "2 haslanmis yumurta + tam bugday ekmek + domates/salatalik + cay",
        "Ara ogun 1": "1 elma + 10 badem",
        "Ogle":       "Izgara tavuk gogsu + bulgur pilavi + yesil salata",
        "Ara ogun 2": "Yogurt + tarcin",
        "Aksam":      "Firinda balik + sebzeli salata + 1 dilim tam bugday ekmek"
    },
    "boy_uzatma": {
        "Kahvalti":   "Sut + yulaf ezmesi + muz + ceviz (kalsiyum cok onemli)",
        "Ara ogun 1": "Peynir + tam bugday ekmek",
        "Ogle":       "Tavuk veya hindi + makarna + brokoli/havuc",
        "Ara ogun 2": "Sutlu kahve veya 1 bardak sut",
        "Aksam":      "Et yemegi + bulgur pilavi + cacik"
    },
    "kondisyon": {
        "Kahvalti":   "Yulaf ezmesi + yaban mersini + bal + 1 yumurta",
        "Ara ogun 1": "Muz + fistik ezmesi",
        "Ogle":       "Tavuk + esmer pirinc + sebzeli salata",
        "Ara ogun 2": "Yogurt + granola",
        "Aksam":      "Hindi + tatli patates + brokoli"
    },
    "guc_kazanma": {
        "Kahvalti":   "4 yumurta omlet + peynir + 2 dilim tam ekmek + 1 bardak sut",
        "Ara ogun 1": "Protein shake + muz + fistik ezmesi",
        "Ogle":       "200gr tavuk gogsu + 1 buyuk porsiyon pirinc + sebze",
        "Ara ogun 2": "Yogurt + 30gr ceviz/badem",
        "Aksam":      "200gr kirmizi et + makarna + ay cekirdegi"
    },
    "hiz_kazanma": {
        "Kahvalti":   "Yulaf + muz + bal + 2 yumurta beyazi",
        "Ara ogun 1": "Hurma + ceviz (hizli enerji)",
        "Ogle":       "Tavuk + pirinc + roka salatasi",
        "Ara ogun 2": "Smoothie (sut + muz + yaban mersini)",
        "Aksam":      "Somon + kinoa + buharlanmis sebze"
    },
    "dovus_sporlari": {
        "Kahvalti":   "Yulaf + 3 yumurta + muz (komplex karbonhidrat onemli)",
        "Ara ogun 1": "Elma + badem yagi",
        "Ogle":       "Tavuk veya dana + bulgur + cok yesil",
        "Ara ogun 2": "Tuna konservesi + tam ekmek",
        "Aksam":      "Kirmizi et + tatli patates + ispanak"
    }
}


YEMEK_TARIFLERI = [
    {
        "ad": "Protein Yulaf Kasesi",
        "malzeme": ["1 fincan yulaf", "1 bardak sut", "1 muz",
                    "1 tatli kasik bal", "5-6 badem", "Tarcin"],
        "yapilis": "Yulaf ve sutu kisik atese koy, 5 dk karistir. "
                   "Muzi dilimle, uzerine bal ve tarcin serp. "
                   "Bademleri ekle. Hazir!"
    },
    {
        "ad": "Izgara Tavuk Bowl",
        "malzeme": ["150gr tavuk gogsu", "Yarim bardak bulgur",
                    "Domates", "Salatalik", "Marul",
                    "Limon", "Zeytinyagi"],
        "yapilis": "Tavugu baharatla ve izgarada pisir. "
                   "Bulguru haslat. Sebzeleri dogra. Hepsini "
                   "bowl'a koy, limon ve zeytinyagi gez."
    },
    {
        "ad": "Firinda Somon",
        "malzeme": ["1 somon fileto", "Limon", "Zeytinyagi",
                    "Karabiber", "Brokoli", "Havuc"],
        "yapilis": "Somonu yag, limon ve baharatla marine et. "
                   "Sebzelerle birlikte 200 derecede 20 dk firinla. "
                   "Cok kolay ve saglikli."
    },
    {
        "ad": "Protein Smoothie",
        "malzeme": ["1 muz", "1 bardak sut",
                    "1 yemek kasigi fistik ezmesi",
                    "1 olcek protein tozu (varsa)", "Buz"],
        "yapilis": "Hepsini blendera at, 30 saniye karistir. "
                   "Antremandan sonra ic."
    },
    {
        "ad": "Yogurtlu Sebze Kahvaltisi",
        "malzeme": ["Suzme yogurt", "Salatalik", "Maydanoz",
                    "Ceviz", "Zeytinyagi", "Tuz"],
        "yapilis": "Salatalik ve maydanozu ince dogra, yogurda kat. "
                   "Cevizleri kir ust, zeytinyagi gezdir. "
                   "Protein ve probiyotik dolu!"
    }
]


HEDEF_ISIMLERI = {
    "kilo_verme":    "KILO VERME",
    "boy_uzatma":    "BOY UZATMA",
    "kondisyon":     "KONDISYON",
    "guc_kazanma":   "GUC KAZANMA",
    "hiz_kazanma":   "HIZ KAZANMA",
    "dovus_sporlari": "DOVUS SPORLARI"
}


# ============================================================
# ANA UYGULAMA SINIFI
# ============================================================

class ForgeFitnessApp:
    
    def __init__(self, pencere):
        # Ana pencere ayarlari
        self.pencere = pencere
        self.pencere.title("FORGE FITNESS")
        self.pencere.geometry("900x750")
        self.pencere.configure(bg=ARKA_PLAN)
        self.pencere.minsize(800, 600)
        
        # Kullaniciyi yukle
        self.kullanici = kullaniciyi_yukle()
        
        # Hangi ekrandayiz onu tutmak icin frame referansi
        self.aktif_frame = None
        
        # Eger kullanici yoksa kayit ekranina, varsa ana menuye git
        if self.kullanici is None:
            self.kayit_ekrani_goster()
        else:
            self.ana_menu_goster()
    
    
    # --------- Ortak yardimcilar ---------
    
    def temizle(self):
        # Aktif frame varsa sil (ekran degisimi icin)
        if self.aktif_frame is not None:
            self.aktif_frame.destroy()
        self.aktif_frame = tk.Frame(self.pencere, bg=ARKA_PLAN)
        self.aktif_frame.pack(fill="both", expand=True)
    
    
    def baslik_ekle(self, frame, yazi, renk=NEON_YESIL):
        # Buyuk baslik etiketi
        etiket = tk.Label(
            frame, text=yazi,
            font=BASLIK_FONT, fg=renk, bg=ARKA_PLAN
        )
        etiket.pack(pady=(20, 10))
        
        # Altina cizgi (kucuk renkli bar)
        cizgi = tk.Frame(frame, bg=NEON_MAVI, height=3, width=400)
        cizgi.pack(pady=(0, 20))
    
    
    def neon_buton(self, frame, yazi, komut, renk=NEON_YESIL, genislik=30):
        # Tkinter butonunu neon temaya gore stillendir
        btn = tk.Button(
            frame, text=yazi,
            font=BUTON_FONT,
            fg=ARKA_PLAN, bg=renk,
            activebackground=renk, activeforeground=ARKA_PLAN,
            relief="flat", bd=0,
            width=genislik, height=2,
            cursor="hand2",
            command=komut
        )
        # Hover efekti icin renk degistir
        def gir(e): btn.configure(bg=NEON_SARI)
        def cik(e): btn.configure(bg=renk)
        btn.bind("<Enter>", gir)
        btn.bind("<Leave>", cik)
        return btn
    
    
    # ========================================================
    # EKRAN 1: KAYIT EKRANI
    # ========================================================
    
    def kayit_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        # Logo / baslik
        tk.Label(f, text="FORGE FITNESS",
                 font=DEV_FONT, fg=NEON_YESIL, bg=ARKA_PLAN).pack(pady=(30, 5))
        tk.Label(f, text="Kisisel antreman ve beslenme programin",
                 font=NORMAL_FONT, fg=NEON_MAVI, bg=ARKA_PLAN).pack(pady=(0, 30))
        
        # Form alani icin orta kart
        kart = tk.Frame(f, bg=KART_RENK, padx=40, pady=30)
        kart.pack(pady=10)
        
        tk.Label(kart, text=">> ILK KAYIT <<",
                 font=ALTBAS_FONT, fg=NEON_SARI, bg=KART_RENK).pack(pady=(0, 20))
        
        # Form elemanlarini olustur
        self.giris_kutulari = {}
        
        # Isim
        self._form_satiri(kart, "Adin:", "isim")
        # Yas
        self._form_satiri(kart, "Yasin:", "yas")
        # Boy
        self._form_satiri(kart, "Boyun (cm):", "boy")
        # Kilo
        self._form_satiri(kart, "Kilon (kg):", "kilo")
        
        # Cinsiyet (radio butonlar)
        cins_frame = tk.Frame(kart, bg=KART_RENK)
        cins_frame.pack(pady=10, anchor="w")
        tk.Label(cins_frame, text="Cinsiyet:",
                 font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK, width=12, anchor="w").pack(side="left")
        
        self.cinsiyet_var = tk.StringVar(value="E")
        for kod, etk in [("E", "Erkek"), ("K", "Kadin")]:
            rb = tk.Radiobutton(
                cins_frame, text=etk, value=kod,
                variable=self.cinsiyet_var,
                font=NORMAL_FONT, fg=NEON_YESIL, bg=KART_RENK,
                selectcolor=ARKA_PLAN, activebackground=KART_RENK,
                activeforeground=NEON_SARI
            )
            rb.pack(side="left", padx=10)
        
        # Fitness hedefi
        tk.Label(kart, text="Fitness Hedefin:",
                 font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK).pack(pady=(15, 5), anchor="w")
        
        self.hedef_var = tk.StringVar(value="kilo_verme")
        hedef_frame = tk.Frame(kart, bg=KART_RENK)
        hedef_frame.pack(anchor="w")
        
        # Hedefleri 2 sutuna yerlestir
        hedefler_listesi = list(HEDEF_ISIMLERI.items())
        for i, (kod, ad) in enumerate(hedefler_listesi):
            satir = i // 2
            sutun = i % 2
            rb = tk.Radiobutton(
                hedef_frame, text=ad, value=kod,
                variable=self.hedef_var,
                font=NORMAL_FONT, fg=NEON_MAVI, bg=KART_RENK,
                selectcolor=ARKA_PLAN, activebackground=KART_RENK,
                activeforeground=NEON_SARI,
                width=18, anchor="w"
            )
            rb.grid(row=satir, column=sutun, padx=5, pady=3, sticky="w")
        
        # Kaydet butonu
        self.neon_buton(kart, "KAYDET VE BASLA",
                        self._kayit_kaydet, NEON_YESIL).pack(pady=20)
    
    
    def _form_satiri(self, parent, etiket, anahtar):
        # Bir form satiri olustur (etiket + giris kutusu)
        satir = tk.Frame(parent, bg=KART_RENK)
        satir.pack(pady=8, fill="x")
        
        tk.Label(satir, text=etiket,
                 font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK,
                 width=12, anchor="w").pack(side="left")
        
        giris = tk.Entry(satir, font=NORMAL_FONT,
                         fg=NEON_YESIL, bg=ARKA_PLAN,
                         insertbackground=NEON_YESIL,
                         relief="flat", width=25)
        giris.pack(side="left", ipady=5)
        
        self.giris_kutulari[anahtar] = giris
    
    
    def _kayit_kaydet(self):
        # Form bilgilerini al, dogrula, kaydet
        try:
            isim = self.giris_kutulari["isim"].get().strip()
            yas = int(self.giris_kutulari["yas"].get())
            boy = float(self.giris_kutulari["boy"].get())
            kilo = float(self.giris_kutulari["kilo"].get())
        except ValueError:
            messagebox.showerror("Hata", "Lutfen sayi alanlarini dogru doldur!")
            return
        
        # Kontroller
        if isim == "":
            messagebox.showerror("Hata", "Isim bos olamaz!")
            return
        if yas < 10 or yas > 100:
            messagebox.showerror("Hata", "Yas 10-100 arasi olmali.")
            return
        if boy < 100 or boy > 250:
            messagebox.showerror("Hata", "Boy 100-250 cm arasi olmali.")
            return
        if kilo < 25 or kilo > 300:
            messagebox.showerror("Hata", "Kilo 25-300 kg arasi olmali.")
            return
        
        # Kullaniciyi olustur
        self.kullanici = {
            "isim": isim,
            "yas": yas,
            "boy": boy,
            "kilo": kilo,
            "cinsiyet": self.cinsiyet_var.get(),
            "hedef": self.hedef_var.get(),
            "kayit_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "gecmis": []
        }
        kullaniciyi_kaydet(self.kullanici)
        
        messagebox.showinfo("Basarili!",
                            f"Hosgeldin {isim}! Forge Fitness'a kaydoldun.")
        self.ana_menu_goster()
    
    
    # ========================================================
    # EKRAN 2: ANA MENU
    # ========================================================
    
    def ana_menu_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        # Ust kisim - logo ve karsilama
        tk.Label(f, text="FORGE FITNESS",
                 font=DEV_FONT, fg=NEON_YESIL, bg=ARKA_PLAN).pack(pady=(20, 5))
        
        karsilama = f"Hosgeldin, {self.kullanici['isim'].upper()}!"
        tk.Label(f, text=karsilama,
                 font=BUYUK_FONT, fg=NEON_SARI, bg=ARKA_PLAN).pack()
        
        hedef = HEDEF_ISIMLERI.get(self.kullanici["hedef"], "")
        tk.Label(f, text=f"Hedef: {hedef}",
                 font=NORMAL_FONT, fg=NEON_MAVI, bg=ARKA_PLAN).pack(pady=(0, 25))
        
        # Cizgi
        tk.Frame(f, bg=NEON_MAVI, height=2, width=600).pack(pady=10)
        
        # Buton kartlari (iki sutun)
        btn_frame = tk.Frame(f, bg=ARKA_PLAN)
        btn_frame.pack(pady=20)
        
        butonlar = [
            ("VKI VE DEGERLENDIRME", self.vki_ekrani_goster, NEON_YESIL),
            ("ANTREMAN PROGRAMIM",    self.antreman_ekrani_goster, NEON_MAVI),
            ("BESLENME VE MENU",      self.beslenme_ekrani_goster, NEON_SARI),
            ("YEMEK TARIFLERI",       self.tarif_ekrani_goster, NEON_YESIL),
            ("YENI OLCUM EKLE",       self.olcum_ekrani_goster, NEON_MAVI),
            ("ISTATISTIKLERIM",       self.istatistik_ekrani_goster, NEON_SARI),
        ]
        
        for i, (yazi, komut, renk) in enumerate(butonlar):
            satir = i // 2
            sutun = i % 2
            btn = self.neon_buton(btn_frame, yazi, komut, renk, genislik=25)
            btn.grid(row=satir, column=sutun, padx=15, pady=10)
        
        # Profili sifirla butonu (kucuk, alta)
        self.neon_buton(f, "PROFILI SIFIRLA",
                        self._profil_sifirla, KIRMIZI, genislik=20).pack(pady=20)
    
    
    def _profil_sifirla(self):
        # Onay sor, sonra dosyayi sil
        onay = messagebox.askyesno("Emin misin?",
                                   "Tum verilerin silinecek. Devam edilsin mi?")
        if onay:
            if os.path.exists(DOSYA):
                os.remove(DOSYA)
            self.kullanici = None
            self.kayit_ekrani_goster()
    
    
    # ========================================================
    # EKRAN 3: VKI VE DEGERLENDIRME
    # ========================================================
    
    def vki_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        self.baslik_ekle(f, "VUCUT KITLE INDEKSI", NEON_YESIL)
        
        # Bilgiler kart icinde
        kart = tk.Frame(f, bg=KART_RENK, padx=40, pady=20)
        kart.pack(pady=10)
        
        # Kisi bilgileri
        bilgi = (f"Boyun:  {self.kullanici['boy']} cm\n"
                 f"Kilon:  {self.kullanici['kilo']} kg\n"
                 f"Yasin:  {self.kullanici['yas']}")
        tk.Label(kart, text=bilgi,
                 font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK,
                 justify="left").pack(pady=10)
        
        # VKI hesabi
        vki = vki_hesapla(self.kullanici["kilo"], self.kullanici["boy"])
        durum, oneri, renk = vki_yorumla(vki)
        
        tk.Label(kart, text=f"VKI SKORUN: {vki}",
                 font=BUYUK_FONT, fg=NEON_SARI, bg=KART_RENK).pack(pady=(20, 10))
        
        # Buyuk durum yazisi (renkli)
        tk.Label(kart, text=durum,
                 font=BASLIK_FONT, fg=renk, bg=KART_RENK).pack(pady=10)
        
        # Oneri
        tk.Label(kart, text=oneri,
                 font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK,
                 wraplength=500, justify="center").pack(pady=10)
        
        # Geri don butonu
        self.neon_buton(f, "<< GERI DON",
                        self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=20)
    
    
    # ========================================================
    # EKRAN 4: ANTREMAN PROGRAMI
    # ========================================================
    
    def antreman_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        self.baslik_ekle(f, "ANTREMAN PROGRAMIN", NEON_MAVI)
        
        hedef = self.kullanici["hedef"]
        hedef_ad = HEDEF_ISIMLERI.get(hedef, "")
        tk.Label(f, text=f"Hedef: {hedef_ad}",
                 font=ALTBAS_FONT, fg=NEON_SARI, bg=ARKA_PLAN).pack(pady=5)
        
        # Program kart icinde
        kart = tk.Frame(f, bg=KART_RENK, padx=30, pady=20)
        kart.pack(pady=10)
        
        program = ANTREMAN_PROGRAMI.get(hedef, [])
        for gun in program:
            tk.Label(kart, text=gun,
                     font=NORMAL_FONT, fg=NEON_YESIL, bg=KART_RENK,
                     anchor="w").pack(pady=4, fill="x")
        
        self.neon_buton(f, "<< GERI DON",
                        self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=20)
    
    
    # ========================================================
    # EKRAN 5: BESLENME VE MENU
    # ========================================================
    
    def beslenme_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        self.baslik_ekle(f, "BESLENME PROGRAMIN", NEON_SARI)
        
        # Gunluk kalori
        kalori = gunluk_kalori_hesapla(self.kullanici)
        tk.Label(f, text=f"Gunluk Kalori Hedefin: {kalori} kcal",
                 font=BUYUK_FONT, fg=NEON_YESIL, bg=ARKA_PLAN).pack(pady=10)
        
        # Menu kart icinde
        kart = tk.Frame(f, bg=KART_RENK, padx=30, pady=20)
        kart.pack(pady=10, fill="x", padx=50)
        
        menu = BESLENME_MENULERI.get(self.kullanici["hedef"], {})
        for ogun, yemek in menu.items():
            satir = tk.Frame(kart, bg=KART_RENK)
            satir.pack(pady=6, fill="x")
            
            tk.Label(satir, text=ogun + ":",
                     font=ALTBAS_FONT, fg=NEON_MAVI, bg=KART_RENK,
                     width=12, anchor="w").pack(side="left")
            
            tk.Label(satir, text=yemek,
                     font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK,
                     anchor="w", wraplength=550, justify="left").pack(side="left")
        
        # Su uyarisi
        tk.Label(f, text="Su tuketimi: gunde en az 2.5 - 3 litre!",
                 font=ALTBAS_FONT, fg=NEON_YESIL, bg=ARKA_PLAN).pack(pady=15)
        
        self.neon_buton(f, "<< GERI DON",
                        self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=10)
    
    
    # ========================================================
    # EKRAN 6: YEMEK TARIFLERI
    # ========================================================
    
    def tarif_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        self.baslik_ekle(f, "YEMEK TARIFLERI", NEON_YESIL)
        
        # Tarif listesi (butonlar)
        tk.Label(f, text="Hangi tarifi gormek istersin?",
                 font=NORMAL_FONT, fg=BEYAZ, bg=ARKA_PLAN).pack(pady=10)
        
        btn_frame = tk.Frame(f, bg=ARKA_PLAN)
        btn_frame.pack(pady=10)
        
        for i, tarif in enumerate(YEMEK_TARIFLERI):
            # Closure problemi icin lambda'ya default deger ver
            btn = self.neon_buton(
                btn_frame, tarif["ad"],
                lambda t=tarif: self._tarif_detay_goster(t),
                NEON_SARI, genislik=30
            )
            btn.pack(pady=5)
        
        self.neon_buton(f, "<< GERI DON",
                        self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=20)
    
    
    def _tarif_detay_goster(self, tarif):
        # Tarif detayini yeni bir pencerede goster
        pencere = tk.Toplevel(self.pencere)
        pencere.title(tarif["ad"])
        pencere.geometry("600x550")
        pencere.configure(bg=ARKA_PLAN)
        
        tk.Label(pencere, text=tarif["ad"].upper(),
                 font=BASLIK_FONT, fg=NEON_YESIL, bg=ARKA_PLAN).pack(pady=15)
        
        # Malzemeler
        tk.Label(pencere, text=">> MALZEMELER",
                 font=ALTBAS_FONT, fg=NEON_SARI, bg=ARKA_PLAN).pack(pady=(10, 5), anchor="w", padx=30)
        
        for m in tarif["malzeme"]:
            tk.Label(pencere, text=f"  - {m}",
                     font=NORMAL_FONT, fg=BEYAZ, bg=ARKA_PLAN,
                     anchor="w").pack(fill="x", padx=40)
        
        # Yapilis
        tk.Label(pencere, text=">> YAPILISI",
                 font=ALTBAS_FONT, fg=NEON_SARI, bg=ARKA_PLAN).pack(pady=(15, 5), anchor="w", padx=30)
        
        tk.Label(pencere, text=tarif["yapilis"],
                 font=NORMAL_FONT, fg=BEYAZ, bg=ARKA_PLAN,
                 wraplength=500, justify="left").pack(padx=40, pady=5)
        
        # Kapat butonu
        tk.Button(pencere, text="KAPAT",
                  font=BUTON_FONT, fg=ARKA_PLAN, bg=NEON_MAVI,
                  relief="flat", width=15, height=2,
                  command=pencere.destroy).pack(pady=20)
    
    
    # ========================================================
    # EKRAN 7: YENI OLCUM EKLEME
    # ========================================================
    
    def olcum_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        self.baslik_ekle(f, "YENI OLCUM EKLE", NEON_MAVI)
        
        tk.Label(f, text="Bugunku gelisimini kaydet:",
                 font=NORMAL_FONT, fg=BEYAZ, bg=ARKA_PLAN).pack(pady=5)
        
        kart = tk.Frame(f, bg=KART_RENK, padx=40, pady=30)
        kart.pack(pady=20)
        
        # Form alanlari
        self.olcum_kutulari = {}
        for etk, anh in [("Kilon (kg):", "kilo"),
                          ("Antreman (dk):", "antreman"),
                          ("Yakilan kalori:", "kalori")]:
            satir = tk.Frame(kart, bg=KART_RENK)
            satir.pack(pady=10, fill="x")
            
            tk.Label(satir, text=etk,
                     font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK,
                     width=15, anchor="w").pack(side="left")
            
            giris = tk.Entry(satir, font=NORMAL_FONT,
                             fg=NEON_YESIL, bg=ARKA_PLAN,
                             insertbackground=NEON_YESIL,
                             relief="flat", width=20)
            giris.pack(side="left", ipady=5)
            self.olcum_kutulari[anh] = giris
        
        # Kaydet butonu
        self.neon_buton(kart, "KAYDET",
                        self._olcum_kaydet, NEON_YESIL, genislik=25).pack(pady=20)
        
        self.neon_buton(f, "<< GERI DON",
                        self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=10)
    
    
    def _olcum_kaydet(self):
        try:
            yeni_kilo = float(self.olcum_kutulari["kilo"].get())
            antreman_dk = int(self.olcum_kutulari["antreman"].get())
            yakilan = int(self.olcum_kutulari["kalori"].get())
        except ValueError:
            messagebox.showerror("Hata", "Lutfen sayi gir!")
            return
        
        olcum = {
            "tarih": datetime.now().strftime("%Y-%m-%d"),
            "kilo": yeni_kilo,
            "antreman_dk": antreman_dk,
            "yakilan_kalori": yakilan
        }
        
        self.kullanici["gecmis"].append(olcum)
        self.kullanici["kilo"] = yeni_kilo  # guncel kiloyu da yenile
        kullaniciyi_kaydet(self.kullanici)
        
        messagebox.showinfo("Basarili!", "Olcum eklendi! Devam et boyle :)")
        self.ana_menu_goster()
    
    
    # ========================================================
    # EKRAN 8: ISTATISTIKLER
    # ========================================================
    
    def istatistik_ekrani_goster(self):
        self.temizle()
        f = self.aktif_frame
        
        self.baslik_ekle(f, "ISTATISTIKLERIN", NEON_SARI)
        
        gecmis = self.kullanici["gecmis"]
        
        # Hic olcum yoksa uyari ver
        if len(gecmis) == 0:
            tk.Label(f, text="Henuz hic olcum eklemedin.\nOnce 'Yeni Olcum Ekle' bolumunden ekleme yap!",
                     font=NORMAL_FONT, fg=KIRMIZI, bg=ARKA_PLAN,
                     justify="center").pack(pady=50)
            
            self.neon_buton(f, "<< GERI DON",
                            self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=20)
            return
        
        # Toplam hesaplar
        toplam_antreman = sum(o["antreman_dk"] for o in gecmis)
        toplam_kalori = sum(o["yakilan_kalori"] for o in gecmis)
        ilk_kilo = gecmis[0]["kilo"]
        son_kilo = gecmis[-1]["kilo"]
        fark = round(son_kilo - ilk_kilo, 2)
        
        # Ozet kart
        kart = tk.Frame(f, bg=KART_RENK, padx=30, pady=20)
        kart.pack(pady=10, padx=50, fill="x")
        
        # Bilgileri tek tek yazdir
        bilgiler = [
            ("Toplam olcum sayisi:", str(len(gecmis)), NEON_YESIL),
            ("Toplam antreman:", f"{toplam_antreman} dakika", NEON_MAVI),
            ("Toplam yakilan kalori:", f"{toplam_kalori} kcal", NEON_SARI),
            ("Ilk kilo:", f"{ilk_kilo} kg", BEYAZ),
            ("Son kilo:", f"{son_kilo} kg", BEYAZ),
        ]
        
        for etk, deger, renk in bilgiler:
            satir = tk.Frame(kart, bg=KART_RENK)
            satir.pack(pady=4, fill="x")
            
            tk.Label(satir, text=etk,
                     font=NORMAL_FONT, fg=BEYAZ, bg=KART_RENK,
                     width=22, anchor="w").pack(side="left")
            tk.Label(satir, text=deger,
                     font=ALTBAS_FONT, fg=renk, bg=KART_RENK).pack(side="left")
        
        # Kilo degisimi (ozel mesaj)
        if fark < 0:
            mesaj = f"Kilo degisimi: {fark} kg  (VERDIN!)"
            renk = NEON_YESIL
        elif fark > 0:
            mesaj = f"Kilo degisimi: +{fark} kg  (Aldin)"
            renk = NEON_SARI
        else:
            mesaj = "Kilo degisimi: sabit"
            renk = NEON_MAVI
        
        tk.Label(kart, text=mesaj,
                 font=BUYUK_FONT, fg=renk, bg=KART_RENK).pack(pady=10)
        
        # Son 5 olcumu listele
        tk.Label(f, text="Son Olcumler:",
                 font=ALTBAS_FONT, fg=NEON_SARI, bg=ARKA_PLAN).pack(pady=(15, 5))
        
        liste_kart = tk.Frame(f, bg=KART_RENK, padx=20, pady=10)
        liste_kart.pack(pady=5, padx=50, fill="x")
        
        for o in gecmis[-5:]:
            yazi = (f"{o['tarih']}   ->   {o['kilo']} kg | "
                    f"{o['antreman_dk']} dk | {o['yakilan_kalori']} kcal")
            tk.Label(liste_kart, text=yazi,
                     font=NORMAL_FONT, fg=NEON_YESIL, bg=KART_RENK,
                     anchor="w").pack(fill="x", pady=2)
        
        self.neon_buton(f, "<< GERI DON",
                        self.ana_menu_goster, NEON_MAVI, genislik=20).pack(pady=15)


# ============================================================
# PROGRAMIN BASLANGIC NOKTASI
# ============================================================

def main():
    # Tkinter penceresini olustur ve uygulamayi baslat
    pencere = tk.Tk()
    app = ForgeFitnessApp(pencere)
    pencere.mainloop()


if __name__ == "__main__":
    main()
