"""
Fenêtre principale de l'application avec design optimisé
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
    """Fenêtre principale optimisée"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Audio Compressor Pro")
        self.setPalette(AppStyles.get_dark_palette())
        
        # Contrôleur
        self.controller = AudioController()
        self._connect_controller_signals()
        
        # UI
        self._setup_ui()
        
        # Taille fixe pour éviter débordement
        self.resize(1200, 700)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur compacte"""
        # Widget principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setCentralWidget(scroll)
        
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # Header compact
        main_layout.addLayout(self._create_header())
        
        # Container avec deux colonnes
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        # Colonne gauche - Contrôles (35%)
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        
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
        
        # Colonne droite - Visualisations (65%)
        self.viz_frame = VisualizationFrame()
        
        # Ajout des colonnes
        content_layout.addLayout(left_column, 35)
        content_layout.addWidget(self.viz_frame, 65)
        
        main_layout.addLayout(content_layout)
    
    def _create_header(self) -> QHBoxLayout:
        """Crée le header compact"""
        header_layout = QHBoxLayout()
        
        # Titre principal
        title_label = QLabel("🎵 AUDIO COMPRESSOR")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3498db;")
        
        # Sous-titre
        subtitle_label = QLabel("Compression intelligente")
        subtitle_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Light))
        subtitle_label.setStyleSheet("color: #888888;")
        
        # Badge version
        version_label = QLabel("v2.0")
        version_label.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        version_label.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 8px;
        """)
        
        left_layout = QVBoxLayout()
        left_layout.setSpacing(2)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        header_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignTop)
        
        return header_layout
    
    def _create_controls(self) -> QVBoxLayout:
        """Crée les contrôles compacts"""
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)
        
        # Audio original
        self.original_frame = ControlFrame("🎵 ORIGINAL")
        self.play_original_btn = StyledButton("▶ ÉCOUTER", AppStyles.COLORS['success'])
        self.play_original_btn.clicked.connect(self.controller.play_original)
        self.original_frame.add_button(self.play_original_btn)
        
        # Compression
        self.compress_frame = ControlFrame("🗜️ COMPRESSION")
        self.compress_btn = StyledButton("COMPRESSER", AppStyles.COLORS['danger'])
        self.compress_btn.clicked.connect(lambda: self.controller.compress_file(self))
        self.compress_frame.add_button(self.compress_btn)
        
        # Audio compressé
        self.compressed_frame = ControlFrame("🎧 COMPRESSÉ")
        self.play_compressed_btn = StyledButton("▶ ÉCOUTER", AppStyles.COLORS['info'])
        self.play_compressed_btn.clicked.connect(
            lambda: self.controller.decompress_and_play(self)
        )
        self.compressed_frame.add_button(self.play_compressed_btn)
        
        # Arrêt
        self.stop_frame = ControlFrame("⏹️ CONTRÔLE")
        self.stop_btn = StyledButton("ARRÊTER", AppStyles.COLORS['gray'])
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
        print(f"[DEBUG] Fichier sélectionné: {filename}")
        self.file_frame.set_file_name(filename)
        self.progress_bar.setValue(100)
        self.info_label.clear_message()
    
    def _on_compression_started(self):
        """Callback: compression démarrée"""
        print("[DEBUG] Compression démarrée")
        self.progress_bar.reset()
        self.info_label.clear_message()
    
    def _on_compression_progress(self, value: int):
        """Callback: progression de la compression"""
        self.progress_bar.setValue(value)
    
    def _on_compression_finished(self, rate: float):
        """Callback: compression terminée"""
        print(f"[DEBUG] Compression terminée: {rate}%")
        self.progress_bar.setValue(100)
        self.info_label.show_compression_rate(rate)
    
    def _on_compression_error(self, message: str):
        """Callback: erreur de compression"""
        print(f"[DEBUG] Erreur: {message}")
        self.info_label.show_error(message)
    
    def _on_decompression_finished(self, filename: str):
        """Callback: décompression terminée"""
        print(f"[DEBUG] Décompression terminée: {filename}")
        self.info_label.show_success(f"Lecture de {filename}")
    
    def _on_original_loaded(self, audio_segment):
        """Callback: audio original chargé"""
        print("[DEBUG] Callback: Audio original chargé")
        self.viz_frame.set_original_audio(audio_segment)
    
    def _on_compressed_loaded(self, audio_segment):
        """Callback: audio compressé chargé"""
        print("[DEBUG] Callback: Audio compressé chargé")
        self.viz_frame.set_compressed_audio(audio_segment)
    
    def _on_metrics_updated(self, original_info, compressed_info, reduction_rate):
        """Callback: métriques mises à jour"""
        print("[DEBUG] Callback: Métriques mises à jour")
        print(f"  Original info: {original_info}")
        print(f"  Compressed info: {compressed_info}")
        print(f"  Reduction rate: {reduction_rate}")
        self.viz_frame.update_metrics(original_info, compressed_info, reduction_rate)
    
    def keyPressEvent(self, event):
        """Gère les événements clavier"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Space:
            self.controller.stop_playback()
        elif event.key() == Qt.Key.Key_F11:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Nettoyage avant fermeture"""
        self.controller.cleanup()
        super().closeEvent(event)