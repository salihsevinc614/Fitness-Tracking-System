"""
╔══════════════════════════════════════════════════════╗
║         FORGE — Sporcu Antrenman Takip Sistemi       ║
║  Sınıflar: Sporcu, Antrenman, Takip                  ║
║  Ben bu uygulamayı OOP prensiplerine göre yazdım.    ║
╚══════════════════════════════════════════════════════╝
"""

import sys
import uuid
import math
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QSpinBox, QDoubleSpinBox, QFrame,
    QHeaderView, QTextEdit, QComboBox, QProgressBar,
    QGraphicsDropShadowEffect, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QRect, QPointF
from PyQt5.QtGui import (QFont, QColor, QPainter, QLinearGradient, QBrush,
                          QPen, QRadialGradient, QConicalGradient, QPainterPath,
                          QPolygonF, QPixmap)


# ══════════════════════════════════════════════
#  VERİ SINIFLARI
# ══════════════════════════════════════════════

class Antrenman:
    """
    Yapılan bir antrenmanı temsil ediyorum.
    Türe ve kiloya göre kalori hesaplıyorum.
    """
    # Her antrenman türü için dakikada yakılan kalori (70 kg referans)
    TUR_KATSAYI: dict = {
        "🏃  Koşu":           9.5,
        "🚴  Bisiklet":       7.5,
        "🏊  Yüzme":          8.2,
        "🏋️  Ağırlık":        6.2,
        "⚡  HIIT":           12.5,
        "🥊  Boks / Dövüş":  10.0,
        "🧘  Yoga":            3.5,
        "🤸  Pilates":         4.2,
        "🚶  Yürüyüş":        4.8,
        "⚽  Takım Sporu":    7.0,
        "🎯  Diğer":           5.0,
    }

    def __init__(self, tur: str, sure: int):
        self.antrenman_id = str(uuid.uuid4())[:6].upper()
        self.tur  = tur
        self.sure = sure   # dakika

    def kalori_hesapla(self, kilo: float) -> float:
        """Kişinin kilosuna göre tahmini kalori yakar."""
        katsayi = self.TUR_KATSAYI.get(self.tur, 5.0)
        return round(katsayi * (kilo / 70.0) * self.sure, 1)


class Takip:
    """
    Bir günün antrenman kaydını tutuyorum.
    Tarih, kalori ve notları birleştiriyorum.
    """
    def __init__(self, antrenman: Antrenman, kalori: float, notlar: str = ""):
        self.tarih     = datetime.now().strftime("%d.%m.%Y")
        self.antrenman = antrenman
        self.kalori    = kalori
        self.notlar    = notlar

    def kisa_ozet(self) -> str:
        return f"{self.tarih}  {self.antrenman.tur.split('  ')[-1]}  {self.antrenman.sure}dk  🔥{self.kalori}kcal"


class Sporcu:
    """
    Sporcu profilini ve tüm antrenman geçmişini yönetiyorum.
    İlerleme kaydetme ve istatistik hesaplama burada.
    """
    def __init__(self, ad: str, kilo: float, boy: float,
                 hedef_kalori: int = 500, hedef_gun: int = 5):
        self.sporcu_id     = str(uuid.uuid4())[:8].upper()
        self.ad            = ad
        self.kilo          = kilo
        self.boy           = boy
        self.hedef_kalori  = hedef_kalori   # Günlük kalori hedefi
        self.hedef_gun     = hedef_gun      # Haftada kaç gün antrenman hedefi
        self.takip_gecmisi: list = []        # Tüm antrenman kayıtlarım
        self.kilo_log: list = []             # Kilo değişim geçmişim
        # Özet istatistiklerimi sözlükte tutuyorum
        self.istatistik: dict = {
            "toplam_seans": 0,
            "toplam_sure_dk": 0,
            "toplam_kalori": 0.0,
            "max_sure": 0,
            "favori_tur": "—",
        }

    # ── Hesaplamalar ──────────────────────────────

    def bmi(self) -> float:
        if self.boy <= 0: return 0.0
        return round(self.kilo / ((self.boy / 100) ** 2), 1)

    def bmi_etiket(self) -> tuple:
        """BMI değerini kategori ve renk olarak döndürüyorum."""
        b = self.bmi()
        if b < 18.5: return ("Zayıf",        "#00BFFF")
        if b < 25.0: return ("Normal ✓",     "#00FF9F")
        if b < 30.0: return ("Fazla Kilolu",  "#FFD700")
        return ("Obez",                        "#FF4444")

    def haftalik_kalori(self) -> float:
        """Son 7 günün toplam kalorisini hesaplıyorum."""
        bugun = datetime.now()
        return sum(
            t.kalori for t in self.takip_gecmisi
            if (bugun - datetime.strptime(t.tarih, "%d.%m.%Y")).days <= 7
        )

    def bu_hafta_seans(self) -> int:
        """Bu haftaki antrenman sayısını sayıyorum."""
        bugun = datetime.now()
        return sum(
            1 for t in self.takip_gecmisi
            if (bugun - datetime.strptime(t.tarih, "%d.%m.%Y")).days <= 7
        )

    # ── Ana metot ────────────────────────────────

    def ilerleme_kaydet(self, antrenman: Antrenman,
                        kalori: float = None, notlar: str = "") -> Takip:
        """
        Yeni antrenman ekleyip istatistikleri güncelliyorum.
        Kalori verilmezse otomatik hesaplıyorum.
        """
        if kalori is None:
            kalori = antrenman.kalori_hesapla(self.kilo)
        kayit = Takip(antrenman, kalori, notlar)
        self.takip_gecmisi.append(kayit)

        # İstatistikleri güncelliyorum
        ist = self.istatistik
        ist["toplam_seans"]   += 1
        ist["toplam_sure_dk"] += antrenman.sure
        ist["toplam_kalori"]  += kalori
        if antrenman.sure > ist["max_sure"]:
            ist["max_sure"] = antrenman.sure

        # En çok hangi türü yapıyorum bul
        sayim: dict = {}
        for t in self.takip_gecmisi:
            sayim[t.antrenman.tur] = sayim.get(t.antrenman.tur, 0) + 1
        ist["favori_tur"] = max(sayim, key=sayim.get).split("  ")[-1]
        return kayit

    def kilo_guncelle(self, yeni: float):
        """Kiloyu güncelleyip geçmişe kaydediyorum."""
        self.kilo_log.append((datetime.now().strftime("%d.%m.%Y"), self.kilo))
        self.kilo = yeni


# ══════════════════════════════════════════════
#  ÖZEL ÇİZİM WİDGET'LARI
# ══════════════════════════════════════════════

class AtesArkaplan(QWidget):
    """
    Yanıp sönen ateş rengi animasyonlu arka plan çiziyorum.
    Her 50ms'de bir güncelleniyor.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.faz = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._adim)
        self.timer.start(50)

    def _adim(self):
        self.faz += 0.015
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Koyu zemin
        p.fillRect(self.rect(), QColor("#08090A"))

        # Alev rengi radyal ışıklar
        katmanlar = [
            (0.15, 0.90, 350, QColor(255, 80,  0,  20), 0.0),
            (0.85, 0.85, 300, QColor(255, 140, 0,  16), 1.2),
            (0.50, 0.50, 400, QColor(200, 50,  0,  12), 2.4),
            (0.20, 0.20, 260, QColor(255, 200, 0,  14), 3.6),
            (0.80, 0.30, 280, QColor(150, 30,  0,  18), 0.8),
        ]
        for bx, by, r, renk, ofset in katmanlar:
            slt = math.sin(self.faz + ofset) * 0.05
            cx = int((bx + slt) * w)
            cy = int((by + math.cos(self.faz + ofset) * 0.04) * h)
            rr = int(r * (1 + math.sin(self.faz * 0.6 + ofset) * 0.1))
            grad = QRadialGradient(cx, cy, rr)
            grad.setColorAt(0, renk)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - rr, cy - rr, rr * 2, rr * 2)

        # Çapraz çizgiler — endüstriyel his
        p.setPen(QPen(QColor(255, 100, 0, 7), 1))
        aralik = 80
        for i in range(-h, w + h, aralik):
            p.drawLine(i, 0, i + h, h)

        # Üst gradient overlay
        ov = QLinearGradient(0, 0, 0, 100)
        ov.setColorAt(0, QColor(8, 9, 10, 210))
        ov.setColorAt(1, QColor(8, 9, 10, 0))
        p.setBrush(QBrush(ov))
        p.setPen(Qt.NoPen)
        p.drawRect(0, 0, w, 100)


class HalkaGostergesi(QWidget):
    """
    Dairesel progress göstergesi çiziyorum.
    Hedef yüzdesini görsel olarak ifade ediyorum.
    """
    def __init__(self, yuzde=0, baslik="", renk="#FF6B00", parent=None):
        super().__init__(parent)
        self.yuzde = yuzde
        self.baslik = baslik
        self.renk = renk
        self.setFixedSize(110, 110)
        self._hedef = yuzde
        self._mevcut = 0.0
        # Animasyonlu dolum
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)

    def _animate(self):
        if abs(self._mevcut - self._hedef) < 1:
            self._mevcut = self._hedef
            self._timer.stop()
        else:
            self._mevcut += (self._hedef - self._mevcut) * 0.08
        self.update()

    def set_yuzde(self, yuzde):
        self._hedef = min(yuzde, 100)
        self._timer.start(16)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        cx, cy = self.width() // 2, self.height() // 2
        r = 42

        # Arka halka
        p.setPen(QPen(QColor(255, 255, 255, 18), 8, Qt.SolidLine, Qt.RoundCap))
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Dolum yayı
        if self._mevcut > 0:
            aci = int(-self._mevcut / 100 * 360 * 16)
            grad_renk = QColor(self.renk)
            p.setPen(QPen(grad_renk, 8, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(cx - r, cy - r, r * 2, r * 2, 90 * 16, aci)

        # Yüzde metni
        p.setPen(QColor(self.renk))
        p.setFont(QFont("Segoe UI", 12, QFont.Black))
        p.drawText(self.rect(), Qt.AlignCenter,
                   f"%{int(self._mevcut)}")


class MetrikKart(QFrame):
    """Parlayan kenarlıklı metrik kart."""
    def __init__(self, ikon, baslik, deger, birim="", renk="#FF6B00", parent=None):
        super().__init__(parent)
        self.renk = renk
        self.setMinimumHeight(95)
        self.setAttribute(Qt.WA_TranslucentBackground)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(2)

        ikon_lbl = QLabel(ikon)
        ikon_lbl.setStyleSheet("font-size:20px; background:transparent; border:none;")
        self.val_lbl  = QLabel(f"{deger}")
        self.val_lbl.setStyleSheet(
            f"font-size:24px; font-weight:900; color:{renk}; "
            f"background:transparent; border:none; letter-spacing:1px;"
        )
        self.birim_lbl = QLabel(f"{birim.upper()}")
        self.birim_lbl.setStyleSheet(
            f"font-size:10px; color:rgba(255,200,100,0.5); "
            f"background:transparent; border:none; letter-spacing:2px;"
        )
        bas_lbl = QLabel(baslik.upper())
        bas_lbl.setStyleSheet(
            "font-size:9px; color:rgba(255,255,255,0.35); "
            "background:transparent; border:none; letter-spacing:2px;"
        )
        lay.addWidget(ikon_lbl)
        lay.addWidget(self.val_lbl)
        lay.addWidget(self.birim_lbl)
        lay.addWidget(bas_lbl)

        # Parlama efekti
        glow = QGraphicsDropShadowEffect(self)
        glow.setColor(QColor(renk))
        glow.setBlurRadius(22)
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
        self.birim = birim

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor(255, 255, 255, 9)))
        p.setPen(QPen(QColor(self.renk), 1.5))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

    def guncelle(self, deger, birim=None):
        self.val_lbl.setText(str(deger))
        if birim:
            self.birim_lbl.setText(birim.upper())


# ══════════════════════════════════════════════
#  RENK & STİL SİSTEMİ
# ══════════════════════════════════════════════

C_BG     = "#08090A"
C_PANEL  = "rgba(14,12,8,0.92)"
C_ORANGE = "#FF6B00"
C_GOLD   = "#FFB800"
C_RED    = "#FF2D20"
C_GREEN  = "#00FF9F"
C_BLUE   = "#00C8FF"
C_TEXT   = "#F5EDE0"
C_DIM    = "rgba(245,237,224,0.45)"
C_BORDER = "rgba(255,107,0,0.28)"

STIL = f"""
* {{
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    color: {C_TEXT};
}}
QWidget {{ background: transparent; }}
QMainWindow {{ background: {C_BG}; }}

QTabWidget::pane {{
    border: 1px solid rgba(255,107,0,0.35);
    background: rgba(10,8,5,0.9);
    border-radius: 14px;
}}
QTabBar::tab {{
    background: rgba(255,255,255,0.05);
    color: rgba(245,237,224,0.45);
    padding: 11px 26px;
    border-radius: 10px 10px 0 0;
    margin-right: 4px;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
QTabBar::tab:selected {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C_RED}, stop:1 {C_ORANGE});
    color: white;
}}
QTabBar::tab:hover:!selected {{
    background: rgba(255,107,0,0.18);
    color: {C_ORANGE};
}}

QLineEdit, QSpinBox, QDoubleSpinBox {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,107,0,0.3);
    border-radius: 9px;
    padding: 9px 14px;
    color: {C_TEXT};
    font-size: 13px;
    selection-background-color: {C_ORANGE};
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {C_ORANGE};
    background: rgba(255,107,0,0.08);
}}

QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C_RED}, stop:1 {C_ORANGE});
    color: white;
    border: none;
    border-radius: 10px;
    padding: 11px 24px;
    font-weight: 900;
    font-size: 13px;
    letter-spacing: 1.5px;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #FF5050, stop:1 #FF8C30);
}}
QPushButton:pressed {{ padding: 13px 22px 9px 26px; }}

QPushButton#btnGreen {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #00CC7A, stop:1 {C_GREEN});
    color: #001A0D;
    font-weight: 900;
}}
QPushButton#btnGreen:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #00EE8A, stop:1 #44FFBB);
}}

QComboBox {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,107,0,0.3);
    border-radius: 9px;
    padding: 9px 14px;
    color: {C_TEXT};
    font-size: 13px;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: #120800;
    border: 1px solid rgba(255,107,0,0.4);
    color: {C_TEXT};
    selection-background-color: {C_ORANGE};
}}

QTableWidget {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,107,0,0.2);
    border-radius: 12px;
    gridline-color: rgba(255,255,255,0.05);
    font-size: 12px;
}}
QTableWidget::item {{ padding: 8px 12px; border: none; }}
QTableWidget::item:selected {{
    background: rgba(255,107,0,0.3);
    color: white;
}}
QHeaderView::section {{
    background: rgba(255,107,0,0.12);
    color: {C_ORANGE};
    padding: 9px 12px;
    border: none;
    border-bottom: 2px solid {C_ORANGE};
    font-weight: 800;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}

QProgressBar {{
    background: rgba(255,255,255,0.08);
    border: none;
    border-radius: 6px;
    height: 12px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C_RED}, stop:0.5 {C_ORANGE}, stop:1 {C_GOLD});
    border-radius: 6px;
}}

QTextEdit {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,107,0,0.25);
    border-radius: 12px;
    padding: 14px;
    color: {C_TEXT};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}
QScrollBar:vertical {{
    background: rgba(255,255,255,0.03);
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,107,0,0.5);
    border-radius: 3px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""


def fl(metin) -> QLabel:
    """Form etiketi oluşturuyorum."""
    lbl = QLabel(metin.upper())
    lbl.setStyleSheet(
        f"color:{C_DIM}; font-size:9px; font-weight:800; "
        f"letter-spacing:2.5px; background:transparent; border:none;"
    )
    return lbl


def panel() -> QFrame:
    f = QFrame()
    f.setStyleSheet(
        "QFrame { background: rgba(14,10,5,0.90); "
        "border: 1px solid rgba(255,107,0,0.22); border-radius: 14px; }"
    )
    return f


# ══════════════════════════════════════════════
#  GİRİŞ EKRANI
# ══════════════════════════════════════════════

class GirisEkrani(QMainWindow):
    """
    Kullanıcı profili oluşturduğu ilk ekran.
    Burada sporcu bilgilerini alıyorum.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FORGE  ·  Sporcu Takip")
        self.resize(520, 640)
        self.setStyleSheet(STIL)
        self._kur()

    def _kur(self):
        self.arkaplan = AtesArkaplan(self)
        self.arkaplan.setGeometry(0, 0, 2000, 2000)
        self.arkaplan.lower()

        merkez = QWidget(self)
        self.setCentralWidget(merkez)
        merkez.setAttribute(Qt.WA_TranslucentBackground)
        ana = QVBoxLayout(merkez)
        ana.setAlignment(Qt.AlignCenter)
        ana.setContentsMargins(50, 30, 50, 30)
        ana.setSpacing(12)

        # Logo
        logo = QLabel("FORGE")
        logo.setStyleSheet(
            f"font-size:52px; font-weight:900; color:{C_ORANGE}; "
            f"letter-spacing:12px; background:transparent; border:none;"
        )
        logo.setAlignment(Qt.AlignCenter)
        g = QGraphicsDropShadowEffect()
        g.setColor(QColor(C_ORANGE)); g.setBlurRadius(45); g.setOffset(0, 0)
        logo.setGraphicsEffect(g)

        tagline = QLabel("BUILD YOUR LEGEND")
        tagline.setStyleSheet(
            f"font-size:11px; font-weight:700; color:{C_GOLD}; "
            f"letter-spacing:5px; background:transparent; border:none;"
        )
        tagline.setAlignment(Qt.AlignCenter)

        alt = QLabel("Antrenmanlarını takip et. Sınırlarını zorla. Efsane ol.")
        alt.setStyleSheet(
            f"font-size:12px; color:{C_DIM}; background:transparent; border:none;"
        )
        alt.setAlignment(Qt.AlignCenter)
        alt.setWordWrap(True)

        ana.addWidget(logo)
        ana.addWidget(tagline)
        ana.addSpacing(4)
        ana.addWidget(alt)
        ana.addSpacing(16)

        # Form paneli
        form_p = panel()
        fl_lay = QVBoxLayout(form_p)
        fl_lay.setContentsMargins(30, 26, 30, 26)
        fl_lay.setSpacing(10)

        self.g_ad   = QLineEdit(); self.g_ad.setPlaceholderText("Sporcu Adı…")
        self.g_kilo = QDoubleSpinBox()
        self.g_kilo.setRange(30, 300); self.g_kilo.setValue(75); self.g_kilo.setSuffix(" kg")
        self.g_boy  = QDoubleSpinBox()
        self.g_boy.setRange(100, 250); self.g_boy.setValue(178); self.g_boy.setSuffix(" cm")
        self.g_hkal = QSpinBox()
        self.g_hkal.setRange(100, 5000); self.g_hkal.setValue(600); self.g_hkal.setSuffix(" kcal")
        self.g_hgun = QSpinBox()
        self.g_hgun.setRange(1, 7); self.g_hgun.setValue(4); self.g_hgun.setSuffix(" gün/hafta")

        for lbl_t, widget in [
            ("Sporcu Adı",               self.g_ad),
            ("Mevcut Kilo",              self.g_kilo),
            ("Boy",                      self.g_boy),
            ("Günlük Kalori Hedefi",     self.g_hkal),
            ("Haftalık Antrenman Hedefi",self.g_hgun),
        ]:
            fl_lay.addWidget(fl(lbl_t))
            fl_lay.addWidget(widget)

        fl_lay.addSpacing(10)
        btn = QPushButton("🔥  FORGE BAŞLAT")
        btn.setMinimumHeight(46)
        btn.clicked.connect(self._baslat)
        fl_lay.addWidget(btn)

        btn_demo = QPushButton("⚡  DEMO PROFIL")
        btn_demo.setObjectName("btnGreen")
        btn_demo.clicked.connect(self._demo)
        fl_lay.addWidget(btn_demo)

        ana.addWidget(form_p)

    def _baslat(self):
        ad = self.g_ad.text().strip()
        if not ad:
            QMessageBox.warning(self, "Uyarı", "İsim boş olamaz!"); return
        sporcu = Sporcu(ad, self.g_kilo.value(), self.g_boy.value(),
                        self.g_hkal.value(), self.g_hgun.value())
        self._ana_ac(sporcu)

    def _demo(self):
        s = Sporcu("Kaan Yıldırım", 82, 182, 700, 5)
        # Gerçekçi demo antrenmanlar ekliyorum
        demo_data = [
            ("🏋️  Ağırlık", 65), ("🏃  Koşu", 35), ("⚡  HIIT", 25),
            ("🚴  Bisiklet", 50), ("🥊  Boks / Dövüş", 45), ("🏋️  Ağırlık", 70),
            ("🏃  Koşu", 40), ("🧘  Yoga", 30),
        ]
        for tur, sure in demo_data:
            s.ilerleme_kaydet(Antrenman(tur, sure))
        self._ana_ac(s)

    def _ana_ac(self, sporcu: Sporcu):
        self.ana_pencere = AnaEkran(sporcu)
        self.ana_pencere.show()
        self.close()

    def resizeEvent(self, e):
        self.arkaplan.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(e)


# ══════════════════════════════════════════════
#  ANA EKRAN
# ══════════════════════════════════════════════

class AnaEkran(QMainWindow):
    """Sporcu profiline özel ana dashboard ekranı."""
    def __init__(self, sporcu: Sporcu):
        super().__init__()
        self.sporcu = sporcu
        self.setWindowTitle(f"FORGE  ·  {sporcu.ad.upper()}")
        self.resize(1120, 740)
        self.setStyleSheet(STIL)
        self._kur()
        self._metrikleri_guncelle()

    def _kur(self):
        self.arkaplan = AtesArkaplan(self)
        self.arkaplan.setGeometry(0, 0, 2000, 2000)
        self.arkaplan.lower()

        merkez = QWidget(self)
        self.setCentralWidget(merkez)
        merkez.setAttribute(Qt.WA_TranslucentBackground)
        ana = QVBoxLayout(merkez)
        ana.setContentsMargins(22, 16, 22, 16)
        ana.setSpacing(14)

        # ── Üst başlık ──
        ust = QHBoxLayout()
        logo = QLabel("FORGE")
        logo.setStyleSheet(
            f"font-size:30px; font-weight:900; color:{C_ORANGE}; "
            f"letter-spacing:6px; background:transparent; border:none;"
        )
        g = QGraphicsDropShadowEffect()
        g.setColor(QColor(C_ORANGE)); g.setBlurRadius(28); g.setOffset(0, 0)
        logo.setGraphicsEffect(g)

        self.sporcu_lbl = QLabel(f"  /  {self.sporcu.ad.upper()}")
        self.sporcu_lbl.setStyleSheet(
            f"font-size:20px; font-weight:300; color:{C_GOLD}; "
            f"background:transparent; border:none; letter-spacing:2px;"
        )
        bmi_etk, bmi_renk = self.sporcu.bmi_etiket()
        self.bmi_lbl = QLabel(f"BMI {self.sporcu.bmi()}  ·  {bmi_etk}")
        self.bmi_lbl.setStyleSheet(
            f"font-size:11px; color:{bmi_renk}; background:transparent; border:none; letter-spacing:1px;"
        )
        ust.addWidget(logo)
        ust.addWidget(self.sporcu_lbl)
        ust.addStretch()
        ust.addWidget(self.bmi_lbl)

        # Geri butonu
        btn_geri = QPushButton("◀  Çıkış")
        btn_geri.setObjectName("btnGreen")
        btn_geri.setMaximumWidth(110)
        btn_geri.clicked.connect(self._cikis)
        ust.addSpacing(8)
        ust.addWidget(btn_geri)
        ana.addLayout(ust)

        # ── Metrik kartlar + Halka gösterge ──
        metrik_lay = QHBoxLayout()
        metrik_lay.setSpacing(10)
        self.m_seans = MetrikKart("🔥", "Toplam Seans",  0, "seans",   C_ORANGE)
        self.m_sure  = MetrikKart("⏱️", "Toplam Süre",   0, "dakika",  C_GOLD)
        self.m_kalori= MetrikKart("⚡", "Toplam Kalori", 0, "kcal",    C_RED)
        self.m_kilo  = MetrikKart("⚖️", "Güncel Kilo",   self.sporcu.kilo, "kg", C_BLUE)
        for m in [self.m_seans, self.m_sure, self.m_kalori, self.m_kilo]:
            metrik_lay.addWidget(m)

        # Haftalık halka göstergeleri
        self.halka_kalori = HalkaGostergesi(0, "kalori", C_ORANGE)
        self.halka_gun    = HalkaGostergesi(0, "gün",    C_GOLD)
        halka_lay = QVBoxLayout()
        halka_lay.setSpacing(6)
        hal_lbl = QLabel("HAFTALIK HEDEF")
        hal_lbl.setStyleSheet(
            f"font-size:9px; font-weight:800; color:{C_DIM}; "
            f"letter-spacing:2px; background:transparent; border:none;"
        )
        h_sub = QHBoxLayout()
        h_sub.addWidget(self.halka_kalori)
        h_sub.addWidget(self.halka_gun)
        hal_blok = panel()
        hal_blok.setMaximumWidth(250)
        hal_ic = QVBoxLayout(hal_blok)
        hal_ic.setContentsMargins(12, 10, 12, 10)
        hal_ic.addWidget(hal_lbl)
        hal_ic.addLayout(h_sub)
        metrik_lay.addWidget(hal_blok)
        ana.addLayout(metrik_lay)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.tabs.addTab(self._antrenman_tab(), "🏋️  ANTRENMAN")
        self.tabs.addTab(self._gecmis_tab(),    "📋  GEÇMİŞ")
        self.tabs.addTab(self._profil_tab(),    "⚡  PROFİL")
        ana.addWidget(self.tabs)

    # ── ANTRENMAN SEKMESI ─────────────────────────

    def _antrenman_tab(self) -> QWidget:
        w = QWidget()
        w.setAttribute(Qt.WA_TranslucentBackground)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(14)

        # Form
        form_p = panel()
        form_p.setMaximumWidth(300)
        fl_lay = QVBoxLayout(form_p)
        fl_lay.setContentsMargins(20, 20, 20, 20)
        fl_lay.setSpacing(10)

        baslik = QLabel("YENİ ANTRENMAN")
        baslik.setStyleSheet(
            f"font-size:14px; font-weight:900; color:{C_ORANGE}; "
            f"letter-spacing:3px; background:transparent; border:none;"
        )
        fl_lay.addWidget(baslik)
        fl_lay.addSpacing(4)

        self.a_tur   = QComboBox()
        self.a_tur.addItems(list(Antrenman.TUR_KATSAYI.keys()))
        self.a_tur.currentIndexChanged.connect(self._oto_kalori)

        self.a_sure  = QSpinBox()
        self.a_sure.setRange(1, 300); self.a_sure.setValue(45); self.a_sure.setSuffix(" dk")
        self.a_sure.valueChanged.connect(self._oto_kalori)

        self.a_kalori = QDoubleSpinBox()
        self.a_kalori.setRange(0, 9999); self.a_kalori.setSuffix(" kcal"); self.a_kalori.setDecimals(1)

        self.a_not = QLineEdit(); self.a_not.setPlaceholderText("Antrenman notu…")

        for lbl_t, widget in [
            ("Antrenman Türü", self.a_tur),
            ("Süre",           self.a_sure),
            ("Yakılan Kalori", self.a_kalori),
            ("Not",            self.a_not),
        ]:
            fl_lay.addWidget(fl(lbl_t))
            fl_lay.addWidget(widget)

        fl_lay.addStretch()
        btn = QPushButton("🔥  KAYDET")
        btn.clicked.connect(self._antrenman_kaydet)
        fl_lay.addWidget(btn)
        lay.addWidget(form_p)
        self._oto_kalori()

        # Sağ: Son 5 antrenman + haftalık bar
        sag_p = panel()
        sl = QVBoxLayout(sag_p)
        sl.setContentsMargins(16, 16, 16, 16)
        sl.setSpacing(12)

        # Haftalık kalori bar
        bar_blok = QVBoxLayout()
        hft_lbl = QLabel("HAFTALIK KALORİ HEDEFİ")
        hft_lbl.setStyleSheet(
            f"font-size:9px; font-weight:800; color:{C_DIM}; "
            f"letter-spacing:2px; background:transparent; border:none;"
        )
        self.hft_deger_lbl = QLabel("0 / 0 kcal")
        self.hft_deger_lbl.setStyleSheet(
            f"font-size:13px; font-weight:700; color:{C_GOLD}; "
            f"background:transparent; border:none;"
        )
        self.hft_bar = QProgressBar()
        self.hft_bar.setRange(0, 100)
        self.hft_bar.setValue(0)
        self.hft_bar.setTextVisible(False)
        self.hft_bar.setFixedHeight(14)
        bar_blok.addWidget(hft_lbl)
        bar_blok.addWidget(self.hft_deger_lbl)
        bar_blok.addWidget(self.hft_bar)
        sl.addLayout(bar_blok)

        # Son antrenmanlar tablosu
        sl.addWidget(fl("Son Antrenmanlar"))
        self.son_tablo = QTableWidget(0, 4)
        self.son_tablo.setHorizontalHeaderLabels(["Tarih", "Tür", "Süre", "Kalori"])
        self.son_tablo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.son_tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.son_tablo.verticalHeader().setVisible(False)
        sl.addWidget(self.son_tablo)
        lay.addWidget(sag_p)
        return w

    def _oto_kalori(self):
        """Kalori alanını otomatik hesaplıyorum."""
        tur  = self.a_tur.currentText()
        sure = self.a_sure.value()
        a    = Antrenman(tur, sure)
        self.a_kalori.setValue(a.kalori_hesapla(self.sporcu.kilo))

    def _antrenman_kaydet(self):
        tur    = self.a_tur.currentText()
        sure   = self.a_sure.value()
        kalori = self.a_kalori.value()
        not_   = self.a_not.text()
        a      = Antrenman(tur, sure)
        self.sporcu.ilerleme_kaydet(a, kalori, not_)
        self.a_not.clear()
        self._metrikleri_guncelle()
        self._son_tabloyu_guncelle()
        self._gecmis_tablosunu_guncelle()
        QMessageBox.information(
            self, "✅  Kaydedildi!",
            f"🔥  {tur.split('  ')[-1]}  ·  {sure} dk  ·  {kalori:.0f} kcal"
        )

    # ── GEÇMİŞ SEKMESI ────────────────────────────

    def _gecmis_tab(self) -> QWidget:
        w = QWidget()
        w.setAttribute(Qt.WA_TranslucentBackground)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.addWidget(fl("Tüm Antrenman Geçmişi"))

        self.gecmis_tablo = QTableWidget(0, 5)
        self.gecmis_tablo.setHorizontalHeaderLabels(
            ["Tarih", "Tür", "Süre (dk)", "Kalori (kcal)", "Not"]
        )
        self.gecmis_tablo.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.gecmis_tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gecmis_tablo.verticalHeader().setVisible(False)
        lay.addWidget(self.gecmis_tablo)
        self._gecmis_tablosunu_guncelle()
        return w

    def _gecmis_tablosunu_guncelle(self):
        self.gecmis_tablo.setRowCount(0)
        for t in reversed(self.sporcu.takip_gecmisi):
            r = self.gecmis_tablo.rowCount()
            self.gecmis_tablo.insertRow(r)
            items = [
                (t.tarih,               C_DIM),
                (t.antrenman.tur.split("  ")[-1], C_TEXT),
                (str(t.antrenman.sure), C_GOLD),
                (f"{t.kalori:.1f}",     C_ORANGE),
                (t.notlar,              C_DIM),
            ]
            for col, (val, renk) in enumerate(items):
                it = QTableWidgetItem(val)
                it.setForeground(QColor(renk))
                self.gecmis_tablo.setItem(r, col, it)

    # ── PROFİL SEKMESI ─────────────────────────────

    def _profil_tab(self) -> QWidget:
        w = QWidget()
        w.setAttribute(Qt.WA_TranslucentBackground)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(14)

        # Kilo güncelleme
        kilo_p = panel()
        kilo_p.setMaximumWidth(280)
        kl = QVBoxLayout(kilo_p)
        kl.setContentsMargins(20, 20, 20, 20)
        kl.setSpacing(10)

        kl.addWidget(fl("⚖️  Kilo Güncelle"))
        self.p_kilo = QDoubleSpinBox()
        self.p_kilo.setRange(30, 300)
        self.p_kilo.setValue(self.sporcu.kilo)
        self.p_kilo.setSuffix(" kg")
        kl.addWidget(self.p_kilo)

        btn_kilo = QPushButton("⚖️  GÜNCELLE")
        btn_kilo.clicked.connect(self._kilo_guncelle)
        kl.addWidget(btn_kilo)
        kl.addSpacing(12)
        kl.addWidget(fl("Kilo Geçmişi"))

        self.kilo_tablo = QTableWidget(0, 2)
        self.kilo_tablo.setHorizontalHeaderLabels(["Tarih", "Kilo"])
        self.kilo_tablo.verticalHeader().setVisible(False)
        self.kilo_tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.kilo_tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        kl.addWidget(self.kilo_tablo)
        lay.addWidget(kilo_p)

        # İstatistik paneli
        ist_p = panel()
        il = QVBoxLayout(ist_p)
        il.setContentsMargins(20, 20, 20, 20)
        il.addWidget(fl("⚡  Sporcu İstatistikleri"))

        self.ist_text = QTextEdit()
        self.ist_text.setReadOnly(True)
        il.addWidget(self.ist_text)
        lay.addWidget(ist_p)

        self._istatistik_guncelle()
        return w

    def _kilo_guncelle(self):
        yeni = self.p_kilo.value()
        eski = self.sporcu.kilo
        self.sporcu.kilo_guncelle(yeni)
        self._metrikleri_guncelle()
        self._istatistik_guncelle()
        self._kilo_gecmis_guncelle()
        fark = round(yeni - eski, 1)
        ok = "▲" if fark > 0 else "▼"
        QMessageBox.information(
            self, "Güncellendi",
            f"⚖️  {eski} kg  →  {yeni} kg  ({ok} {abs(fark)} kg)"
        )

    def _kilo_gecmis_guncelle(self):
        self.kilo_tablo.setRowCount(0)
        for tarih, kilo in reversed(self.sporcu.kilo_log):
            r = self.kilo_tablo.rowCount()
            self.kilo_tablo.insertRow(r)
            self.kilo_tablo.setItem(r, 0, QTableWidgetItem(tarih))
            it = QTableWidgetItem(f"{kilo} kg")
            it.setForeground(QColor(C_GOLD))
            self.kilo_tablo.setItem(r, 1, it)

    def _istatistik_guncelle(self):
        s = self.sporcu
        ist = s.istatistik
        bmi_etk, _ = s.bmi_etiket()
        sa = ist["toplam_sure_dk"]
        rapor = (
            f"{'━'*44}\n"
            f"  ⚡  SPORCU PROFİLİ\n"
            f"{'━'*44}\n"
            f"  ID            : {s.sporcu_id}\n"
            f"  Ad            : {s.ad}\n"
            f"  Kilo          : {s.kilo} kg\n"
            f"  Boy           : {s.boy} cm\n"
            f"  BMI           : {s.bmi()} ({bmi_etk})\n"
            f"  Kalori Hedefi : {s.hedef_kalori} kcal/gün\n"
            f"  Seans Hedefi  : {s.hedef_gun} gün/hafta\n"
            f"{'━'*44}\n"
            f"  🔥  ANTRENMan İSTATİSTİKLERİ\n"
            f"{'━'*44}\n"
            f"  Toplam Seans  : {ist['toplam_seans']}\n"
            f"  Toplam Süre   : {sa} dk  ({sa//60} sa {sa%60} dk)\n"
            f"  Toplam Kalori : {ist['toplam_kalori']:.1f} kcal\n"
            f"  En Uzun Seans : {ist['max_sure']} dk\n"
            f"  Favori Tür    : {ist['favori_tur']}\n"
            f"  Haftalık Kal  : {s.haftalik_kalori():.1f} kcal\n"
            f"  Bu Hft Seans  : {s.bu_hafta_seans()} seans\n"
            f"{'━'*44}\n"
        )
        self.ist_text.setText(rapor)

    # ── GENEL GÜNCELLEME ──────────────────────────

    def _metrikleri_guncelle(self):
        ist = self.sporcu.istatistik
        self.m_seans.guncelle(ist["toplam_seans"])
        self.m_sure.guncelle(ist["toplam_sure_dk"])
        self.m_kalori.guncelle(f"{ist['toplam_kalori']:.0f}")
        self.m_kilo.guncelle(self.sporcu.kilo)

        # Haftalık bar
        hedef7  = self.sporcu.hedef_kalori * 7
        gercek  = self.sporcu.haftalik_kalori()
        yuzde   = int(min(gercek / hedef7 * 100, 100)) if hedef7 > 0 else 0
        try:
            self.hft_bar.setValue(yuzde)
            self.hft_deger_lbl.setText(f"{gercek:.0f} / {hedef7} kcal  ·  %{yuzde}")

            # Halka göstergeler
            self.halka_kalori.set_yuzde(yuzde)
            gun_yuzde = int(min(self.sporcu.bu_hafta_seans() / self.sporcu.hedef_gun * 100, 100))
            self.halka_gun.set_yuzde(gun_yuzde)
        except AttributeError:
            pass
        self._son_tabloyu_guncelle()

    def _son_tabloyu_guncelle(self):
        try:
            self.son_tablo.setRowCount(0)
            for t in reversed(self.sporcu.takip_gecmisi[-6:]):
                r = self.son_tablo.rowCount()
                self.son_tablo.insertRow(r)
                items = [
                    (t.tarih, C_DIM),
                    (t.antrenman.tur.split("  ")[-1], C_TEXT),
                    (str(t.antrenman.sure), C_GOLD),
                    (f"{t.kalori:.0f}", C_ORANGE),
                ]
                for col, (val, renk) in enumerate(items):
                    it = QTableWidgetItem(val)
                    it.setForeground(QColor(renk))
                    self.son_tablo.setItem(r, col, it)
        except AttributeError:
            pass

    def _cikis(self):
        self.giris = GirisEkrani()
        self.giris.show()
        self.close()

    def resizeEvent(self, e):
        self.arkaplan.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(e)


# ══════════════════════════════════════════════
#  BAŞLATMA
# ══════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pencere = GirisEkrani()
    pencere.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
