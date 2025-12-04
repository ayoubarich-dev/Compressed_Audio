"""
Fenêtre principale de l'application avec visualisations
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from .styles import AppStyles
from .widgets import (
    ControlFrame, StyledButton, FileInfoFrame,
    StyledProgressBar, CompressionInfoLabel
)
from .visualization_widget import VisualizationFrame
from .controllers import AudioController


class AudioCompressorWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Audio Compressor - Avec Visualisations")
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
        # Widget principal avec scroll
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        main_layout.addLayout(self._create_header())
        
        # Container avec deux colonnes
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Colonne gauche - Contrôles
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        # Sélection de fichier
        self.file_frame = FileInfoFrame()
        self.file_frame.browse_button.clicked.connect(
            lambda: self.controller.browse_file(self)
        )
        left_column.addWidget(self.file_frame)
        
        # Contrôles
        left_column.addLayout(self._create_controls())
        
        # Barre de progression
        self.progress_bar = StyledProgressBar()
        left_column.addWidget(self.progress_bar)
        
        # Informations de compression
        self.info_label = CompressionInfoLabel()
        left_column.addWidget(self.info_label)
        
        left_column.addStretch()
        
        # Colonne droite - Visualisations
        self.viz_frame = VisualizationFrame()
        
        # Ajout des colonnes
        content_layout.addLayout(left_column, 1)  # 1/3 de l'espace
        content_layout.addWidget(self.viz_frame, 2)  # 2/3 de l'espace
        
        main_layout.addLayout(content_layout)
    
    def _create_header(self) -> QHBoxLayout:
        """Crée le header avec le titre"""
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎵 AUDIO COMPRESSOR")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0;")
        
        subtitle_label = QLabel("Compression avec visualisation en temps réel")
        subtitle_label.setFont(QFont("Segoe UI", 9))
        subtitle_label.setStyleSheet("color: #888888;")
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        
        return header_layout
    
    def _create_controls(self) -> QVBoxLayout:
        """Crée les contrôles principaux"""
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        
        # Audio original
        self.original_frame = ControlFrame("ORIGINAL AUDIO")
        self.play_original_btn = StyledButton("▶ PLAY ORIGINAL", AppStyles.COLORS['success'])
        self.play_original_btn.clicked.connect(self.controller.play_original)
        self.original_frame.add_button(self.play_original_btn)
        
        # Compression
        self.compress_frame = ControlFrame("COMPRESSION")
        self.compress_btn = StyledButton("🗜️ COMPRESS", AppStyles.COLORS['danger'])
        self.compress_btn.clicked.connect(lambda: self.controller.compress_file(self))
        self.compress_frame.add_button(self.compress_btn)
        
        # Audio compressé
        self.compressed_frame = ControlFrame("COMPRESSED AUDIO")
        self.play_compressed_btn = StyledButton("▶ PLAY COMPRESSED", AppStyles.COLORS['info'])
        self.play_compressed_btn.clicked.connect(
            lambda: self.controller.decompress_and_play(self)
        )
        self.compressed_frame.add_button(self.play_compressed_btn)
        
        # Arrêt
        self.stop_frame = ControlFrame("PLAYBACK")
        self.stop_btn = StyledButton("⏹ STOP", AppStyles.COLORS['gray'])
        self.stop_btn.clicked.connect(self.controller.stop_playback)
        self.stop_frame.add_button(self.stop_btn)
        
        controls_layout.addWidget(self.original_frame)
        controls_layout.addWidget(self.compress_frame)
        controls_layout.addWidget(self.compressed_frame)
        controls_layout.addWidget(self.stop_frame)
        
        return controls_layout
    
    def _connect_controller_signals(self):
        """Connecte les signaux du contrôleur"""
        self.controller.file_selected.connect(self._on_file_selected)
        self.controller.compression_started.connect(self._on_compression_started)
        self.controller.compression_progress.connect(self._on_compression_progress)
        self.controller.compression_finished.connect(self._on_compression_finished)
        self.controller.compression_error.connect(self._on_compression_error)
        self.controller.decompression_finished.connect(self._on_decompression_finished)
        
        # Signaux de visualisation
        self.controller.original_audio_loaded.connect(self._on_original_loaded)
        self.controller.compressed_audio_loaded.connect(self._on_compressed_loaded)
        self.controller.metrics_updated.connect(self._on_metrics_updated)
    
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
    
    def _on_original_loaded(self, audio_segment):
        """Callback: audio original chargé"""
        self.viz_frame.set_original_audio(audio_segment)
    
    def _on_compressed_loaded(self, audio_segment):
        """Callback: audio compressé chargé"""
        self.viz_frame.set_compressed_audio(audio_segment)
    
    def _on_metrics_updated(self, original_info, compressed_info, reduction_rate):
        """Callback: métriques mises à jour"""
        self.viz_frame.update_metrics(original_info, compressed_info, reduction_rate)
    
    def keyPressEvent(self, event):
        """Gère les événements clavier"""
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
        elif event.key() == Qt.Key.Key_Space:
            self.controller.stop_playback()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Nettoyage avant fermeture"""
        self.controller.cleanup()
        super().closeEvent(event)