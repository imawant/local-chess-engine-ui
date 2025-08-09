# local-chess-engine-ui

<img width="440" height="350" alt="image" src="https://github.com/user-attachments/assets/0e6660c4-cece-42fb-87d4-f675352d30d1" />

Proyek ini adalah antarmuka grafis permainan catur berbasis **Pygame** yang terintegrasi dengan **Stockfish** sebagai engine catur lokal.  
Dapat dijalankan sepenuhnya **offline**, mendukung drag-and-drop, evaluasi bar real-time, undo/redo, dan fitur hint langkah terbaik dari engine.

---

## 🎯 Fitur
- **Drag-and-drop bidak** dengan highlight langkah legal.
- **Hint langkah terbaik** dari Stockfish.
- **Engine Move** untuk membiarkan Stockfish bermain.
- **Undo/Redo** langkah permainan.
- **Evaluation bar** real-time.
- **Flip Board** untuk mengganti perspektif papan.
- **Jalan offline** tanpa internet (hanya perlu Stockfish lokal).

---

## 📦 Yang Harus Dipersiapkan
1. **Python 3.8+** sudah terinstall.
2. Install library **Pygame** dan **python-chess** 
3. **Stockfish engine** untuk Windows:
   - Download di [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
   - Pilih versi Windows yang sesuai CPU (misalnya `x86-64-avx2`).
   - Ekstrak ZIP dan salin **path lengkap** file `.exe` (misalnya  
     `C:\Users\NamaAnda\Downloads\stockfish\stockfish-windows-x86-64-avx2.exe`).
   - ganti bagian STOCKFISH_PATH menjadi path menuju file stockfish binary yang telah diextract sebelumnya
     <img width="365" height="30" alt="image" src="https://github.com/user-attachments/assets/0b04eb1e-134f-49f5-9813-e7410967bf03" />

     contoh:
     "C:\Users\User\Downloads\stockfish\stockfish-windows-x86-64-avx2.exe

---

## ⚙️ Langkah Instalasi & Konfigurasi

### 1. Clone Repositori
```bash
git clone https://github.com/imawant/local-chess-engine-ui.git
cd local-chess-engine-ui
python main.py
