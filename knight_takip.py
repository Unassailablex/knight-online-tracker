import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
from datetime import datetime
import winsound
import threading
import pystray
import time
from tkinter import ttk, messagebox, simpledialog
from plyer import notification
from PIL import Image, ImageDraw
from telegram import Bot

# Masaüstü yolu ve dosyalar
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
otomatik_yedek_dosya = os.path.join(desktop, "otomatikyedek.json")
manuel_yedek_dosya = os.path.join(desktop, "yedek.json")
log_dosya = os.path.join(desktop, "log.txt")
SHORTCUTS_PATH = os.path.join(desktop, "shortcuts.json")

KAMP_LIST = ["1", "2", "3", "4", "5"]
PERI_LIST = ["Para Perisi", "Düz Peri"]
JOB_LIST = ["Warrior", "Mage", "Rogue", "Priest", "Kurian"]
POT_LIST = ["MP Pot", "HP Pot"]
secili_karakter_id = None  # Sağ tıkla seçilen karakterin Giriş ID'si tutulacak
mana_bildirim_gonderildi = {}  # Her karakter için bir flag tutacak (örn: {id: True/False})
kritik_bildirim_gonderildi = {}
bildirim_gonderilen_esyalar = set()

car_listesi = []
silinenler = []
gizlenenler = []  # <-- Gizlenen kayıtlar burada tutulacak
gizlenen_sutunlar = []  # Gizlenen sütun isimlerini tutacak liste
secili_index = None
son_siralama = {"sutun": None, "artan": True}
tepsi_icon = None
pencere_withdrawn = False
ana_pencere_acik = True
son_bildirimler = {}
THEMES = {
    "Koyu": {"bg": "#212121", "fg": "#fafafa", "row": "#333", "header": "#222", "select": "#1967d2"},
    "Açık": {"bg": "#f5f5f5", "fg": "#212121", "row": "#fff", "header": "#d2e3fa", "select": "#7fa1ef"},
    "Knight": {"bg": "#251f1c", "fg": "#ffe08e", "row": "#433427", "header": "#c0882f", "select": "#de5c12"},
    "Mavi Kontrast": {"bg": "#183265", "fg": "#fff", "row": "#3054a3", "header": "#2c4069", "select": "#7ca3ef"}
}

# Varsayılan kısayollar
default_shortcuts = {
    "kaydet": {"keysym": "Return", "ctrl": False},
    "sil": {"keysym": "Delete", "ctrl": False},
    "geri_al": {"keysym": "z", "ctrl": True},
    "yenile": {"keysym": "F5", "ctrl": False},
    "yedek_al": {"keysym": "s", "ctrl": True},
    "yedek_yukle": {"keysym": "o", "ctrl": True}
}

current_shortcuts = {}

OCR_BOT_TOKEN = "7638711968:AAGNI42aL66NtvkCVt9uezCnxKzX6w1mVSo"
OCR_CHAT_ID = "2005146572"
telegram_bot = Bot(token=OCR_BOT_TOKEN)

# -------------------------- Fonksiyonlar --------------------------
def kaydet():
    messagebox.showinfo("Bilgi", "Kayıt/Güncelleme fonksiyonu çalıştı.")

def sil():
    messagebox.showinfo("Bilgi", "Silme fonksiyonu çalıştı.")

def geri_al():
    messagebox.showinfo("Bilgi", "Geri Al fonksiyonu çalıştı.")

def telegram_test_gonder():
    messagebox.showinfo("Bilgi", "Telegram Test fonksiyonu çalıştı.")

def yedekle():
    messagebox.showinfo("Bilgi", "Yedek Alma fonksiyonu çalıştı.")

def yedek_yukle_dialog():
    messagebox.showinfo("Bilgi", "Yedek Yükle fonksiyonu çalıştı.")

def envanter_buton_tiklandi():
    messagebox.showinfo("Bilgi", "Envanter Takip fonksiyonu çalıştı.")

def open_shortcut_settings():
    messagebox.showinfo("Bilgi", "Kısayol Ayarları fonksiyonu çalıştı.")

def gizlenen_sutunlari_goster():
    messagebox.showinfo("Bilgi", "Gizlenen Sütunlar gösterildi.")

def sistem_bildirimi(baslik, mesaj):
    print(f"Bildirimi göstermek istiyor: {baslik} - {mesaj}")


def bildirim_ve_telegram(baslik, mesaj, telegram=True):
    sistem_bildirimi(baslik, mesaj)
    if telegram:
        try:
            telegram_bot.send_message(chat_id=OCR_CHAT_ID, text=f"{baslik}: {mesaj}")
        except Exception as e:
            print(f"Telegram bildirim hatası: {e}")

def tema_koyu():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#212121", foreground="#fafafa")
    style.configure("TButton", background="#444", foreground="#fafafa")
    style.configure("Treeview", background="#2b2b2b", foreground="#fafafa", fieldbackground="#212121")

def tema_acik():
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TLabel", background="white", foreground="black")
    style.configure("TButton", background="#f0f0f0", foreground="black")
    style.configure("Treeview", background="white", foreground="black", fieldbackground="white")

def tema_mavi():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#2a3f5f", foreground="#dbe9ff")
    style.configure("TButton", background="#375a9f", foreground="#dbe9ff")
    style.configure("Treeview", background="#1e2e50", foreground="#dbe9ff", fieldbackground="#2a3f5f")
    style.configure("TEntry", fieldbackground="#2a3f5f", foreground="#dbe9ff")
    pencere.configure(bg="#2a3f5f")  # Pencere arkaplanı

def tema_yesil():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#2e4d2f", foreground="#d0ffd0")
    style.configure("TButton", background="#3c6e3c", foreground="#d0ffd0")
    style.configure("Treeview", background="#254022", foreground="#d0ffd0", fieldbackground="#2e4d2f")
    style.configure("TEntry", fieldbackground="#2e4d2f", foreground="#d0ffd0")
    pencere.configure(bg="#2e4d2f")


def tema_degistir(event=None):
    secilen_tema = tema_var.get()
    if secilen_tema == "Koyu":
        tema_koyu()
    elif secilen_tema == "Açık":
        tema_acik()
    elif secilen_tema == "Mavi":
        tema_mavi()
    elif secilen_tema == "Yeşil":
        tema_yesil()


def gizlenen_sutunlari_goster():
    for col_name in gizlenen_sutunlar[:]:  # Kopyasını al, çünkü içini temizleyeceğiz
        tree.column(col_name, width=col_widths[col_name], minwidth=col_widths[col_name], stretch=True)
        tree.heading(col_name, text=col_name)
        gizlenen_sutunlar.remove(col_name)

def log_yaz(islem, kayit=None):
    with open(log_dosya, "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        satir = f"[{ts}] {islem}"
        if kayit:
            satir += f" | {kayit}"
        f.write(satir + "\n")

# Örnek envanter verileri (her karakter için)
# Örnek envanter verisi, key karakter ID'si olmalı
envanter_verileri = {
    "111": [
        {"item": "Arrow", "toplam": 100, "saatlik_tuketim": 10, "last_update": 0},
        {"item": "Genie Hammer", "toplam": 5, "saatlik_tuketim": 1, "last_update": 0},
        {"item": "Wolf", "toplam": 3, "saatlik_tuketim": 0.5, "last_update": 0},
        {"item": "HP Pot", "toplam": 20, "saatlik_tuketim": 2, "last_update": 0},
        {"item": "Swift SW", "toplam": 10, "saatlik_tuketim": 1, "last_update": 0},
        {"item": "Kitap", "toplam": 1, "saatlik_tuketim": 0, "last_update": 0},
        {"item": "Ağaç SC", "toplam": 7, "saatlik_tuketim": 0.1, "last_update": 0}
    ],
    # Diğer karakterler için ekleme yapabilirsin
}
    # Başka karakterler için de ekleyebilirsin

bildirim_gonderilen_esyalar = set()

def envanter_buton_tiklandi():
    secili = secili_karakter_var.get()
    if secili.startswith("Seçili Karakter:"):
        secili = secili.replace("Seçili Karakter:", "").strip()

    secili = secili.strip().lower()

    if secili == "" or secili == "yok":
        messagebox.showwarning("Uyarı", "Lütfen önce bir karakter seçin.")
        return

    envanter_pencere = tk.Toplevel(pencere)
    envanter_pencere.title(f"Seçili Karakter: {secili} - Envanter Takip")
    envanter_pencere.geometry("600x400")

    tree_env = ttk.Treeview(envanter_pencere, columns=("item", "kalan", "toplam", "yuzde", "saatlik_tuketim"), show="headings")
    tree_env.heading("item", text="Eşya")
    tree_env.heading("kalan", text="Kalan Adet")
    tree_env.heading("toplam", text="Toplam Adet")
    tree_env.heading("yuzde", text="Kalan %")
    tree_env.heading("saatlik_tuketim", text="Saatlik Tüketim")
    tree_env.column("item", anchor="center", width=180)
    tree_env.column("kalan", anchor="center", width=80)
    tree_env.column("toplam", anchor="center", width=80)
    tree_env.column("yuzde", anchor="center", width=80)
    tree_env.column("saatlik_tuketim", anchor="center", width=100)
    tree_env.pack(fill="both", expand=True)

    btn_frame = tk.Frame(envanter_pencere)
    btn_frame.pack(fill="x", pady=5)

    secili_id = None
    for car in car_listesi:
        isim = car.get("Karakter İsmi", "").strip().lower()
        if isim == secili:
            secili_id = str(car.get("Giriş ID", ""))
            break

    if not secili_id:
        messagebox.showerror("Hata", "Seçilen karakter bulunamadı.")
        return

    veriler = envanter_verileri.get(secili_id, [])
    now_ts = time.time()

    for esya in veriler:
        if "last_update" not in esya or esya["last_update"] == 0:
            esya["last_update"] = now_ts
        if "kalan" not in esya:
            esya["kalan"] = esya.get("toplam", 0)
        if "saatlik_tuketim" not in esya:
            esya["saatlik_tuketim"] = 0

    for esya in veriler:
        gecen_saniye = now_ts - esya["last_update"]
        harcanan = (esya["saatlik_tuketim"] / 3600) * gecen_saniye
        kalan = max(esya.get("toplam", 0) - harcanan, 0)
        yuzde = (kalan / esya.get("toplam", 1)) * 100 if esya.get("toplam", 0) > 0 else 0
        esya["kalan"] = kalan

        tree_env.insert("", "end", values=(
            esya["item"],
            int(kalan),
            int(esya.get("toplam", 0)),
            f"{yuzde:.1f}%",
            esya.get("saatlik_tuketim", 0)
        ))

    bildirim_gonderilen_esyalar = set()

    def yeni_esya_ekle():
        ad = tk.simpledialog.askstring("Yeni Eşya", "Eşya adını giriniz:")
        if not ad:
            return
        try:
            toplam = int(tk.simpledialog.askstring("Yeni Eşya", "Toplam adet giriniz:"))
            tuketim = float(tk.simpledialog.askstring("Yeni Eşya", "Saatlik tüketim giriniz:"))
        except:
            messagebox.showerror("Hata", "Geçerli sayılar giriniz.")
            return

        yeni_esya = {"item": ad, "toplam": toplam, "saatlik_tuketim": tuketim, "last_update": time.time(), "kalan": toplam}
        veriler.append(yeni_esya)
        tree_env.insert("", "end", values=(ad, toplam, toplam, "100.0%", tuketim))

        yedekle()  # Otomatik yedekle

    def sil():
        sec_item = tree_env.selection()
        if not sec_item:
            messagebox.showwarning("Uyarı", "Lütfen silinecek eşyayı seçin.")
            return
        for item in sec_item:
            index = tree_env.index(item)
            tree_env.delete(item)
            veriler.pop(index)

        yedekle()  # Otomatik yedekle

    def duzenle():
        sec_item = tree_env.selection()
        if not sec_item:
            messagebox.showwarning("Uyarı", "Lütfen düzenlenecek eşyayı seçin.")
            return
        item = sec_item[0]
        index = tree_env.index(item)
        esya = veriler[index]

        yeni_ad = tk.simpledialog.askstring("Düzenle", "Eşya adı:", initialvalue=esya["item"])
        if yeni_ad is None:
            return
        yeni_toplam = tk.simpledialog.askstring("Düzenle", "Toplam adet:", initialvalue=str(esya.get("toplam", 0)))
        yeni_tuketim = tk.simpledialog.askstring("Düzenle", "Saatlik tüketim:", initialvalue=str(esya.get("saatlik_tuketim", 0)))

        try:
            yeni_toplam = int(yeni_toplam) if yeni_toplam and yeni_toplam.strip() else 0
            yeni_tuketim = float(yeni_tuketim) if yeni_tuketim and yeni_tuketim.strip() else 0.0
        except:
            messagebox.showerror("Hata", "Geçerli sayı giriniz.")
            return

        esya["item"] = yeni_ad
        esya["toplam"] = yeni_toplam
        esya["saatlik_tuketim"] = yeni_tuketim
        esya["last_update"] = time.time()
        esya["kalan"] = yeni_toplam

        tree_env.item(item, values=(yeni_ad, yeni_toplam, yeni_toplam, "100.0%", yeni_tuketim))

        yedekle()  # Otomatik yedekle

    btn_yeni = tk.Button(btn_frame, text="Yeni Eşya Ekle", command=yeni_esya_ekle)
    btn_yeni.pack(side="left", padx=5)

    btn_duzenle = tk.Button(btn_frame, text="Düzenle", command=duzenle)
    btn_duzenle.pack(side="left", padx=5)

    btn_sil = tk.Button(btn_frame, text="Sil", command=sil)
    btn_sil.pack(side="left", padx=5)

    def guncelle():
        now = time.time()
        for i, esya in enumerate(veriler):
            gecen = now - esya["last_update"]
            harcanan = (esya.get("saatlik_tuketim", 0) / 3600) * gecen
            kalan = max(esya.get("toplam", 0) - harcanan, 0)
            yuzde = (kalan / esya.get("toplam", 1)) * 100 if esya.get("toplam", 0) > 0 else 0
            esya["kalan"] = kalan

            item_id = tree_env.get_children()[i]
            tree_env.set(item_id, "kalan", int(kalan))
            tree_env.set(item_id, "yuzde", f"{yuzde:.1f}%")

            # Telegram bildirim kontrolü:
            if yuzde <= 20 and esya["item"] not in bildirim_gonderilen_esyalar:
                try:
                    mesaj = f"{esya['item']} kalan miktar %20'nin altına düştü! Kalan: {int(kalan)} / Toplam: {int(esya.get('toplam', 0))}"
                    telegram_bot.send_message(chat_id=OCR_CHAT_ID, text=mesaj)
                    print(f"Bildirim gönderildi: {mesaj}")
                    bildirim_gonderilen_esyalar.add(esya["item"])
                except Exception as e:
                    print(f"Telegram bildirim gönderme hatası: {e}")

            if yuzde > 20 and esya["item"] in bildirim_gonderilen_esyalar:
                bildirim_gonderilen_esyalar.remove(esya["item"])

        envanter_pencere.after(1000, guncelle)

    guncelle()


def sesli_uyari():
    secilen_ses = ses_secimi.get()
    if secilen_ses == "Default Beep":
        winsound.Beep(1500, 300)
    elif secilen_ses == "Beep 2":
        winsound.Beep(1000, 500)
    elif secilen_ses == "Beep 3":
        winsound.Beep(2000, 100)

def mana_kritik_kontrol():
    global mana_bildirim_gonderildi
    simdi = datetime.now().timestamp()
    for car in car_listesi:
        try:
            karakter_ismi = car.get("Karakter İsmi", "")
            giris_id = str(car.get("Giriş ID", ""))
            toplam_mana = int(car.get("Toplam Mana", "0") or 0)
            saatlik_mana = int(car.get("Saatlik Mana Tüketimi", "0") or 0)
            last_update = car.get("mana_last_update", simdi)
            gecen_saniye = simdi - last_update

            # Her saniye toplam manadan harcananı düş
            harcanan_mana = (saatlik_mana * gecen_saniye) / 3600
            kalan_mana = max(0, toplam_mana - harcanan_mana)
            yuzde = (kalan_mana / toplam_mana) * 100 if toplam_mana > 0 else 100
            car["Mana Seviyesi"] = f"%{yuzde:.1f}"

            # Bildirim flag'i ilk kez ekle
            if giris_id not in mana_bildirim_gonderildi:
                mana_bildirim_gonderildi[giris_id] = False

            # Kritik bildirim
            if yuzde <= 20 and not mana_bildirim_gonderildi[giris_id]:
                try:
                    mesaj = f"{karakter_ismi} ({giris_id}) için mana kritik seviyede! ({int(kalan_mana)}/{toplam_mana} - %{yuzde:.1f})"
                    telegram_bot.send_message(chat_id=OCR_CHAT_ID, text=mesaj)
                except Exception as e:
                    print(f"Telegram gönderim hatası: {e}")
                mana_bildirim_gonderildi[giris_id] = True

            if yuzde > 20:
                mana_bildirim_gonderildi[giris_id] = False

        except Exception as e:
            print("Mana kritik kontrolünde hata:", e)
            continue

    guncelle_liste()
    pencere.after(1000, mana_kritik_kontrol)  # Her saniye çalış!
   

def kritik_envanter_ozeti():
    kritik_listesi = []
    now_ts = time.time()
    for car in car_listesi:
        giris_id = str(car.get("Giriş ID", ""))
        karakter_adi = car.get("Karakter İsmi", "Bilinmiyor")
        envanter = envanter_verileri.get(giris_id, [])
        for esya in envanter:
            toplam = esya.get("toplam", 0)
            saatlik_tuketim = esya.get("saatlik_tuketim", 0)
            last_update = esya.get("last_update", now_ts)
            gecen = now_ts - last_update
            harcanan = (saatlik_tuketim / 3600) * gecen
            kalan = max(toplam - harcanan, 0)
            yuzde = (kalan / toplam) * 100 if toplam > 0 else 100
            if yuzde <= 20:
                kritik_listesi.append(f"{karakter_adi} - {esya['item']}: %{yuzde:.1f} ({int(kalan)} / {toplam})")
    return kritik_listesi

from tkinter import ttk

import tkinter as tk
from tkinter import ttk

def kritik_ozet_popup():
    kritik_listesi = kritik_envanter_ozeti()  # Kendi fonksiyonun

    if not kritik_listesi:
        return

    popup = tk.Toplevel(pencere)
    popup.title("Kritik Envanterler")
    popup.geometry("600x350")
    popup.attributes("-topmost", True)

    label = tk.Label(popup, text="Kritik Envanterler (%20 ve altında):", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    frame = tk.Frame(popup)
    frame.pack(padx=10, pady=5, fill="both", expand=True)

    # Başlıklar
    baslik_frame = tk.Frame(frame)
    baslik_frame.pack(fill="x")

    tk.Label(baslik_frame, text="Karakter", font=("Arial", 10, "bold"), width=20, anchor="w").grid(row=0, column=0)
    tk.Label(baslik_frame, text="Eşya", font=("Arial", 10, "bold"), width=30, anchor="w").grid(row=0, column=1)
    tk.Label(baslik_frame, text="Durum", font=("Arial", 10, "bold"), width=30, anchor="center").grid(row=0, column=2)

    # Listbox frame
    listbox_frame = tk.Frame(frame)
    listbox_frame.pack(fill="both", expand=True)

    # Karakter Listbox
    karakter_lb = tk.Listbox(listbox_frame, font=("Arial", 10, "bold"), fg="black", width=20)
    karakter_lb.grid(row=0, column=0, sticky="nsew")

    # Eşya Listbox
    esya_lb = tk.Listbox(listbox_frame, font=("Arial", 10, "bold"), fg="black", width=30)
    esya_lb.grid(row=0, column=1, sticky="nsew")

    # Durum Listbox (kırmızı kalın)
    durum_lb = tk.Listbox(listbox_frame, font=("Arial", 10, "bold"), fg="red", width=40)
    durum_lb.grid(row=0, column=2, sticky="nsew")

    # Scrollbar - tüm listboxları kontrol eder
    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
    scrollbar.grid(row=0, column=3, sticky="ns")

    # Scrollbar ile senkronizasyon
    def on_scroll(*args):
        karakter_lb.yview(*args)
        esya_lb.yview(*args)
        durum_lb.yview(*args)

    scrollbar.config(command=on_scroll)

    # Aynı anda scroll yapma
    def sync_scroll(event):
        karakter_lb.yview_moveto(esya_lb.yview()[0])
        esya_lb.yview_moveto(karakter_lb.yview()[0])
        durum_lb.yview_moveto(karakter_lb.yview()[0])
        return "break"

    karakter_lb.bind("<MouseWheel>", sync_scroll)
    esya_lb.bind("<MouseWheel>", sync_scroll)
    durum_lb.bind("<MouseWheel>", sync_scroll)

    # Verileri ekle
    for satir in kritik_listesi:
        try:
            karakter, geri_kalan = satir.split(" - ", 1)
            esya_adi, durum = geri_kalan.split(": ", 1)
        except Exception:
            karakter, esya_adi, durum = "", satir, ""

        karakter_lb.insert(tk.END, karakter)
        esya_lb.insert(tk.END, esya_adi)
        durum_lb.insert(tk.END, durum)

    btn_kapat = ttk.Button(popup, text="Tamam", command=popup.destroy)
    btn_kapat.pack(pady=10)


def tree_secim_degisti(event):
    global secili_index
    secili_item = tree.focus()  # Seçili item id'si
    if secili_item:
        secili_index = tree.index(secili_item)
    else:
        secili_index = None

def envanter_penceresi_ac(index):
    if index is None or index >= len(car_listesi):
        messagebox.showerror("Hata", "Lütfen önce bir kayıt seçin.")
        return

    car = car_listesi[index]
    envanter = car.get("Envanter", {})

    penc = tk.Toplevel(pencere)
    penc.title(f"{car.get('Karakter İsmi', 'Bilinmeyen')} - Envanter")
    penc.geometry("300x300+200+200")
    penc.attributes("-topmost", True)
    penc.after(5000, lambda: penc.attributes("-topmost", False))

    tree_inv = ttk.Treeview(penc, columns=("Item", "Adet"), show="headings")
    tree_inv.heading("Item", text="Item")
    tree_inv.heading("Adet", text="Adet")
    tree_inv.pack(fill="both", expand=True)

    # Düzeltilmiş kısım: envanter dict değilse listeyse liste şeklinde dönüyoruz
    if isinstance(envanter, dict):
        for item, adet in envanter.items():
            tree_inv.insert("", "end", values=(item, adet))
    elif isinstance(envanter, list):
        for veri in envanter:
            tree_inv.insert("", "end", values=(veri.get("item", ""), veri.get("adet", "")))

def tree_cift_tikla(event):
    global secili_index
    item_id = tree.identify_row(event.y)
    if not item_id:
        return
    index = tree.index(item_id)
    secili_index = index

    car = car_listesi[index]
    giris_id.set(car.get("Giriş ID", ""))
    karakter_isim.set(car.get("Karakter İsmi", ""))
    kamp.set(car.get("Kamp", ""))
    mob.set(car.get("Mob", ""))
    gunluk_getiri.set(car.get("Günlük Getiri", ""))
    pot_turu.set(car.get("Pot Türü", "MP Pot"))
    mp_pot_adedi.set(car.get("MP Pot Adedi", ""))
    job.set(car.get("Job", ""))
    peri_turu.set(car.get("Peri Türü", "Para Perisi"))
    pc_bilgi.set(car.get("PC", ""))
    not_kutu.set(car.get("Not", ""))
    genie_var.set(car.get("Genie", "00:00"))
    premium_var.set(str(car.get("Premium", "")))
    toplam_mana_var.set(car.get("Toplam Mana", ""))
    saatlik_mana_var.set(car.get("Saatlik Mana Tüketimi", ""))
    mana_seviyesi_var.set(car.get("Mana Seviyesi", ""))
    pot_turu_degisti()  # Pot türü HP ise adedi kapatır


def zamanli_bildirim(kayit_adi, alan, car=None):
    global son_bildirimler
    if car is not None:
        anahtar = f"{kayit_adi}_{alan}"
        simdi = datetime.now().timestamp()
        if anahtar in son_bildirimler and simdi - son_bildirimler[anahtar] < 300:
            return
        son_bildirimler[anahtar] = simdi
    sesli_uyari()
    mesaj = f"{kayit_adi} kaydının '{alan}' alanında kritik süreye girildi!"
    sistem_bildirimi("Hatırlatma!", mesaj)
    try:
        telegram_bot.send_message(chat_id=OCR_CHAT_ID, text=mesaj)
    except Exception as e:
        print(f"Telegram bildirim gönderilemedi: {e}")

son_yedekleme_bildirim_saati = -1  # Global değişken, başlangıçta geçersiz saat

ilk_yedekleme = True

def otomatik_yedekle():
    global ilk_yedekleme, son_yedekleme_bildirim_saati
    with open(otomatik_yedek_dosya, "w", encoding="utf-8") as f:
        json.dump(car_listesi, f, ensure_ascii=False, indent=2)
    log_yaz("Otomatik yedek alındı", otomatik_yedek_dosya)

    simdi = datetime.now()
    simdi_saati = simdi.hour

    if simdi_saati != son_yedekleme_bildirim_saati:
        son_yedekleme_bildirim_saati = simdi_saati
        if not ilk_yedekleme:
            bildirim_ve_telegram("Otomatik Yedekleme", f"Otomatik yedekleme yapıldı:\n{otomatik_yedek_dosya}")
        else:
            ilk_yedekleme = False

    pencere.after(30000, otomatik_yedekle)  # 30 saniyede bir yedek al


def yedekle():
    with open(manuel_yedek_dosya, "w", encoding="utf-8") as f:
        # Aktif kayıtlar ve gizlenenler ayrı ayrı kaydedilecek!
        json.dump({"aktifler": car_listesi, "gizlenenler": gizlenenler}, f, ensure_ascii=False, indent=2)
    log_yaz("Manuel yedek alındı", manuel_yedek_dosya)
    # messagebox.showinfo("Yedek Alındı", f"Manuel yedek {manuel_yedek_dosya} dosyasına alındı.")  # Bu satırı yorum satırı yaptım

def yedek_yukle(dosya=manuel_yedek_dosya):
    global car_listesi, gizlenenler
    if not os.path.exists(dosya):
        log_yaz("Yedek dosyası bulunamadı", dosya)
        return
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            car_listesi = data
            gizlenenler = []
        else:
            car_listesi = data.get("aktifler", [])
            gizlenenler = data.get("gizlenenler", [])
        car_listesi = [x for x in car_listesi if isinstance(x, dict)]
        gizlenenler = [x for x in gizlenenler if isinstance(x, dict)]
        guncelle_liste()
        log_yaz("Yedek yüklendi", dosya)
    except Exception as e:
        log_yaz("Yedek yükleme hatası", str(e))

def yedek_yukle_otomatik():
    global car_listesi, gizlenenler
    if os.path.exists(otomatik_yedek_dosya):
        try:
            yedek_yukle(otomatik_yedek_dosya)
        except Exception as e:
            print("Otomatik yedek yükleme hatası:", e)
    else:
        pass

def guncelle_liste():
    for row in tree.get_children():
        tree.delete(row)
    global car_listesi
    car_listesi = [x for x in car_listesi if isinstance(x, dict)]
    gizlileri_goster = gizli_goster_var.get()
    now_ts = datetime.now().timestamp()

    for car in car_listesi:
        if not isinstance(car, dict):
            continue
        if car.get("gizli_mi", False) and not gizlileri_goster:
            continue

        # --- Mana Seviyesi HESAPLA ---
        try:
            toplam_mana = float(car.get("Toplam Mana", "0") or 0)
            saatlik_mana = float(car.get("Saatlik Mana Tüketimi", "0") or 0)
            mana_last_update = float(car.get("mana_last_update", now_ts))
            gecen_saniye = now_ts - mana_last_update
            harcanan_mana = (saatlik_mana / 3600) * gecen_saniye
            kalan_mana = max(toplam_mana - harcanan_mana, 0)
            if toplam_mana > 0:
                mana_yuzde = (kalan_mana / toplam_mana) * 100
            else:
                mana_yuzde = 0.0
            mana_seviye_str = f"%{mana_yuzde:.1f}"
        except Exception as e:
            mana_seviye_str = "%0.0"

        renk = job_renk(car.get("Job", ""), car.get("Genie Canli", "00:00:00"))

        tree.insert("", tk.END, values=(
            car.get("Giriş ID", ""),
            car.get("Karakter İsmi", ""),
            car.get("Kamp", ""),
            car.get("Mob", ""),
            car.get("Günlük Getiri", ""),
            car.get("Pot Türü", ""),
            car.get("MP Pot Adedi", ""),
            car.get("Job", ""),
            car.get("Peri Türü", ""),
            car.get("PC", ""),
            car.get("Not", ""),
            car.get("Genie", ""),
            car.get("Premium", ""),
            car.get("Genie Canli", ""),
            car.get("Premium Canli", ""),
            car.get("Toplam Mana", ""),
            car.get("Saatlik Mana Tüketimi", ""),
            mana_seviye_str   # <-- Dinamik güncel değer
        ), tags=(renk,))

    # --- Seçili karakteri koru ---
    if secili_karakter_id:
        for row in tree.get_children():
            item = tree.item(row)
            if str(item["values"][0]) == str(secili_karakter_id):
                tree.selection_set(row)
                tree.see(row)
                secili_karakter_guncelle(None)
                break

def job_renk(job, genie_canli):
    job = str(job).strip().lower()
    if genie_canli == "00:00:00" or genie_canli == 0 or genie_canli == "0":
        return "kirmizi"
    if "priest" in job:
        return "mor"
    elif "warrior" in job:
        return "kirmizi"
    elif "mage" in job:
        return "mavi"
    elif "archer" in job or "rogue" in job:
        return "yesil"
    elif "kurian" in job:
        return "turuncu"
    else:
        return "gri"

def saniyeden_genie_canli_yaz(saniye):
    # Saniyeyi saat:dakika:saniye formatına çevirir
    saat = saniye // 3600
    dakika = (saniye % 3600) // 60
    saniye_ = saniye % 60
    return f"{saat:02d}:{dakika:02d}:{saniye_:02d}"

def saniyeden_premium_canli_yaz(saniye):
    gun = saniye // (3600*24)
    saat = (saniye % (3600*24)) // 3600
    return f"{gun} gün {saat} saat"

def genie_saniyeye_cevir(genie_str):
    try:
        parts = genie_str.split(":")
        if len(parts) == 2:
            saat = int(parts[0])
            dakika = int(parts[1])
            toplam_saniye = saat*3600 + dakika*60
            return toplam_saniye
        elif len(parts) == 3:
            saat = int(parts[0])
            dakika = int(parts[1])
            saniye = int(parts[2])
            toplam_saniye = saat*3600 + dakika*60 + saniye
            return toplam_saniye
        else:
            return 0
    except:
        return 0


def kaydet():
    global secili_index
    now_ts = datetime.now().timestamp()

    genie_str = genie_var.get()
    if len(genie_str.split(":")) == 2:
        genie_canli_str = genie_str + ":00"
    else:
        genie_canli_str = genie_str

    # --- Mana Seviyesi otomatik hesaplama ---
    toplam_mana = int(toplam_mana_var.get() or 0)
    saatlik_mana = int(saatlik_mana_var.get() or 0)
    kalan_mana = toplam_mana  # Başlangıçta tamamı dolu (veya daha gelişmiş bir sistemde anlık takip)
    yuzde = 100
    if toplam_mana > 0:
        yuzde = (kalan_mana / toplam_mana) * 100
    mana_seviyesi_otomatik = f"%{yuzde:.1f}"
    mana_seviyesi_var.set(mana_seviyesi_otomatik)

    car = {
        "Giriş ID": giris_id.get(),
        "Karakter İsmi": karakter_isim.get(),
        "Kamp": kamp.get(),
        "Mob": mob.get(),
        "Günlük Getiri": gunluk_getiri.get(),
        "Pot Türü": pot_turu.get(),
        "MP Pot Adedi": mp_pot_adedi.get() if pot_turu.get() == "MP Pot" else "",
        "Job": job.get(),
        "Peri Türü": peri_turu.get(),
        "PC": pc_bilgi.get(),
        "Not": not_kutu.get(),
        "Genie": genie_str,
        "Genie Canli": genie_canli_str,
        "Genie_last_update": now_ts,
        "Premium": int(premium_var.get()) if premium_var.get().isdigit() else 0,
        "Premium_last_update": now_ts,
        "Toplam Mana": toplam_mana_var.get(),
        "Saatlik Mana Tüketimi": saatlik_mana_var.get(),
        "Mana Seviyesi": mana_seviyesi_otomatik,  # <-- OTO HESAPLANAN DEĞERİ BURAYA YAZ
        "mana_last_update": now_ts,
        "gizli_mi": False,
        "Envanter": {"Hammer": 20, "Potion": 10, "Gold": 5000}
    }
    # (devamı...)

    # Sonrası eski haliyle devam!

    if secili_index is not None:
        car_listesi[secili_index] = car
        log_yaz("Kayıt güncellendi", str(car))
        secili_index = None
    else:
        car_listesi.append(car)
        log_yaz("Kayıt eklendi", str(car))

    guncelle_liste()
    temizle()
    yedekle()

def temizle():
    global secili_index
    giris_id.set("")
    karakter_isim.set("")
    kamp.set("")
    mob.set("")
    gunluk_getiri.set("")
    pot_turu.set("MP Pot")
    mp_pot_adedi.set("")
    job.set("")
    peri_turu.set("Para Perisi")
    pc_bilgi.set("")
    not_kutu.set("")
    genie_var.set("00:00")
    premium_var.set("")
    toplam_mana_var.set("")
    saatlik_mana_var.set("")
    mana_seviyesi_var.set("")
    pot_adedi_entry.config(state="normal")
    secili_index = None

def sil():
    global secili_index
    secili = tree.selection()
    if not secili:
        messagebox.showinfo("Uyarı", "Lütfen silmek için bir kayıt seç.")
        return
    index = tree.index(secili[0])
    silinenler.append(car_listesi[index])
    log_yaz("Kayıt silindi", str(car_listesi[index]))
    car_listesi.pop(index)
    guncelle_liste()
    temizle()
    yedekle()

def geri_al():
    if not silinenler:
        messagebox.showinfo("Geri Al", "Geri alınacak silinen kayıt yok.")
        return
    geri_kayit = silinenler.pop()
    car_listesi.append(geri_kayit)
    log_yaz("Geri alındı", str(geri_kayit))
    guncelle_liste()
    yedekle()

def tumunu_goster():
    for car in car_listesi:
        if isinstance(car, dict):
            car["gizli_mi"] = False
    guncelle_liste()

def pot_turu_degisti(event=None):
    if pot_turu.get() == "MP Pot":
        pot_adedi_entry.config(state="normal")
    else:
        pot_adedi_entry.delete(0, tk.END)
        pot_adedi_entry.config(state="disabled")

def tree_cift_tikla(event):
    global secili_index
    item = tree.identify_row(event.y)
    if not item:
        return
    index = tree.index(item)
    secili_index = index  # Burada güncelle

    car = car_listesi[index]
    giris_id.set(car.get("Giriş ID", ""))
    karakter_isim.set(car.get("Karakter İsmi", ""))
    kamp.set(car.get("Kamp", ""))
    mob.set(car.get("Mob", ""))
    gunluk_getiri.set(car.get("Günlük Getiri", ""))
    pot_turu.set(car.get("Pot Türü", "MP Pot"))
    mp_pot_adedi.set(car.get("MP Pot Adedi", ""))
    job.set(car.get("Job", ""))
    peri_turu.set(car.get("Peri Türü", "Para Perisi"))
    pc_bilgi.set(car.get("PC", ""))
    not_kutu.set(car.get("Not", ""))
    genie_var.set(car.get("Genie Canli", "00:00:00"))  # Burada canli olarak göster
    premium_var.set(str(car.get("Premium", "")))
    toplam_mana_var.set(car.get("Toplam Mana", ""))
    saatlik_mana_var.set(car.get("Saatlik Mana Tüketimi", ""))
    mana_seviyesi_var.set(car.get("Mana Seviyesi", ""))
    pot_turu_degisti()


def arama_filtrele(*args):
    kelime = arama_var.get().strip().lower()
    # Önce tüm satırları temizle
    for row in tree.get_children():
        tree.delete(row)
    # Filtreleme yaparak listeyi güncelle
    for car in car_listesi:
        metin = " ".join([str(v).lower() for v in car.values()])
        if kelime in metin:
            renk = job_renk(car.get("Job", ""), car.get("Genie Canli", "00:00:00"))
            tree.insert("", tk.END, values=(
                car.get("Giriş ID", ""),
                car.get("Karakter İsmi", ""),
                car.get("Kamp", ""),
                car.get("Mob", ""),
                car.get("Günlük Getiri", ""),
                car.get("Pot Türü", ""),
                car.get("MP Pot Adedi", ""),
                car.get("Job", ""),
                car.get("Peri Türü", ""),
                car.get("PC", ""),
                car.get("Not", ""),
                car.get("Genie", ""),
                car.get("Premium", ""),
                car.get("Genie Canli", ""),
                car.get("Premium Canli", ""),
                car.get("Toplam Mana", ""),
                car.get("Saatlik Mana Tüketimi", ""),
                car.get("Mana Seviyesi", "")
            ), tags=(renk,))


def sirala_sutun(event):
    region = tree.identify("region", event.x, event.y)
    if region != "heading":
        return
    col = tree.identify_column(event.x)
    col_num = int(col.replace("#", "")) - 1
    basliklar = [
        "Giriş ID", "Karakter İsmi", "Kamp", "Mob", "Günlük Getiri", "Pot Türü",
        "MP Pot Adedi", "Job", "Peri Türü", "PC", "Not", "Genie", "Premium",
        "Genie Canli", "Premium Canli", "Toplam Mana", "Saatlik Mana Tüketimi", "Mana Seviyesi"
    ]
    sutun = basliklar[col_num]
    son = son_siralama
    if son["sutun"] == sutun:
        son["artan"] = not son["artan"]
    else:
        son["sutun"] = sutun
        son["artan"] = True
    car_listesi.sort(key=lambda x: str(x.get(sutun, "")).lower(), reverse=not son["artan"])
    guncelle_liste()


def yedek_al_dialog():
    dosya = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Json Dosyası", "*.json")])
    if dosya:
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(car_listesi + gizlenenler, f, ensure_ascii=False, indent=2)  # gizlenenler dahil
        log_yaz("Manuel yedek alındı", dosya)
        messagebox.showinfo("Yedek Alındı", f"Manuel yedek {dosya} dosyasına alındı.")


def yedek_yukle_dialog():
    dosya = filedialog.askopenfilename(filetypes=[("Json Dosyası", "*.json")])
    if dosya:
        yedek_yukle(dosya)


def dosya_birak(event):
    try:
        dosya_yolu = event.data
        if dosya_yolu.endswith(".json"):
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                global car_listesi, gizlenenler
                full_list = json.load(f)
                car_listesi = full_list
                gizlenenler = []
            guncelle_liste()
            messagebox.showinfo("Başarılı", f"{dosya_yolu}\ndosyası yüklendi.")
            log_yaz("Dosya sürükle bırakla yüklendi", dosya_yolu)
        else:
            messagebox.showwarning("Uyarı", "Lütfen JSON dosyası sürükleyip bırakın.")
    except Exception as e:
        messagebox.showerror("Hata", f"Sürükle bırak yükleme hatası: {e}")


def saniyeyi_saat_dakika_saniyeye_cevir(saniye):
    if saniye < 0:
        saniye = 0
    saat = saniye // 3600
    dakika = (saniye % 3600) // 60
    saniye_ = saniye % 60
    return f"{saat:02d}:{dakika:02d}:{saniye_:02d}"

def genie_saniyeye_cevir(genie_str):
    try:
        parts = genie_str.split(":")
        if len(parts) == 2:
            saat = int(parts[0])
            dakika = int(parts[1])
            toplam_saniye = saat * 3600 + dakika * 60
            return toplam_saniye
        elif len(parts) == 3:
            saat = int(parts[0])
            dakika = int(parts[1])
            saniye = int(parts[2])
            toplam_saniye = saat * 3600 + dakika * 60 + saniye
            return toplam_saniye
        else:
            return 0
    except:
        return 0

def genie_premium_checker():
    now_ts = datetime.now().timestamp()
    degisiklik_var = False
    for car in car_listesi:
        try:
            # Genie canlı kalan süresi
            toplam_saniye = genie_saniyeye_cevir(car.get("Genie", "00:00"))
            last_update = car.get("Genie_last_update", now_ts)
            gecen_saniye = int(now_ts - last_update)
            kalan_saniye = toplam_saniye - gecen_saniye

            if kalan_saniye < 0:
                kalan_saniye = 0

            yeni_canli = saniyeyi_saat_dakika_saniyeye_cevir(kalan_saniye)
            if car.get("Genie Canli", "") != yeni_canli:
                car["Genie Canli"] = yeni_canli
                degisiklik_var = True

            if kalan_saniye == 0:
                car["Genie"] = "00:00"
                car["Genie_last_update"] = now_ts

            # --- PREMIUM CANLI SÜRESİ EKLENTİSİ ---
            premium_gun = int(car.get("Premium", 0))
            premium_last_update = car.get("Premium_last_update", now_ts)
            premium_gecen_saniye = int(now_ts - premium_last_update)
            premium_toplam_saniye = premium_gun * 24 * 3600
            premium_kalan_saniye = premium_toplam_saniye - premium_gecen_saniye

            if premium_kalan_saniye < 0:
                premium_kalan_saniye = 0

            gun = premium_kalan_saniye // (24 * 3600)
            saat = (premium_kalan_saniye % (24 * 3600)) // 3600

            premium_canli_yeni = f"{gun} gün {saat} saat"
            if car.get("Premium Canli", "") != premium_canli_yeni:
                car["Premium Canli"] = premium_canli_yeni
                degisiklik_var = True

            if premium_kalan_saniye == 0:
                car["Premium"] = 0
                car["Premium_last_update"] = now_ts

        except Exception as e:
            print(f"Genie/Premium hesaplama hatası: {e}")
            continue

    if degisiklik_var:
        guncelle_liste()

    pencere.after(1000, genie_premium_checker)

def tema_degistir(event=None):
    secilen_tema = tema_var.get()  # Kullanıcının seçtiği tema değerini al

    if secilen_tema == "Koyu":
        # Koyu tema için renk ayarları
        pencere.configure(bg="#212121")
        frm_left.configure(bg="#212121")
        frm_right.configure(bg="#212121")
        tree_frame.configure(bg="#212121")

        secili_karakter_label.configure(fg="red", bg="#212121")

        # frm_left içindeki tüm label ve buttonların rengini koyulaştır
        for child in frm_left.winfo_children():
            if isinstance(child, (tk.Label, tk.Button)):
                child.configure(bg="#212121", fg="#fafafa")

        # frm_right içindeki tüm label ve buttonların rengini koyulaştır
        for child in frm_right.winfo_children():
            if isinstance(child, (tk.Label, tk.Button)):
                child.configure(bg="#212121", fg="#fafafa")

    elif secilen_tema == "Açık":
        # Açık tema için renk ayarları
        pencere.configure(bg="#f0f0f0")
        frm_left.configure(bg="#f0f0f0")
        frm_right.configure(bg="#f0f0f0")
        tree_frame.configure(bg="#f0f0f0")

        secili_karakter_label.configure(fg="black", bg="#f0f0f0")

        # frm_left içindeki tüm label ve buttonların rengini aç
        for child in frm_left.winfo_children():
            if isinstance(child, (tk.Label, tk.Button)):
                child.configure(bg="#f0f0f0", fg="black")

        # frm_right içindeki tüm label ve buttonların rengini aç
        for child in frm_right.winfo_children():
            if isinstance(child, (tk.Label, tk.Button)):
                child.configure(bg="#f0f0f0", fg="black")


# Kısayol fonksiyonları
def load_shortcuts():
    global current_shortcuts
    if os.path.exists(SHORTCUTS_PATH):
        try:
            with open(SHORTCUTS_PATH, "r", encoding="utf-8") as f:
                current_shortcuts = json.load(f)
        except Exception:
            current_shortcuts = default_shortcuts.copy()
    else:
        current_shortcuts = default_shortcuts.copy()

def save_shortcuts():
    with open(SHORTCUTS_PATH, "w", encoding="utf-8") as f:
        json.dump(current_shortcuts, f, ensure_ascii=False, indent=2)

def open_shortcut_settings():
    def kaydet_kisayollar():
        for key, entry in entries.items():
            val = entry.get().strip()
            if '+' in val:
                parts = val.split('+')
                ctrl = 'Ctrl' in parts or 'ctrl' in parts
                key_sym = [p for p in parts if p.lower() != 'ctrl'][0]
            else:
                ctrl = False
                key_sym = val
            current_shortcuts[key] = {"keysym": key_sym, "ctrl": ctrl}
        save_shortcuts()
        messagebox.showinfo("Başarılı", "Kısayollar kaydedildi.")
        ayar_pencere.destroy()

    ayar_pencere = tk.Toplevel(pencere)
    ayar_pencere.title("Klavye Kısayolları Ayarları")
    entries = {}

    satir = 0
    for key in default_shortcuts.keys():
        tk.Label(ayar_pencere, text=key.capitalize()).grid(row=satir, column=0, padx=5, pady=5, sticky="w")
        ent = tk.Entry(ayar_pencere, width=20)
        ent.grid(row=satir, column=1, padx=5, pady=5)
        val = current_shortcuts.get(key, default_shortcuts[key])
        ctrl_prefix = "Ctrl+" if val.get("ctrl") else ""
        ent.insert(0, ctrl_prefix + val.get("keysym"))
        entries[key] = ent
        satir += 1

    tk.Button(ayar_pencere, text="Kaydet", command=kaydet_kisayollar).grid(row=satir, column=0, columnspan=2, pady=10)

def kisa_yol(event):
    ctrl_pressed = (event.state & 0x4) != 0
    for action, shortcut in current_shortcuts.items():
        if event.keysym.lower() == shortcut["keysym"].lower() and ctrl_pressed == shortcut["ctrl"]:
            if action == "kaydet":
                kaydet()
            elif action == "sil":
                sil()
            elif action == "geri_al":
                geri_al()
            elif action == "yenile":
                guncelle_liste()
            elif action == "yedek_al":
                yedek_al_dialog()
            elif action == "yedek_yukle":
                yedek_yukle_dialog()
            break

# --- Telegram Test Mesajı ---
def telegram_test_gonder():
    try:
        telegram_bot.send_message(chat_id=OCR_CHAT_ID, text="Telegram test mesajı başarıyla gönderildi.")
        messagebox.showinfo("Telegram Test", "Telegram test mesajı gönderildi.")
    except Exception as e:
        messagebox.showerror("Telegram Hatası", f"Mesaj gönderilemedi:\n{e}")

# ------------ Tepsi ikon işlemleri ------------

def create_icon_image():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    # Basit beyaz K harfi çiz
    draw.text((16, 16), "K", fill="white")
    return image

def on_tray_quit(icon, item):
    global ana_pencere_acik
    if messagebox.askyesno("Çıkış", "Programdan çıkmak istediğinize emin misiniz?"):
        ana_pencere_acik = False
        yedekle()
        icon.stop()
        pencere.destroy()

def on_tray_show(icon, item):
    global pencere_withdrawn
    if pencere_withdrawn:
        pencere.deiconify()
        pencere_withdrawn = False
    icon.stop()

def setup_tray_icon():
    global tepsi_icon
    icon_image = create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem('Göster', on_tray_show),
        pystray.MenuItem('Çıkış', on_tray_quit)
    )
    tepsi_icon = pystray.Icon("KnightOnlineTracker", icon_image, "Knight Online Car Takip", menu)
    tepsi_icon.run()

def stop_tray_icon():
    global tepsi_icon
    if tepsi_icon:
        tepsi_icon.stop()
        tepsi_icon = None

def minimize_to_tray():
    global pencere_withdrawn
    pencere.withdraw()
    pencere_withdrawn = True
    threading.Thread(target=setup_tray_icon, daemon=True).start()

def on_close():
    minimize_to_tray()

# Pencere kapatma butonuna basınca tepsiye küçült
def on_closing():
    global pencere_withdrawn
    pencere_withdrawn = True
    pencere.withdraw()
    threading.Thread(target=setup_tray_icon, daemon=True).start()

# ---------------- Gizleme Fonksiyonları ----------------

# --- KAYDI GİZLE ---
def gizle_secili_kayit():
    secili = tree.selection()
    if not secili:
        messagebox.showinfo("Uyarı", "Lütfen gizlemek için bir kayıt seçin.")
        return
    item = tree.item(secili[0])
    values = item["values"]
    for car in car_listesi:
        if str(car.get("Giriş ID", "")) == str(values[0]) and str(car.get("Karakter İsmi", "")) == str(values[1]):
            car["gizli_mi"] = True
            break
    guncelle_liste()


def gizlenenleri_goster_pencere():
    gizli_liste = [car for car in car_listesi if car.get("gizli_mi", False)]
    if not gizli_liste:
        messagebox.showinfo("Bilgi", "Gizlenen kayıt yok.")
        return

    penc = tk.Toplevel(pencere)
    penc.title("Gizlenen Kayıtlar")
    lbl = tk.Label(penc, text="Gizlenen Kayıtlar", font=("Arial", 12, "bold"))
    lbl.pack(pady=5)
    tree_gizlenen = ttk.Treeview(penc, columns=tree["columns"], show="headings")
    for col in tree["columns"]:
        tree_gizlenen.heading(col, text=col, anchor="center")
        width = tree.column(col, option="width")
        tree_gizlenen.column(col, width=width, anchor="center")
    for car in gizli_liste:
        tree_gizlenen.insert("", tk.END, values=tuple(car.get(col, "") for col in tree["columns"]))
    tree_gizlenen.pack(fill="both", expand=True, padx=10, pady=10)

    def goster():
        secili = tree_gizlenen.selection()
        if not secili:
            messagebox.showinfo("Uyarı", "Lütfen gösterilecek kayıt seçin.")
            return
        values = tree_gizlenen.item(secili[0], "values")
        for car in car_listesi:
            if (str(car.get("Giriş ID", "")) == str(values[0]) and
                str(car.get("Karakter İsmi", "")) == str(values[1]) and
                car.get("gizli_mi", False)):
                car["gizli_mi"] = False
                log_yaz("Kayıt gösterildi", str(values))
                break
        penc.destroy()
        guncelle_liste()

    btn_goster = tk.Button(penc, text="Seçili Kaydı Göster", command=goster)
    btn_goster.pack(pady=5)


def sag_tik_menu(event):
    rowid = tree.identify_row(event.y)
    region = tree.identify("region", event.x, event.y)
    menu = tk.Menu(pencere, tearoff=0)

    if region == "cell" and rowid:
        # Sağ tıklanan satırın Giriş ID'sini bul
        item = tree.item(rowid)
        values = item["values"]
        giris_id = values[0] if values else None

        def sec_komut():
            global secili_karakter_id
            if not giris_id:
                messagebox.showerror("Hata", "Bu satır artık mevcut değil!")
                return
            secili_karakter_id = giris_id
            bulundu = False
            # Seçimi ID'ye göre Treeview'da bulup yap
            for row in tree.get_children():
                ivalues = tree.item(row)["values"]
                if str(ivalues[0]) == str(secili_karakter_id):
                    tree.selection_set(row)
                    tree.see(row)
                    secili_karakter_guncelle(None)
                    bulundu = True
                    break
            if not bulundu:
                messagebox.showerror("Hata", "Seçmek istediğin karakter şu an listede yok!")

        def gizle_komut():
            gizle_secili_kayit()
        def envanter_takip_komut():
            index = tree.index(rowid)
            envanter_penceresi_ac(index)

        menu.add_command(label="Seç", command=sec_komut)
        menu.add_command(label="Gizle", command=gizle_komut)
        menu.add_command(label="Envanter Takip", command=envanter_takip_komut)

    menu.tk_popup(event.x_root, event.y_root)


# ------------------ Kısayol Tuşları ------------------

def load_shortcuts():
    global current_shortcuts
    if os.path.exists(SHORTCUTS_PATH):
        try:
            with open(SHORTCUTS_PATH, "r", encoding="utf-8") as f:
                current_shortcuts = json.load(f)
        except Exception:
            current_shortcuts = default_shortcuts.copy()
    else:
        current_shortcuts = default_shortcuts.copy()

def save_shortcuts():
    with open(SHORTCUTS_PATH, "w", encoding="utf-8") as f:
        json.dump(current_shortcuts, f, ensure_ascii=False, indent=2)

def open_shortcut_settings():
    def kaydet_kisayollar():
        for key, entry in entries.items():
            val = entry.get().strip()
            if '+' in val:
                parts = val.split('+')
                ctrl = 'Ctrl' in parts or 'ctrl' in parts
                key_sym = [p for p in parts if p.lower() != 'ctrl'][0]
            else:
                ctrl = False
                key_sym = val
            current_shortcuts[key] = {"keysym": key_sym, "ctrl": ctrl}
        save_shortcuts()
        messagebox.showinfo("Başarılı", "Kısayollar kaydedildi.")
        ayar_pencere.destroy()

    ayar_pencere = tk.Toplevel(pencere)
    ayar_pencere.title("Klavye Kısayolları Ayarları")
    entries = {}

    satir = 0
    for key in default_shortcuts.keys():
        tk.Label(ayar_pencere, text=key.capitalize()).grid(row=satir, column=0, padx=5, pady=5, sticky="w")
        ent = tk.Entry(ayar_pencere, width=20)
        ent.grid(row=satir, column=1, padx=5, pady=5)
        val = current_shortcuts.get(key, default_shortcuts[key])
        ctrl_prefix = "Ctrl+" if val.get("ctrl") else ""
        ent.insert(0, ctrl_prefix + val.get("keysym"))
        entries[key] = ent
        satir += 1

    tk.Button(ayar_pencere, text="Kaydet", command=kaydet_kisayollar).grid(row=satir, column=0, columnspan=2, pady=10)

def kisa_yol(event):
    ctrl_pressed = (event.state & 0x4) != 0
    for action, shortcut in current_shortcuts.items():
        if event.keysym.lower() == shortcut["keysym"].lower() and ctrl_pressed == shortcut["ctrl"]:
            if action == "kaydet":
                kaydet()
            elif action == "sil":
                sil()
            elif action == "geri_al":
                geri_al()
            elif action == "yenile":
                guncelle_liste()
            elif action == "yedek_al":
                yedek_al_dialog()
            elif action == "yedek_yukle":
                yedek_yukle_dialog()
            break

# --- Telegram Test Mesajı ---
def telegram_test_gonder():
    try:
        telegram_bot.send_message(chat_id=OCR_CHAT_ID, text="Telegram test mesajı başarıyla gönderildi.")
        messagebox.showinfo("Telegram Test", "Telegram test mesajı gönderildi.")
    except Exception as e:
        messagebox.showerror("Telegram Hatası", f"Mesaj gönderilemedi:\n{e}")

# ------------ Tepsi ikon işlemleri ------------

def create_icon_image():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    # Basit beyaz K harfi çiz
    draw.text((16, 16), "K", fill="white")
    return image

def on_tray_quit(icon, item):
    global ana_pencere_acik
    if messagebox.askyesno("Çıkış", "Programdan çıkmak istediğinize emin misiniz?"):
        ana_pencere_acik = False
        yedekle()
        icon.stop()
        pencere.destroy()

def on_tray_show(icon, item):
    global pencere_withdrawn
    if pencere_withdrawn:
        pencere.deiconify()
        pencere_withdrawn = False
    icon.stop()

def setup_tray_icon():
    global tepsi_icon
    icon_image = create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem('Göster', on_tray_show),
        pystray.MenuItem('Çıkış', on_tray_quit)
    )
    tepsi_icon = pystray.Icon("KnightOnlineTracker", icon_image, "Knight Online Car Takip", menu)
    tepsi_icon.run()

def stop_tray_icon():
    global tepsi_icon
    if tepsi_icon:
        tepsi_icon.stop()
        tepsi_icon = None

def minimize_to_tray():
    global pencere_withdrawn
    pencere.withdraw()
    pencere_withdrawn = True
    threading.Thread(target=setup_tray_icon, daemon=True).start()

def on_close():
    minimize_to_tray()

# Pencere kapatma butonuna basınca tepsiye küçült
def on_closing():
    global pencere_withdrawn
    pencere_withdrawn = True
    pencere.withdraw()
    threading.Thread(target=setup_tray_icon, daemon=True).start()

# ------------ Scrollbar ve sütun gizleme ------------

def toggle_column(event):
    # Sağ tıklayınca sütun gizleme/gösterme işlemi
    region = tree.identify("region", event.x, event.y)
    if region != "heading":
        return
    col = tree.identify_column(event.x)
    col_num = int(col.replace("#", "")) - 1
    if col_num < 0 or col_num >= len(tree["columns"]):
        return
    # Sütun görünürlüğünü toggle et
    current_width = tree.column(tree["columns"][col_num], option="width")
    if current_width == 0:
        # Sütunu önceki genişlikte göster
        tree.column(tree["columns"][col_num], width=col_widths[tree["columns"][col_num]])
    else:
        # Sütunu gizle (genişliği 0 yap)
        tree.column(tree["columns"][col_num], width=0)


import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Temel pencere ayarları
pencere = tk.Tk()
pencere.title("Knight Online Car Takip")
pencere.geometry("1500x700")
pencere.state("zoomed")

# Grid yapılandırması (2 sütun)
pencere.grid_rowconfigure(0, weight=1)
pencere.grid_rowconfigure(1, weight=8)  # Treeview için yüksek ağırlık
pencere.grid_columnconfigure(0, weight=3)  # Sol geniş form alanı
pencere.grid_columnconfigure(1, weight=5)  # Sağ geniş liste alanı

style = ttk.Style()
style.theme_use("clam")

# Frame'ler
frm_left = tk.Frame(pencere, bg="#212121")
frm_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
frm_left.grid_columnconfigure(1, weight=1)

frm_right = tk.Frame(pencere, bg="#212121")
frm_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
frm_right.grid_columnconfigure(1, weight=1)

right_row = 0  # BURAYA EKLE

sistem_saat_label = tk.Label(
    frm_right, 
    text="", 
    font=("Arial", 16, "bold"),
    bg="#212121", 
    fg="red"
)
sistem_saat_label.grid(row=right_row, column=0, columnspan=2, pady=5)
right_row += 1


# --- Değişkenler ---
giris_id = tk.StringVar()
karakter_isim = tk.StringVar()
kamp = tk.StringVar()
mob = tk.StringVar()
gunluk_getiri = tk.StringVar()
pot_turu = tk.StringVar(value="MP Pot")
mp_pot_adedi = tk.StringVar()
job = tk.StringVar()
peri_turu = tk.StringVar(value="Para Perisi")
pc_bilgi = tk.StringVar()
not_kutu = tk.StringVar()
genie_var = tk.StringVar(value="00:00")
premium_var = tk.StringVar()
toplam_mana_var = tk.StringVar()
saatlik_mana_var = tk.StringVar()
mana_seviyesi_var = tk.StringVar()
arama_var = tk.StringVar()
tema_var = tk.StringVar(value="Koyu")
secili_karakter_var = tk.StringVar(value="Seçili Karakter: Yok")
gizli_goster_var = tk.BooleanVar(value=False)

# --- Sol Alan Form Elemanları ---
labels = [
    ("Üy Giriş ID", giris_id),
    ("Karakter İsmi", karakter_isim),
    ("Kamp", kamp),
    ("Mob", mob),
    ("Günlük Getiri", gunluk_getiri),
    ("Pot Türü", pot_turu),
    ("MP Pot Adedi", mp_pot_adedi),
    ("Job", job),
    ("Peri Türü", peri_turu),
    ("PC", pc_bilgi),
    ("Not", not_kutu),
    ("Genie (Saat:Dakika)", genie_var),
    ("Premium (gün)", premium_var),
    ("Toplam Mana", toplam_mana_var),
    ("Saatlik Mana Tüketimi", saatlik_mana_var),
    ("Mana Seviyesi", mana_seviyesi_var),
]

for i, (text, var) in enumerate(labels):
    tk.Label(frm_left, text=text, font=("Arial", 11), bg="#212121", fg="#fafafa").grid(row=i, column=0, sticky="e", padx=5, pady=5)
    if text in ["Kamp", "Pot Türü", "Job", "Peri Türü"]:
        if text == "Kamp":
            combo_values = ["1", "2", "3", "4", "5"]
        elif text == "Pot Türü":
            combo_values = ["MP Pot", "HP Pot"]
        elif text == "Job":
            combo_values = ["Warrior", "Mage", "Rogue", "Priest", "Kurian"]
        elif text == "Peri Türü":
            combo_values = ["Para Perisi", "Düz Peri"]
        cb = ttk.Combobox(frm_left, textvariable=var, values=combo_values, state="readonly", font=("Arial", 11))
        cb.grid(row=i, column=1, sticky="we", padx=5, pady=5)
    else:
        entry = tk.Entry(frm_left, textvariable=var, font=("Arial", 11), bg="#333", fg="#fafafa")
        entry.grid(row=i, column=1, sticky="we", padx=5, pady=5)

secili_karakter_label = tk.Label(frm_left, textvariable=secili_karakter_var, font=("Arial", 12), bg="#212121", fg="red")
secili_karakter_label.grid(row=len(labels), column=0, columnspan=2, pady=15)

# --- Sağ Alan Butonlar ---
right_row = 0

def dummy_func():
    messagebox.showinfo("Bilgi", "Fonksiyon henüz uygulanmadı.")

buttons = [
    ("Kaydet / Güncelle", kaydet, "#38c172", "white"),
    ("Sil", sil, "#f34646", "white"),
    ("Geri Al", geri_al, "#e39c20", "white"),
    ("Telegram Test", telegram_test_gonder, "#ff6600", "white"),
    ("Yedek Al (Manual)", yedekle, "#3498db", "white"),
    ("Yedek Yükle", yedek_yukle_dialog, "#f7b731", "black"),
    ("Bildirim Test", dummy_func, "#ff9900", "black"),
    ("Envanter Takip", envanter_buton_tiklandi, "#5a8ad7", "white"),
    ("Kısayol Ayarları", open_shortcut_settings, "#8e44ad", "white"),
    ("Gizlenen Sütunları Göster", gizlenen_sutunlari_goster, None, "black")
]

for text, cmd, bg_color, fg_color in buttons:
    fg = fg_color if fg_color else "white"
    btn = tk.Button(frm_right, text=text, command=cmd, width=18, font=("Arial", 11, "bold"),
                    bg=bg_color if bg_color else "#444", fg=fg)
    btn.grid(row=right_row, column=0, columnspan=2, pady=8, sticky="we")
    right_row += 1

# --- ARA ve TEMA ---
tk.Label(frm_right, text="Ara/Filtrele", font=("Arial", 11), bg="#212121", fg="#fafafa").grid(row=right_row, column=0, sticky="e", padx=7, pady=5)
arama_entry = tk.Entry(frm_right, textvariable=arama_var, font=("Arial", 11), bg="#333", fg="#fafafa")
arama_entry.grid(row=right_row, column=1, sticky="we", padx=7, pady=5)
right_row += 1

# Tema labelı
tk.Label(frm_right, text="Tema Seçimi", font=("Arial", 11), bg="#212121", fg="#fafafa").grid(row=right_row, column=0, sticky="e", padx=7, pady=5)

# Tema combobox, zaten senin verdiğin koda çok benzeyen ama padding ve sticky ayarı daha iyi
tema_sec = ttk.Combobox(frm_right, textvariable=tema_var, font=("Arial", 11), values=["Koyu", "Açık"], state="readonly", width=15)
tema_sec.grid(row=right_row, column=1, sticky="we", padx=7, pady=5)
tema_sec.bind("<<ComboboxSelected>>", tema_degistir)
right_row += 1



# --- TREEVIEW FRAME ---
tree_frame = tk.Frame(pencere, bg="#212121")
tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

# Grid ağırlıklar
pencere.grid_rowconfigure(1, weight=8)

# Scrollbarlar
tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scroll_y.grid(row=0, column=1, sticky="ns")

tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
tree_scroll_x.grid(row=1, column=0, sticky="ew")

columns = [
    "Giriş ID", "Karakter İsmi", "Kamp", "Mob", "Günlük Getiri", "Pot Türü", "MP Pot Adedi",
    "Job", "Peri Türü", "PC", "Not", "Genie", "Premium", "Genie Canli",
    "Premium Canli", "Toplam Mana", "Saatlik Mana Tüketimi", "Mana Seviyesi"
]

col_widths = {
    "Giriş ID": 110,
    "Karakter İsmi": 150,
    "Kamp": 70,
    "Mob": 50,
    "Günlük Getiri": 90,
    "Pot Türü": 80,
    "MP Pot Adedi": 90,
    "Job": 90,
    "Peri Türü": 90,
    "PC": 100,
    "Not": 140,
    "Genie": 75,
    "Premium": 75,
    "Genie Canli": 100,
    "Premium Canli": 100,
    "Toplam Mana": 90,
    "Saatlik Mana Tüketimi": 90,
    "Mana Seviyesi": 80
}

# Treeview oluşturma (her yerde tree olacak)
tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                    yscrollcommand=tree_scroll_y.set,
                    xscrollcommand=tree_scroll_x.set)
tree.grid(row=0, column=0, sticky="nsew")
tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

for col in columns:
    tree.heading(col, text=col, anchor="center")
    tree.column(col, width=col_widths[col], anchor="center")

tree.tag_configure("mor", background="#5a437a", foreground="#fafafa")
tree.tag_configure("kirmizi", background="#522f2f", foreground="#fafafa")
tree.tag_configure("mavi", background="#2e4066", foreground="#fafafa")
tree.tag_configure("yesil", background="#35543e", foreground="#fafafa")
tree.tag_configure("turuncu", background="#63543c", foreground="#fafafa")
tree.tag_configure("gri", background="#2b2b2b", foreground="#fafafa")

# Seçili karakter güncelleme fonksiyonu
def secili_karakter_guncelle(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        values = item["values"]
        karakter_ismi = values[1] if len(values) > 1 else ""
        secili_karakter_var.set(f"Seçili Karakter: {karakter_ismi}")
    else:
        secili_karakter_var.set("Seçili Karakter: Yok")


# Sadece bu eventi bağla
tree.bind("<<TreeviewSelect>>", secili_karakter_guncelle)
tree.bind("<Button-3>", sag_tik_menu)
tree.bind("<Double-1>", tree_cift_tikla)

# Sistem saati label'ı oluşturuldu (senin kodun)
sistem_saat_label = tk.Label(frm_right, text="", font=("Arial", 20, "bold"), bg="#212121", fg="red")
sistem_saat_label.grid(row=right_row, column=0, columnspan=2, pady=5)
right_row += 1


def sistem_saat_guncelle():
    from datetime import datetime
    simdi = datetime.now().strftime("%H:%M:%S")
    sistem_saat_label.config(text=simdi)
    pencere.after(1000, sistem_saat_guncelle)

sistem_saat_guncelle()

yedek_yukle_otomatik()
pencere.after(1000, genie_premium_checker)
mana_kritik_kontrol()

def tabloyu_surekli_guncelle():
    guncelle_liste()
    pencere.after(1000, tabloyu_surekli_guncelle)


def mana_azalt_ve_guncelle():
    now_ts = datetime.now().timestamp()
    for car in car_listesi:
        try:
            toplam_mana = int(car.get("Toplam Mana", "0") or 0)
            saatlik_mana = int(car.get("Saatlik Mana Tüketimi", "0") or 0)
            if toplam_mana > 0 and saatlik_mana > 0:
                # İlk açılışta/eklemede kalan_mana tanımlı değilse:
                if "mana_last_update" not in car:
                    car["mana_last_update"] = now_ts
                    car["kalan_mana"] = toplam_mana
                else:
                    gecen_saniye = now_ts - car["mana_last_update"]
                    car["mana_last_update"] = now_ts
                    harcanan = saatlik_mana * (gecen_saniye / 3600)  # saniyede düşüş
                    car["kalan_mana"] = max(0, car.get("kalan_mana", toplam_mana) - harcanan)
                yuzde = (car["kalan_mana"] / toplam_mana) * 100 if toplam_mana > 0 else 0
                car["Mana Seviyesi"] = f"%{yuzde:.1f}"
            else:
                car["Mana Seviyesi"] = "%100.0"
        except Exception as e:
            print("Mana otomatik azalma hatası:", e)
            continue
    
    tabloyu_surekli_guncelle()
    guncelle_liste()  # BU SATIRI EKLE!
    pencere.after(1000, mana_azalt_ve_guncelle)
# --- Sistem Tepsisi Eklentisi Başlangıcı ---
tepsi_icon = None
pencere_withdrawn = False
ana_pencere_acik = True

def create_icon_image():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    draw.text((16, 16), "K", fill="white")
    return image

def on_tray_quit(icon, item):
    global ana_pencere_acik
    if messagebox.askyesno("Çıkış", "Programdan çıkmak istediğinize emin misiniz?"):
        ana_pencere_acik = False
        yedekle()
        icon.stop()
        pencere.destroy()

def on_tray_show(icon, item):
    global pencere_withdrawn
    if pencere_withdrawn:
        pencere.deiconify()
        pencere_withdrawn = False
    icon.stop()

def setup_tray_icon():
    global tepsi_icon
    icon_image = create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem('Göster', on_tray_show),
        pystray.MenuItem('Çıkış', on_tray_quit)
    )
    tepsi_icon = pystray.Icon("KnightOnlineTracker", icon_image, "Knight Online Car Takip", menu)
    tepsi_icon.run()

def minimize_to_tray():
    global pencere_withdrawn
    pencere.withdraw()
    pencere_withdrawn = True
    threading.Thread(target=setup_tray_icon, daemon=True).start()

def on_closing():
    minimize_to_tray()

# Pencere kapatma tuşuna bu fonksiyonu bağla
pencere.protocol("WM_DELETE_WINDOW", on_closing)
# --- Sistem Tepsisi Eklentisi Sonu ---

kritik_ozet_popup()
otomatik_yedekle()
pencere.mainloop()    



