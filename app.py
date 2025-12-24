import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                               QTextEdit, QProgressBar, QFileDialog, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from backend import OrganizerWorker

# --- Constants & Theme Config ---
FONT_FAMILY = "Fira Code"
COLOR_BG_MAIN = "#343541"
COLOR_BG_SIDEBAR = "#202123"
COLOR_BTN_PRIMARY = "#ffffff"
COLOR_BTN_HOVER = "#d9d9e3"
COLOR_TEXT_PRIMARY = "#ececf1"
COLOR_TEXT_SECONDARY = "#acacbe"
COLOR_BORDER = "#565869"
CORNER_RADIUS = "8px"

# --- Stylesheet (QSS) ---
STYLESHEET = f"""
QMainWindow {{
    background-color: {COLOR_BG_MAIN};
}}
QWidget {{
    font-family: "{FONT_FAMILY}", monospace;
    font-size: 14px;
    color: {COLOR_TEXT_PRIMARY};
}}
/* Sidebar */
QFrame#Sidebar {{
    background-color: {COLOR_BG_SIDEBAR};
    border-right: 1px solid #2d2d30;
}}
QPushButton#SidebarBtn {{
    text-align: left;
    padding-left: 15px;
    border: none;
    background-color: transparent;
    color: {COLOR_TEXT_SECONDARY};
    border-radius: 6px;
    font-size: 13px;
}}
QPushButton#SidebarBtn:hover {{
    background-color: #2a2b32;
    color: {COLOR_TEXT_PRIMARY};
}}
QPushButton#SidebarBtn:checked {{
    background-color: #343541;
    color: {COLOR_TEXT_PRIMARY};
    font-weight: bold;
}}
/* Main Content */
QLineEdit {{
    background-color: #40414f;
    border: 1px solid {COLOR_BORDER};
    border-radius: {CORNER_RADIUS};
    padding: 8px;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: #10a37f;
}}
QPushButton#ActionBtn {{
    background-color: #40414f;
    border: none;
    border-radius: {CORNER_RADIUS};
    padding: 8px 16px;
    color: {COLOR_TEXT_PRIMARY};
    font-weight: bold;
}}
QPushButton#ActionBtn:hover {{
    background-color: #565869;
}}
QPushButton#StartBtn {{
    background-color: {COLOR_BTN_PRIMARY};
    color: #000000;
    border-radius: {CORNER_RADIUS};
    padding: 12px;
    font-weight: bold;
    font-size: 14px;
}}
QPushButton#StartBtn:hover {{
    background-color: {COLOR_BTN_HOVER};
}}
QPushButton#StartBtn:disabled {{
    background-color: #565869;
    color: #acacbe;
}}
QProgressBar {{
    border: none;
    background-color: #40414f;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {COLOR_BTN_PRIMARY};
    border-radius: 4px;
}}
QTextEdit {{
    background-color: #40414f;
    border: 1px solid {COLOR_BORDER};
    border-radius: {CORNER_RADIUS};
    color: #d1d5db;
    padding: 10px;
    font-family: "{FONT_FAMILY}", monospace;
    font-size: 12px;
}}
/* Stats Labels */
QLabel#StatLabel {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: 11px;
}}
QLabel#StatValue {{
    color: {COLOR_TEXT_PRIMARY};
    font-size: 13px;
    font-weight: bold;
}}
"""

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synaptiq")
        self.resize(1000, 550)
        
        self.selected_path = "Select a folder to organize"
        self.current_mode = "ai" # Default
        self.worker = None
        self.last_log_was_progress = False

        self.init_ui()
        self.setup_styles()

    def setup_styles(self):
        self.setStyleSheet(STYLESHEET)

    def init_ui(self):
        # Main Layout Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(10)

        # Logo / Header
        title_lbl = QLabel("SYNAPTIQ - FILE ORGANIZER")
        title_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        
        sidebar_layout.addWidget(title_lbl)
        title_lbl.setContentsMargins(3, 0, 0, 0)  # Align 10px from left

        # Strategy Navigation
        nav_lbl = QLabel("STRATEGY")
        nav_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLOR_TEXT_SECONDARY}; margin-top: 10px;")
        sidebar_layout.addWidget(nav_lbl)

        self.btn_ai = self.create_sidebar_btn("  > AI SEMANTIC CLUSTER", "ai")
        self.btn_ai.setChecked(True) # Default
        self.btn_ext = self.create_sidebar_btn("  > FILE EXTENSION", "type")
        self.btn_date = self.create_sidebar_btn("  > DATE MODIFIED", "date")

        sidebar_layout.addWidget(self.btn_ai)
        sidebar_layout.addWidget(self.btn_ext)
        sidebar_layout.addWidget(self.btn_date)

        sidebar_layout.addStretch()

        # Stats Panel (Bottom of Sidebar)
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(5)

        self.lbl_total_val = self.add_stat_row(stats_layout, "TOTAL FILES", "0")
        self.lbl_proc_val = self.add_stat_row(stats_layout, "PROCESSED", "0")
        self.lbl_group_val = self.add_stat_row(stats_layout, "GROUPS", "0")

        sidebar_layout.addWidget(stats_container)
        main_layout.addWidget(self.sidebar)

        # --- Content Area ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)

        # Path Selection
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.selected_path)
        self.path_input.setReadOnly(True)
        self.path_input.setFixedHeight(45)
        
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.setObjectName("ActionBtn")
        self.browse_btn.setCursor(Qt.PointingHandCursor) # type: ignore
        self.browse_btn.setFixedHeight(45)
        self.browse_btn.clicked.connect(self.browse_folder)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        content_layout.addLayout(path_layout)

        # Description / Status
        self.desc_label = QLabel("Ready to cluster documents using local LLM.")
        self.desc_label.setAlignment(Qt.AlignCenter) # type: ignore
        self.desc_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; margin-top: 10px;")
        content_layout.addWidget(self.desc_label)

        # Start Button
        self.start_btn = QPushButton("START ORGANIZATION")
        self.start_btn.setObjectName("StartBtn")
        self.start_btn.setCursor(Qt.PointingHandCursor) # type: ignore
        self.start_btn.setFixedWidth(250)
        self.start_btn.clicked.connect(self.start_process)
        
        # Center the button
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.start_btn)
        btn_container.addStretch()
        content_layout.addLayout(btn_container)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # --- MODIFICATION: Hide initially ---
        self.progress_bar.setVisible(False) 
        
        content_layout.addWidget(self.progress_bar)

        # Console Output
        console_lbl = QLabel("CONSOLE OUTPUT")
        console_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLOR_TEXT_SECONDARY}; margin-top: 20px;")
        content_layout.addWidget(console_lbl)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        content_layout.addWidget(self.console)

        main_layout.addWidget(content_area)

    def create_sidebar_btn(self, text, mode):
        btn = QPushButton(text)
        btn.setObjectName("SidebarBtn")
        btn.setCursor(Qt.PointingHandCursor) # type: ignore
        btn.setCheckable(True)
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: self.change_mode(btn, mode))
        return btn

    def add_stat_row(self, layout, title, value):
        row = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setObjectName("StatLabel")
        lbl_val = QLabel(value)
        lbl_val.setObjectName("StatValue")
        row.addWidget(lbl_title)
        row.addStretch()
        row.addWidget(lbl_val)
        layout.addLayout(row)
        return lbl_val

    def change_mode(self, sender, mode):
        # Logic to ensure exclusive checking visuals
        self.btn_ai.setChecked(False)
        self.btn_ext.setChecked(False)
        self.btn_date.setChecked(False)
        sender.setChecked(True)
        
        self.current_mode = mode
        
        descriptions = {
            "ai": "Ready to cluster documents using local LLM.",
            "type": "Ready to group files into folders based on extensions (PDF, JPG, etc).",
            "date": "Ready to organize files chronologically by Year-Month."
        }
        self.desc_label.setText(descriptions.get(mode, ""))

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_path = folder
            self.path_input.setText(folder)
            self.log_message(f"Selected target: {folder}")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        
        # Check if this is a download progress message
        is_progress = "Downloading:" in message
        
        # Get the cursor from the console text edit
        cursor = self.console.textCursor()
        
        # Move to the end of the document
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if self.last_log_was_progress and is_progress:
            # Select the text from End back to StartOfBlock to overwrite it
            cursor.movePosition(
                QTextCursor.MoveOperation.StartOfBlock, 
                QTextCursor.MoveMode.KeepAnchor
            )
            cursor.removeSelectedText()
            cursor.insertText(formatted_msg)
        else:
            # Standard append (creates new line)
            self.console.append(formatted_msg)

        # Update state
        self.last_log_was_progress = is_progress

        # Auto scroll
        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_process(self):
        if self.selected_path == "Select a folder to organize" or not os.path.exists(self.selected_path):
            self.log_message("Error: Invalid directory selected.")
            return

        # UI State
        self.start_btn.setEnabled(False)
        self.start_btn.setText("PROCESSING...")
        
        # --- MODIFICATION: Show progress bar when starting ---
        self.progress_bar.setVisible(True)
        
        self.console.clear()
        self.progress_bar.setValue(0)
        self.reset_stats()

        # Start Worker
        self.worker = OrganizerWorker(self.selected_path, self.current_mode)
        self.worker.log_signal.connect(self.log_message)
        self.worker.progress_signal.connect(lambda p: self.progress_bar.setValue(int(p * 100)))
        self.worker.stats_signal.connect(self.update_stats)
        self.worker.finished_signal.connect(self.on_process_finished)
        self.worker.error_signal.connect(self.on_process_error)
        self.worker.start()

    def update_stats(self, total, processed, groups):
        self.lbl_total_val.setText(str(total))
        self.lbl_proc_val.setText(str(processed))
        self.lbl_group_val.setText(str(groups))

    def reset_stats(self):
        self.update_stats(0, 0, 0)

    def on_process_finished(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("START ORGANIZATION")
        self.log_message("Done.")

    def on_process_error(self, msg):
        self.log_message(f"ERROR: {msg}")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("START ORGANIZATION")

    def closeEvent(self, event):
        """
        Handle application closure.
        Stop the worker thread gracefully before exiting to prevent crashes
        and lingering background processes.
        """
        if self.worker and self.worker.isRunning():
            self.log_message("Stopping active processes... Please wait.")
            
            # 1. Signal the thread to stop (sets is_running = False)
            self.worker.stop()
            
            # 2. Block the window closing until the thread finishes (Clean Exit)
            # This prevents "QThread Destroyed while thread is running"
            self.worker.wait()
        
        # 3. Accept the close event (Kill the app)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load Font (Optional: Falls back to system monospace if not found)
    font_db = QFont(FONT_FAMILY)
    font_db.setStyleHint(QFont.Monospace) # type: ignore
    app.setFont(font_db)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

