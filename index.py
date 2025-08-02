import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import pyttsx3
import threading
import json
from PyPDF2 import PdfReader
import os
import re
import speech_recognition as sr
import pyaudio

SAVE_FILE = "last_read_position.json"

class SmartBookReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Audio Book Reader")
        self.root.geometry("850x700")

        # Text display widget
        self.text_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.text_display.pack(fill=tk.BOTH, expand=True)

        # Page navigation buttons
        self.pages = []
        self.current_page_index = 0

        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack()

        self.prev_page_button = tk.Button(self.nav_frame, text="Previous Page", command=self.prev_page)
        self.prev_page_button.grid(row=0, column=0, padx=5)

        self.next_page_button = tk.Button(self.nav_frame, text="Next Page", command=self.next_page)
        self.next_page_button.grid(row=0, column=1, padx=5)

        # Controls Frame
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=5)

        self.open_button = tk.Button(self.controls_frame, text="Open Book", command=self.open_book)
        self.open_button.grid(row=0, column=0, padx=5)

        self.start_button = tk.Button(self.controls_frame, text="Start Reading", command=self.start_reading)
        self.start_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(self.controls_frame, text="Stop Reading", command=self.stop_reading)
        self.stop_button.grid(row=0, column=2, padx=5)

        self.font_size = 12
        self.font_size_button = tk.Button(self.controls_frame, text="Font +", command=self.increase_font_size)
        self.font_size_button.grid(row=0, column=3, padx=5)

        self.font_size_minus_button = tk.Button(self.controls_frame, text="Font -", command=self.decrease_font_size)
        self.font_size_minus_button.grid(row=0, column=4, padx=5)

        self.dark_mode = False
        self.mode_button = tk.Button(self.controls_frame, text="Toggle Dark Mode", command=self.toggle_mode)
        self.mode_button.grid(row=0, column=5, padx=5)

        self.read_from_start_button = tk.Button(self.controls_frame, text="Read from Start", command=self.read_from_start)
        self.read_from_start_button.grid(row=0, column=6, padx=5)

        # Speed controls
        tk.Label(self.controls_frame, text="Speed:").grid(row=1, column=0, padx=5)
        self.speed_var = tk.IntVar(value=150)
        self.speed_scale = ttk.Scale(self.controls_frame, from_=50, to=300, orient=tk.HORIZONTAL,
                                     variable=self.speed_var, command=self.update_speed)
        self.speed_scale.grid(row=1, column=1, padx=5, sticky="we", columnspan=2)

        # Volume controls
        tk.Label(self.controls_frame, text="Volume:").grid(row=1, column=3, padx=5)
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_scale = ttk.Scale(self.controls_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                      variable=self.volume_var, command=self.update_volume)
        self.volume_scale.grid(row=1, column=4, padx=5, sticky="we", columnspan=2)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=700, mode="determinate")
        self.progress.pack(pady=5)

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.speed_var.get())
        self.engine.setProperty('volume', self.volume_var.get())

        self.is_reading = False
        self.reading_thread = None
        self.stop_flag = threading.Event()

        self.book_text = ""
        self.sentences = []
        self.current_sentence_index = 0
        self.current_word_index = 0
        self.book_path = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        threading.Thread(target=self.speech_control, daemon=True).start()

    def open_book(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
        if file_path:
            self.book_path = file_path
            self.load_book(file_path)

    def load_book(self, file_path):
        try:
            if file_path.endswith(".pdf"):
                pdf_reader = PdfReader(file_path)
                self.pages = [page.extract_text() or "[Empty page]" for page in pdf_reader.pages]
                self.current_page_index = 0
                self.display_current_page()
                text = "\n".join(self.pages)
            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()
                self.text_display.delete(1.0, tk.END)
                self.text_display.insert(tk.END, text)

            self.book_text = text
            self.sentences = self.split_into_sentences(text)
            self.progress["maximum"] = len(self.sentences)

            self.current_sentence_index, self.current_word_index = self.load_position_for_book(file_path)
            self.progress['value'] = self.current_sentence_index
            self.remove_highlight()

        except Exception as e:
            messagebox.showerror("Error", f"Error loading book: {str(e)}")

    def display_current_page(self):
        self.text_display.delete(1.0, tk.END)
        if 0 <= self.current_page_index < len(self.pages):
            self.text_display.insert(tk.END, self.pages[self.current_page_index])
            self.root.title(f"Smart Audio Book Reader - Page {self.current_page_index + 1} of {len(self.pages)}")

    def next_page(self):
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self.display_current_page()

    def prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.display_current_page()

    def split_into_sentences(self, text):
        sentence_endings = re.compile(r'(?<=[.!?]) +')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def speech_control(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        while True:
            try:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("Listening for commands...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Recognized command: {command}")

                    if "restart" in command:
                        self.read_from_start()
                    elif "start" in command:
                        self.start_reading()
                    elif "pause" in command or "stop" in command:
                        self.stop_reading()
                    elif "resume" in command:
                        self.start_reading()
                    elif "increase speed" in command:
                        new_rate = self.engine.getProperty('rate') + 20
                        self.engine.setProperty('rate', new_rate)
                        self.speed_var.set(new_rate)
                    elif "decrease speed" in command:
                        new_rate = max(50, self.engine.getProperty('rate') - 20)
                        self.engine.setProperty('rate', new_rate)
                        self.speed_var.set(new_rate)

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue

    def start_reading(self):
        if not self.sentences:
            messagebox.showinfo("Info", "Please open a book first.")
            return
        if self.is_reading:
            messagebox.showinfo("Info", "Already reading.")
            return

        self.is_reading = True
        self.stop_flag.clear()
        self.reading_thread = threading.Thread(target=self.read_sentences, daemon=True)
        self.reading_thread.start()

    def read_from_start(self):
        if not self.sentences:
            messagebox.showinfo("Info", "Please open a book first.")
            return
        if self.is_reading:
            messagebox.showinfo("Info", "Already reading.")
            return

        self.current_sentence_index = 0
        self.current_word_index = 0
        self.progress['value'] = 0
        self.start_reading()

    def read_sentences(self):
        self.engine.setProperty('rate', self.speed_var.get())
        self.engine.setProperty('volume', self.volume_var.get())

        batch_size = 1
        sentence_idx = self.current_sentence_index
        word_idx = self.current_word_index

        while sentence_idx < len(self.sentences) and not self.stop_flag.is_set():
            sentence = self.sentences[sentence_idx]
            self.root.after(0, self.highlight_sentence, sentence)
            words = sentence.split()

            for i in range(word_idx, len(words), batch_size):
                if self.stop_flag.is_set():
                    self.current_sentence_index = sentence_idx
                    self.current_word_index = i
                    self.save_position(self.book_path, self.current_sentence_index, self.current_word_index)
                    return

                chunk = " ".join(words[i:i + batch_size])
                self.engine.say(chunk)
                self.engine.runAndWait()

                self.current_sentence_index = sentence_idx
                self.current_word_index = i + batch_size
                self.save_position(self.book_path, self.current_sentence_index, self.current_word_index)
                self.root.after(0, self.update_progress, sentence_idx + 1)

            sentence_idx += 1
            word_idx = 0

        self.current_sentence_index = 0
        self.current_word_index = 0
        self.save_position(self.book_path, 0, 0)
        self.root.after(0, self.remove_highlight)
        self.root.after(0, self.update_progress, 0)
        self.is_reading = False

    def highlight_sentence(self, sentence):
        self.text_display.tag_remove("highlight", "1.0", tk.END)
        idx = self.text_display.search(sentence, "1.0", tk.END)
        if idx:
            end_idx = f"{idx}+{len(sentence)}c"
            self.text_display.tag_add("highlight", idx, end_idx)
            self.text_display.tag_config("highlight", background="grey")
            self.text_display.see(idx)

    def remove_highlight(self):
        self.text_display.tag_remove("highlight", "1.0", tk.END)

    def update_progress(self, value):
        self.progress['value'] = value

    def stop_reading(self):
        if not self.is_reading:
            messagebox.showinfo("Info", "Not currently reading.")
            return
        self.stop_flag.set()
        self.engine.stop()
        if self.reading_thread and self.reading_thread.is_alive():
            self.reading_thread.join(timeout=2)
        self.is_reading = False

    def increase_font_size(self):
        self.font_size += 2
        self.text_display.config(font=("Arial", self.font_size))

    def decrease_font_size(self):
        if self.font_size > 8:
            self.font_size -= 2
            self.text_display.config(font=("Arial", self.font_size))

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#2e2e2e" if self.dark_mode else "white"
        fg = "white" if self.dark_mode else "black"
        self.text_display.config(bg=bg, fg=fg)

    def update_speed(self, event=None):
        self.engine.setProperty('rate', self.speed_var.get())

    def update_volume(self, event=None):
        self.engine.setProperty('volume', self.volume_var.get())

    def save_position(self, book_path, sentence_idx, word_idx):
        if not book_path:
            return
        data = {}
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        data[book_path] = {"sentence": sentence_idx, "word": word_idx}
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load_position_for_book(self, book_path):
        if not os.path.exists(SAVE_FILE):
            return 0, 0
        with open(SAVE_FILE, "r") as f:
            try:
                data = json.load(f)
                pos = data.get(book_path, {"sentence": 0, "word": 0})
                return pos.get("sentence", 0), pos.get("word", 0)
            except json.JSONDecodeError:
                return 0, 0

    def on_close(self):
        self.save_position(self.book_path, self.current_sentence_index, self.current_word_index)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartBookReaderApp(root)
    root.mainloop()
