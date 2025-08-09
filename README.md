# local-chess-engine-ui

<img width="352" height="280" alt="image" src="https://github.com/user-attachments/assets/0e6660c4-cece-42fb-87d4-f675352d30d1" />      
   <img width="352" height="280" alt="image" src="https://github.com/user-attachments/assets/5aa26dca-bb80-4634-ab8d-1a49404eaa4e" />


This project is a **Pygame-based graphical chess interface** integrated with **Stockfish** as a local chess engine.
It runs fully **offline**, supports drag-and-drop, real-time evaluation bar, undo/redo, and engine move hints.

---

## 🎯 Features

* **Drag-and-drop pieces** with legal move highlighting.
* **Best move hints** from Stockfish.
* **Engine Move** to let Stockfish play automatically.
* **Undo/Redo** functionality.
* **Real-time evaluation bar**.
* **Flip Board** to change perspective.
* **Works fully offline** (only requires a local Stockfish engine).

---

## 📦 Requirements

1. **Python 3.8+** installed.
2. Install the required libraries:

   ```bash
   pip install pygame python-chess
   ```
3. **Stockfish Engine** for Windows:

   * Download from [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
   * Select the Windows build that matches your CPU (e.g., `x86-64-avx2`).
   * Extract the ZIP file.
   * Copy the **full path** to the `.exe` file (e.g.,
     `C:\Users\YourName\Downloads\stockfish\stockfish-windows-x86-64-avx2.exe`).
   * Update the `STOCKFISH_PATH` variable in the code to point to your extracted Stockfish binary:

     <img width="365" height="30" alt="image" src="https://github.com/user-attachments/assets/0b04eb1e-134f-49f5-9813-e7410967bf03" />  

     **Example:**

     ```text
     C:\Users\User\Downloads\stockfish\stockfish-windows-x86-64-avx2.exe
     ```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/imawant/local-chess-engine-ui.git
cd local-chess-engine-ui
```

### 2. Install Dependencies

```bash
pip install pygame python-chess
```

### 3. Configure Stockfish Path

Open `main.py` (or the relevant config file) and replace the `STOCKFISH_PATH` value with the **full path** to your Stockfish `.exe` file as described above.

### 4. Run the Application

```bash
python main.py
```
