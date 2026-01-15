from flask import Flask, send_from_directory, render_template_string, request
import os, socket, tkinter as tk
from tkinter import filedialog, messagebox
import threading, webbrowser
import qrcode
from PIL import Image, ImageTk

app = Flask(__name__)
shared_folder = None
upload_folder = None
server_thread = None
qr_img = None
activity_logs = []

def add_log(msg):
    activity_logs.append(msg)
    log_text.config(state="normal")
    log_text.insert("end", msg + "\n")
    log_text.see("end")
    log_text.config(state="disabled")

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

@app.route('/')
def index():
    global shared_folder
    if not shared_folder:
        return "<h3>Belum ada folder dipilih</h3>"
    files = os.listdir(shared_folder)
    if not files:
        return "<h3>Folder kosong</h3>"
    html = "<h2>Daftar File</h2><ul>"
    for f in files:
        html += f'<li><a href="/files/{f}">{f}</a></li>'
    html += "</ul>"
    return render_template_string(html)

@app.route('/files/<path:filename>')
def download_file(filename):
    add_log(f"📤 File diunduh: {filename}")
    return send_from_directory(shared_folder, filename, as_attachment=True)

UPLOAD_HTML = """
<!doctype html>
<title>Upload File</title>
<h1>Upload File ke PC</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
"""

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global upload_folder
    if request.method == 'POST':
        f = request.files['file']
        if f and upload_folder:
            save_path = os.path.join(upload_folder, f.filename)
            f.save(save_path)
            add_log(f"📥 File diupload: {f.filename} → {upload_folder}")
            return f"Upload sukses! File tersimpan di {upload_folder}"
    return render_template_string(UPLOAD_HTML)

def start_flask(link_target="/"):
    ip = get_ip()
    link = f"http://{ip}:5000{link_target}"
    link_label.config(text=f"Server aktif: {link}\n"
                           "(Wajib 1 jaringan WiFi yang sama)\n"
                           "⚡ Kecepatan transfer tergantung seberapa cepat WiFi kamu")

    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    global qr_img
    qr_img = ImageTk.PhotoImage(img)
    qr_label.config(image=qr_img)
    qr_label.image = qr_img

    global server_thread
    if not server_thread:
        server_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
        server_thread.daemon = True
        server_thread.start()

def stop_flask():
    os._exit(0)

def choose_folder_share():
    global shared_folder
    folder = filedialog.askdirectory()
    if folder:
        shared_folder = folder
        info_label.config(text="📤 Kirim File dari Laptop ke HP:\n"
                               "1. Pastikan PC & HP 1 WiFi\n"
                               "2. Scan QR / buka link di HP\n"
                               "3. Pilih file di browser HP untuk download\n"
                               "4. Klik Stop Server jika selesai\n"
                               "⚡ Kecepatan transfer tergantung WiFi")
        messagebox.showinfo("Instruksi", "Kirim File:\n\n"
                            "1. Pastikan PC & HP 1 WiFi\n"
                            "2. Scan QR / buka link di HP\n"
                            "3. Download file dari browser HP\n"
                            "4. Klik Stop Server jika selesai\n\n"
                            "⚡ Kecepatan transfer tergantung seberapa cepat WiFi kamu")
        start_flask("/")

def choose_folder_upload():
    global upload_folder
    folder = filedialog.askdirectory()
    if folder:
        upload_folder = folder
        info_label.config(text="📥 Upload File dari HP ke Laptop:\n"
                               "1. Pastikan PC & HP 1 WiFi\n"
                               "2. Scan QR / buka link di HP\n"
                               "3. Pilih file di HP lalu klik Upload\n"
                               "4. File tersimpan di folder PC\n"
                               "5. Klik Stop Server jika selesai\n"
                               "⚡ Kecepatan transfer tergantung WiFi")
        messagebox.showinfo("Instruksi", "Upload File:\n\n"
                            "1. Pastikan PC & HP 1 WiFi\n"
                            "2. Scan QR / buka link di HP\n"
                            "3. Pilih file di HP lalu klik Upload\n"
                            "4. File tersimpan di folder PC\n"
                            "5. Klik Stop Server jika selesai\n\n"
                            "⚡ Kecepatan transfer tergantung seberapa cepat WiFi kamu")
        start_flask("/upload")

# === Tooltip helper ===
class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# === GUI ===
root = tk.Tk()
root.title("File Share Flask + QR")

# Set window di tengah layar
window_width = 500
window_height = 650
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width/2) - (window_width/2))
y_coordinate = int((screen_height/2) - (window_height/2))
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

choose_btn = tk.Button(root, text="Pilih Folder untuk Share (Laptop → HP)", command=choose_folder_share)
choose_btn.pack(pady=10)

upload_btn = tk.Button(root, text="Terima File dari HP (HP → Laptop)", command=choose_folder_upload)
upload_btn.pack(pady=10)

link_label = tk.Label(root, text="Belum ada server")
link_label.pack(pady=10)

qr_label = tk.Label(root)
qr_label.pack(pady=10)

info_label = tk.Label(root, text="Instruksi akan muncul di sini", justify="left")
info_label.pack(pady=10)

log_label = tk.Label(root, text="Log Aktivitas:")
log_label.pack(pady=5)

log_text = tk.Text(root, height=10, width=60, state="disabled")
log_text.pack(pady=5)

stop_btn = tk.Button(root, text="Stop Server", command=stop_flask)
stop_btn.pack(pady=10)

# === Footer ===
footer_label = tk.Label(root, text="Aplikasi ini dibuat oleh Riki Setiawan", font=("Arial", 10, "italic"))
footer_label.pack(pady=5)

def open_instagram():
    webbrowser.open("https://www.instagram.com/riki.setiawan92/")

def open_whatsapp():
    webbrowser.open("https://wa.me/6281220707244")

ig_btn = tk.Button(root, text="Instagram", command=open_instagram, fg="white", bg="#E1306C")
ig_btn.pack(pady=5)
ToolTip(ig_btn, "Klik untuk membuka Instagram Riki Setiawan")

wa_btn = tk.Button(root, text="WhatsApp", command=open_whatsapp, fg="white", bg="#25D366")
wa_btn.pack(pady=5)
ToolTip(wa_btn, "Klik untuk chat WhatsApp Riki Setiawan")

root.mainloop()