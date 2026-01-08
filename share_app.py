from flask import Flask, send_from_directory, render_template_string
import os, socket, tkinter as tk
from tkinter import filedialog
import threading
import qrcode
from PIL import Image, ImageTk

app = Flask(__name__)
shared_folder = None
server_thread = None
qr_img = None

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
    return send_from_directory(shared_folder, filename, as_attachment=True)

def start_flask():
    ip = get_ip()
    link = f"http://{ip}:5000"
    link_label.config(text=f"Server aktif: {link}")

    # Buat QR Code
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    global qr_img
    qr_img = ImageTk.PhotoImage(img)
    qr_label.config(image=qr_img)
    qr_label.image = qr_img

    # Jalankan Flask di thread terpisah
    global server_thread
    server_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    server_thread.daemon = True
    server_thread.start()

def stop_flask():
    os._exit(0)  # cara cepat matikan server + GUI

def choose_folder():
    global shared_folder
    folder = filedialog.askdirectory()
    if folder:
        shared_folder = folder
        start_flask()  # otomatis start server setelah pilih folder

root = tk.Tk()
root.title("File Share Flask + QR")

choose_btn = tk.Button(root, text="Pilih Folder", command=choose_folder)
choose_btn.pack(pady=10)

link_label = tk.Label(root, text="Belum ada server")
link_label.pack(pady=10)

qr_label = tk.Label(root)
qr_label.pack(pady=10)

stop_btn = tk.Button(root, text="Stop Server", command=stop_flask)
stop_btn.pack(pady=10)

root.mainloop()