"""
Fenêtre principale de l'application
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .styles import AppStyles
from .widgets import (
    ControlFrame, StyledButton, FileInfoFrame,
    StyledProgressBar, CompressionInfoLabel
)
from .controllers import AudioController


class AudioCompressorWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Audio Compressor")
        self.setPalette(AppStyles.get_dark_palette())
        
        # Contrôleur
        self.controller = AudioController()
        self._connect_controller_signals()
        
        # UI
        self._setup_ui()
        
        # État initial
        self.showMaximized()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Header
        main_layout.addLayout(self._create_header())
        
        # Sélection de fichier
        self.file_frame = FileInfoFrame()
        self.file_frame.browse_button.clicked.connect(
            lambda: self.controller.browse_file(self)
        )
        main_layout.addWidget(self.file_frame)
        
        # Contrôles
        main_layout.addLayout(self._create_controls())
        
        # Barre de progression
        self.progress_bar = StyledProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # Informations de compression
        self.info_label = CompressionInfoLabel()
        main_layout.addWidget(self.info_label)
        
        # Spacer
        main_layout.addStretch()
    
    def _create_header(self) -> QHBoxLayout:
        """Crée le header avec le titre"""
        header_layout = QHBoxLayout()
        
        title_label = QLabel("AUDIO COMPRESSOR")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        return header_layout
    
    def _create_controls(self) -> QHBoxLayout:
        """Crée les contrôles principaux"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        # Audio original
        self.original_frame = ControlFrame("ORIGINAL AUDIO")
        self.play_original_btn = StyledButton("PLAY", AppStyles.COLORS['success'])
        self.play_original_btn.clicked.connect(self.controller.play_original)
        self.original_frame.add_button(self.play_original_btn)
        
        # Compression
        self.compress_frame = ControlFrame("COMPRESSION")
        self.compress_btn = StyledButton("COMPRESS", AppStyles.COLORS['danger'])
        self.compress_btn.clicked.connect(lambda: self.controller.compress_file(self))
        self.compress_frame.add_button(self.compress_btn)
        
        # Audio compressé
        self.compressed_frame = ControlFrame("COMPRESSED AUDIO")
        self.play_compressed_btn = StyledButton("PLAY", AppStyles.COLORS['info'])
        self.play_compressed_btn.clicked.connect(
            lambda: self.controller.decompress_and_play(self)
        )
        self.compressed_frame.add_button(self.play_compressed_btn)
        
        controls_layout.addWidget(self.original_frame)
        controls_layout.addWidget(self.compress_frame)
        controls_layout.addWidget(self.compressed_frame)
        
        return controls_layout
    
    def _connect_controller_signals(self):
        """Connecte les signaux du contrôleur"""
        self.controller.file_selected.connect(self._on_file_selected)
        self.controller.compression_started.connect(self._on_compression_started)
        self.controller.compression_progress.connect(self._on_compression_progress)
        self.controller.compression_finished.connect(self._on_compression_finished)
        self.controller.compression_error.connect(self._on_compression_error)
        self.controller.decompression_finished.connect(self._on_decompression_finished)
    
    def _on_file_selected(self, filename: str):
        """Callback: fichier sélectionné"""
        self.file_frame.set_file_name(filename)
        self.progress_bar.setValue(100)
        self.info_label.clear_message()
    
    def _on_compression_started(self):
        """Callback: compression démarrée"""
        self.progress_bar.reset()
        self.info_label.clear_message()
    
    def _on_compression_progress(self, value: int):
        """Callback: progression de la compression"""
        self.progress_bar.setValue(value)
    
    def _on_compression_finished(self, rate: float):
        """Callback: compression terminée"""
        self.progress_bar.setValue(100)
        self.info_label.show_compression_rate(rate)
    
    def _on_compression_error(self, message: str):
        """Callback: erreur de compression"""
        self.info_label.show_error(message)
    
    def _on_decompression_finished(self, filename: str):
        """Callback: décompression terminée"""
        self.info_label.show_success(f"Lecture de {filename}")
    
    def keyPressEvent(self, event):
        """Gère les événements clavier"""
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Nettoyage avant fermeture"""
        self.controller.cleanup()
        super().closeEvent(event)