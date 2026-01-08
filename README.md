\# 📂 ShareApp



Aplikasi sederhana untuk berbagi file/folder dari laptop ke perangkat lain (misalnya Android) melalui jaringan Wi-Fi.  

Dibuat dengan \*\*Python + Flask + Tkinter + QRCode\*\*, aplikasi ini otomatis menampilkan link dan QR Code untuk akses file.



---



\## ✨ Fitur

\- Pilih folder → otomatis aktifkan server HTTP.

\- Tampilkan daftar file di browser laptop/HP.

\- QR Code otomatis → cukup scan di HP, tanpa ketik IP.

\- Tombol \*\*Stop Server\*\* untuk mematikan server dengan cepat.

\- Bisa dijalankan sebagai `.exe` (portable, tanpa perlu Python di laptop target).



---



\## 📦 Dependensi

Jika menjalankan dari source code Python, pastikan install library berikut:



```bash

pip install flask qrcode pillow

python share\_app.py

