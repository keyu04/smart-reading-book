# 📖 Smart Audio Book Reader

**Smart Audio Book Reader** is a Python-based intelligent reading assistant that reads aloud PDF and TXT files using a text-to-speech engine, highlights the text being read, and supports voice commands for hands-free interaction. The application remembers your last read position and offers controls for reading speed, volume, dark mode, and font size.

---

## 🚀 Features

- 📂 Open and read PDF/TXT books
- 🔊 Text-to-Speech (adjustable speed and volume)
- 🎤 Voice commands: Start, Stop, Resume, Restart, Adjust Speed
- 💡 Dark Mode toggle
- 🧠 Resume from last reading position
- 🟨 Sentence highlighting during speech
- 📊 Reading progress bar
- 🗣️ Real-time voice control using speech recognition

---

## 🛠️ Requirements

### ✅ Prerequisites

- Python 3.8 or higher
- PyCharm IDE (recommended for running/debugging)

### 📦 Install Required Libraries

```bash
pip install pyttsx3
pip install pyaudio
pip install speechrecognition
pip install PyPDF2
```

> ⚠️ Note: On Windows, use `pipwin` to install PyAudio:
```bash
pip install pipwin
pipwin install pyaudio
```

---

## 📂 Project Structure

```
📁 smart-audio-book-reader/
 ├️ 📄 index.py     # Main GUI + logic script
 ├️ 📄 last_read_position.json   # Auto-saved reading state
 └️ 📄 README.md                 # Project instructions
```

---

## 💻 How to Run in PyCharm

### 1. Download the Project

- **Option A**: Clone the repository  
  ```bash
  git clone https://github.com/yourusername/smart-audio-book-reader.git
  cd smart-audio-book-reader
  ```

- **Option B**: Download ZIP from GitHub → Extract

---

### 2. Open the Project in PyCharm

- Open **PyCharm**
- Click `File > Open` → select the extracted project folder
- Let PyCharm index the project

---

### 3. Configure Python Interpreter

- Go to `File > Settings > Project > Python Interpreter`
- Choose Python 3.8+ (or create a new virtual environment)
- Install missing packages (PyCharm will usually prompt this)

---

### 4. Run the Application

- Open `index.py`
- Click the green "Run" button or right-click → Run
- GUI window will launch with controls

---

## 🎧 Voice Commands You Can Use

| Voice Command       | Action                     |
|---------------------|----------------------------|
| “start”             | Start reading              |
| “stop” / “pause”    | Stop reading               |
| “resume”            | Resume reading             |
| “restart”           | Start from beginning       |
| “increase speed”    | Increase reading speed     |
| “decrease speed”    | Decrease reading speed     |

> Make sure your microphone is connected and functional.

---

## 🧪 Performance Notes

While this application doesn't use traditional ML classification metrics (like accuracy/F1), performance is evaluated based on:

- **Speech-to-text command success rate**
- **TTS smoothness and clarity**
- **User responsiveness (e.g., highlight sync)**
- **Robustness in noisy environments**

---

## 🔐 Data & Privacy

- No user data is stored online
- Reading position saved locally in `last_read_position.json`
- Voice data is only processed in real-time and not stored

---

## 🌍 Future Enhancements

- EPUB file support
- Offline speech recognition models
- Word-by-word highlighting
- Mobile version using Kivy or Flutter

---
