import sys
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog,
    QPushButton, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from ebooklib import epub
from bs4 import BeautifulSoup


class CustomWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()
        if url_str.startswith("http"):
            webbrowser.open(url_str)  # Open external links in default browser
            return False
        elif "#" in url_str:
            anchor = url_str.split("#")[-1]
            self.parent().scroll_to_anchor(anchor)
            return False
        return True


class EPUBViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPUB Viewer")
        self.setGeometry(100, 100, 1000, 700)

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebPage(self.browser))
        self.next_button = QPushButton("Next")
        self.prev_button = QPushButton("Previous")
        self.next_button.clicked.connect(self.next_page)
        self.prev_button.clicked.connect(self.prev_page)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.browser)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.current_index = 0
        self.pages = []

        self.load_epub()

    def load_epub(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open EPUB File", "", "EPUB Files (*.epub)")
        if not file_path:
            return

        book = epub.read_epub(file_path)

        # Load content from the spine (in reading order)
        for item in book.spine:
            idref = item[0]
            doc = book.get_item_with_id(idref)
            if doc:
                soup = BeautifulSoup(doc.get_content(), 'html.parser')
                body = soup.body
                if body:
                    self.pages.append(str(body))

        if not self.pages:
            self.pages = ["<body><p>No readable pages found.</p></body>"]

        self.display_page()

    def display_page(self):
        content = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Georgia', serif;
                        line-height: 1.6;
                        padding: 40px;
                        font-size: 18px;
                        background-color: #fefefe;
                        color: #333;
                        max-width: 800px;
                        margin: auto;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    a {{
                        color: #0645AD;
                        text-decoration: underline;
                        cursor: pointer;
                    }}
                </style>
                <script>
                    document.addEventListener('DOMContentLoaded', function() {{
                        document.querySelectorAll('a').forEach(function(link) {{
                            link.addEventListener('click', function(e) {{
                                e.preventDefault();
                                window.location.href = link.getAttribute('href');
                            }});
                        }});
                    }});
                </script>
            </head>
            {self.pages[self.current_index]}
        </html>
        """
        self.browser.setHtml(content, QUrl(""))

    def next_page(self):
        if self.current_index < len(self.pages) - 1:
            self.current_index += 1
            self.display_page()

    def prev_page(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_page()

    def scroll_to_anchor(self, anchor):
        js = f"""
            var el = document.getElementById("{anchor}");
            if (el) el.scrollIntoView({{ behavior: 'smooth' }});
        """
        self.browser.page().runJavaScript(js)


# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = EPUBViewer()
    viewer.show()
    sys.exit(app.exec_())
