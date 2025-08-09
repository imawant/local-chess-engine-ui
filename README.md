# local-chess-engine-ui

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
2. **Pygame** dan **python-chess** (akan diinstal saat setup).
3. **Stockfish engine** untuk Windows:
   - Download di [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
   - Pilih versi Windows yang sesuai CPU (misalnya `x86-64-avx2`).
   - Ekstrak ZIP dan salin **path lengkap** file `.exe` (misalnya  
     `C:\Users\NamaAnda\Downloads\stockfish\stockfish-windows-x86-64-avx2.exe`).

---

## ⚙️ Langkah Instalasi & Konfigurasi

### 1. Clone Repositori
```bash
git clone https://github.com/imawant/local-chess-engine-ui.git
cd local-chess-engine-ui
**
