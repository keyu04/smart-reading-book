import unittest
import os
import time
import tkinter as tk
from index import SmartBookReaderApp  # your main app class
from unittest.mock import patch

SAVE_FILE = "last_read_position.json"

class TestSmartBookReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the main window during tests

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.app = SmartBookReaderApp(self.root)
        self.test_book_path = "test_book.txt"

        with open(self.test_book_path, "w", encoding="utf-8") as f:
            f.write("Hello world. This is a test book. Let's read!")

        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    def tearDown(self):
        if os.path.exists(self.test_book_path):
            os.remove(self.test_book_path)
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    def test_load_book_and_split_sentences(self):
        self.app.load_book(self.test_book_path)
        self.assertEqual(len(self.app.sentences), 3)

    def test_save_and_load_position(self):
        self.app.save_position(self.test_book_path, 2, 3)
        pos = self.app.load_position_for_book(self.test_book_path)
        self.assertEqual(pos, (2, 3))

    def test_start_and_stop_reading(self):
        self.app.load_book(self.test_book_path)
        self.app.start_reading()
        self.assertTrue(self.app.is_reading)

        self.app.stop_reading()
        self.assertFalse(self.app.is_reading)

    def test_speed_and_volume_controls(self):
        self.app.speed_var.set(180)
        self.app.update_speed()

        self.app.volume_var.set(0.5)
        self.app.update_volume()

        self.assertEqual(self.app.engine.getProperty('rate'), 180)
        self.assertAlmostEqual(self.app.engine.getProperty('volume'), 0.5, places=1)

    def test_font_size_controls(self):
        initial_size = self.app.font_size
        self.app.increase_font_size()
        self.assertGreater(self.app.font_size, initial_size)
        self.app.decrease_font_size()
        self.assertEqual(self.app.font_size, initial_size)

    def test_toggle_dark_mode(self):
        initial_mode = self.app.dark_mode
        self.app.toggle_mode()
        self.assertNotEqual(self.app.dark_mode, initial_mode)

    def test_highlight_and_remove_highlight(self):
        self.app.load_book(self.test_book_path)
        sentence = self.app.sentences[0]
        self.app.highlight_sentence(sentence)
        self.assertIn("highlight", self.app.text_display.tag_names())

        self.app.remove_highlight()
        self.assertEqual(self.app.text_display.tag_ranges("highlight"), ())

if __name__ == "__main__":
    unittest.main()
