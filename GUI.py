import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                              QHBoxLayout, QFileDialog, QLabel, QWidget,
                              QFrame, QProgressBar)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QFont, QColor, QPalette
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import matplotlib.pyplot as plt
from stereotreatment import *
from AsciiQuantif import *
from support import *
from mehdi_compression import *

class AudioCompressorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Audio Compressor")
        
        # Set dark theme
        self.apply_dark_theme()
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.showMaximized()  # This line sets the window to maximized size
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("AUDIO COMPRESSOR")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add file selection area
        file_frame = QFrame()
        file_frame.setFrameShape(QFrame.Shape.StyledPanel)
        file_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        file_layout = QHBoxLayout(file_frame)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Segoe UI", 10))
        self.file_label.setStyleSheet("color: #aaaaaa;")
        
        browse_button = QPushButton("SELECT AUDIO")
        browse_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_button.setMinimumHeight(40)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6aa5;
            }
        """)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(browse_button)
        
        
       
        
        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        # Original audio controls
        original_frame = self.create_control_frame("ORIGINAL AUDIO")
        original_controls = QHBoxLayout()
        
        play_original_btn = self.create_button("PLAY", "#27ae60")
        
        original_controls.addWidget(play_original_btn)
        original_frame.layout().addLayout(original_controls)
        
        # Compression controls
        compress_frame = self.create_control_frame("COMPRESSION")
        compress_controls = QHBoxLayout()
        
        compress_btn = self.create_button("COMPRESS", "#e74c3c")
        
        compress_controls.addWidget(compress_btn)
        compress_frame.layout().addLayout(compress_controls)
        
        # Compressed audio controls
        compressed_frame = self.create_control_frame("COMPRESSED AUDIO")
        compressed_controls = QHBoxLayout()
        
        play_compressed_btn = self.create_button("PLAY", "#9b59b6")
        
        
        compressed_controls.addWidget(play_compressed_btn)
        
        compressed_frame.layout().addLayout(compressed_controls)
        
        # Add all frames to controls layout
        controls_layout.addWidget(original_frame)
        controls_layout.addWidget(compress_frame)
        controls_layout.addWidget(compressed_frame)
        
        # Add all components to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(file_frame)
    
        main_layout.addLayout(controls_layout)
        
        # Initialize media player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Connect signals and slots
        browse_button.clicked.connect(self.browse_file)
        play_original_btn.clicked.connect(lambda: self.play_audio("original"))
        compress_btn.clicked.connect(self.compress_audio)
        play_compressed_btn.clicked.connect(lambda: self.play_audio("compressed"))
        
        # Initialize variables
        self.original_audio_path = None
        self.compressed_audio_path = None
        
        # Set fullscreen mode
        self.showFullScreen()
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(33, 33, 33))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        self.setPalette(palette)
    
    def create_control_frame(self, title):
        """Create a styled frame for controls with title"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        
        return frame
    
    def create_button(self, text, color):
        """Create a styled button with given text and color"""
        button = QPushButton(text)
        button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(40)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {color}cc;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """)
        return button
    
    def browse_file(self):
        """Open file dialog to select audio file"""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Audio Files (*.mp3 *.wav *.ogg *.flac)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.original_audio_path = selected_files[0]
                file_name = Path(self.original_audio_path).name
                self.file_label.setText(file_name)
                self.compressed_audio_path = None
                
                # Simulate loading the file
                for i in range(101):
                    self.progress_bar.setValue(i)
                    QApplication.processEvents()
                    # In a real app, you'd update this based on actual loading progress
    
    def play_audio(self, audio_type):
        """Play the selected audio (original or compressed)"""
        if audio_type == "original" and self.original_audio_path:
            self.player.setSource(QUrl.fromLocalFile(self.original_audio_path))
            self.player.play()
        elif audio_type == "compressed" and self.compressed_audio_path:
            self.player.setSource(QUrl.fromLocalFile(self.compressed_audio_path))
            self.player.play()
    
    def compress_audio(self):
        """Effectuer une vraie compression et sauvegarder le fichier"""
        if self.original_audio_path:
        # Boîte de dialogue pour choisir l'emplacement du fichier compressé
            save_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier compressé", "", "Fichiers Binaires (*.bin)")
        if not save_path:
            return  # L'utilisateur a annulé

        # Simulation de la progression
        self.progress_bar.setValue(0)
        QApplication.processEvents()

        try:
            # Appel de la vraie fonction de compression
            compression(self.original_audio_path, save_path)

            # Mise à jour de la barre de progression (simple simulation ici)
            for i in range(1, 101):
                self.progress_bar.setValue(i)
                QApplication.processEvents()

            # Mise à jour de l'étiquette
            self.file_label.setText(f"Fichier compressé enregistré : {Path(save_path).name}")
            self.compressed_audio_path = save_path

        except Exception as e:
            self.file_label.setText(f"Erreur : {e}")
    
    def save_audio(self):
        """Save the compressed audio file"""
        if self.compressed_audio_path:
            save_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Compressed Audio", 
                str(Path(self.compressed_audio_path)), 
                "Audio Files (*.mp3 *.wav *.ogg *.flac)"
            )
            
            if save_path:
                # In a real application, you would actually save the file here
                # For this demo, we just pretend it worked
                self.file_label.setText(f"Saved as: {Path(save_path).name}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Add ability to exit fullscreen with Escape key
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent cross-platform look
    
    window = AudioCompressorApp()
    window.show()
    
    sys.exit(app.exec())