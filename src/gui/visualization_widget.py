"""
Widget de visualisation pour comparer l'audio original et compressé
"""

import numpy as np
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QPen, QColor
from pydub import AudioSegment


class WaveformWidget(QWidget):
    """Widget pour afficher une forme d'onde"""
    
    def __init__(self, title: str, color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = QColor(color)
        self.samples = None
        self.setMinimumHeight(120)
        
    def set_audio_data(self, audio_segment: AudioSegment):
        """
        Charge les données audio
        
        Args:
            audio_segment: Segment audio à afficher
        """
        samples = np.array(audio_segment.get_array_of_samples())
        
        # Sous-échantillonnage pour la visualisation (max 2000 points)
        if len(samples) > 2000:
            step = len(samples) // 2000
            self.samples = samples[::step]
        else:
            self.samples = samples
            
        # Normalisation pour l'affichage
        if len(self.samples) > 0:
            max_val = np.max(np.abs(self.samples))
            if max_val > 0:
                self.samples = self.samples / max_val
        
        self.update()
    
    def clear(self):
        """Efface les données"""
        self.samples = None
        self.update()
    
    def paintEvent(self, event):
        """Dessine la forme d'onde"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fond
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        # Titre
        painter.setPen(QColor("#aaaaaa"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(10, 20, self.title)
        
        if self.samples is None or len(self.samples) == 0:
            # Message si pas de données
            painter.setPen(QColor("#555555"))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data")
            return
        
        # Dimensions
        width = self.width() - 20
        height = self.height() - 40
        x_offset = 10
        y_offset = 30
        center_y = y_offset + height / 2
        
        # Ligne centrale
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawLine(x_offset, int(center_y), x_offset + width, int(center_y))
        
        # Forme d'onde
        painter.setPen(QPen(self.color, 1.5))
        
        points_per_pixel = len(self.samples) / width
        
        for x in range(width):
            # Récupère les échantillons pour ce pixel
            start_idx = int(x * points_per_pixel)
            end_idx = int((x + 1) * points_per_pixel)
            
            if end_idx >= len(self.samples):
                end_idx = len(self.samples) - 1
            
            if start_idx < len(self.samples):
                # Min et max pour ce segment
                segment = self.samples[start_idx:end_idx]
                if len(segment) > 0:
                    min_val = np.min(segment)
                    max_val = np.max(segment)
                    
                    # Conversion en coordonnées écran
                    y1 = int(center_y - (max_val * height / 2))
                    y2 = int(center_y - (min_val * height / 2))
                    
                    painter.drawLine(x_offset + x, y1, x_offset + x, y2)


class MetricsWidget(QFrame):
    """Widget pour afficher les métriques de comparaison"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("📊 MÉTRIQUES DE COMPARAISON")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #f0f0f0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Container pour les métriques en grille
        metrics_container = QWidget()
        metrics_layout = QHBoxLayout(metrics_container)
        metrics_layout.setSpacing(20)
        
        # Colonne 1
        col1 = QVBoxLayout()
        self.size_label = self._create_metric_label("Taille", "-- → --")
        self.reduction_label = self._create_metric_label("Réduction", "--%")
        col1.addWidget(self.size_label)
        col1.addWidget(self.reduction_label)
        
        # Colonne 2
        col2 = QVBoxLayout()
        self.duration_label = self._create_metric_label("Durée", "--:--")
        self.channels_label = self._create_metric_label("Canaux", "--")
        col2.addWidget(self.duration_label)
        col2.addWidget(self.channels_label)
        
        # Colonne 3
        col3 = QVBoxLayout()
        self.samplerate_label = self._create_metric_label("Sample Rate", "-- Hz")
        self.bitdepth_label = self._create_metric_label("Bit Depth", "-- bits")
        col3.addWidget(self.samplerate_label)
        col3.addWidget(self.bitdepth_label)
        
        metrics_layout.addLayout(col1)
        metrics_layout.addLayout(col2)
        metrics_layout.addLayout(col3)
        
        layout.addWidget(metrics_container)
    
    def _create_metric_label(self, name: str, value: str) -> QLabel:
        """Crée un label de métrique"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 8))
        name_label.setStyleSheet("color: #888888;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #3498db;")
        
        layout.addWidget(name_label)
        layout.addWidget(value_label)
        
        return container
    
    def update_metrics(self, original_info: dict, compressed_info: dict, reduction_rate: float):
        """
        Met à jour les métriques
        
        Args:
            original_info: Infos du fichier original
            compressed_info: Infos du fichier compressé
            reduction_rate: Taux de réduction en %
        """
        # Taille
        orig_size = self._format_size(original_info.get('size', 0))
        comp_size = self._format_size(compressed_info.get('size', 0))
        size_text = f"{orig_size} → {comp_size}"
        self._update_metric_value(self.size_label, size_text)
        
        # Réduction
        reduction_text = f"{reduction_rate:.1f}%"
        self._update_metric_value(self.reduction_label, reduction_text, "#e74c3c")
        
        # Durée
        duration = original_info.get('duration', 0)
        duration_text = self._format_duration(duration)
        self._update_metric_value(self.duration_label, duration_text)
        
        # Canaux
        channels = original_info.get('channels', 0)
        channels_text = "Mono" if channels == 1 else "Stéréo"
        self._update_metric_value(self.channels_label, channels_text)
        
        # Sample Rate
        sr = original_info.get('sample_rate', 0)
        sr_text = f"{sr:,} Hz".replace(',', ' ')
        self._update_metric_value(self.samplerate_label, sr_text)
        
        # Bit Depth
        bit_depth = original_info.get('sample_width', 0) * 8
        bit_text = f"{bit_depth} bits"
        self._update_metric_value(self.bitdepth_label, bit_text)
    
    def _update_metric_value(self, container: QWidget, text: str, color: str = "#3498db"):
        """Met à jour la valeur d'une métrique"""
        # Le deuxième widget du container est le label de valeur
        value_label = container.layout().itemAt(1).widget()
        value_label.setText(text)
        value_label.setStyleSheet(f"color: {color};")
    
    def _format_size(self, size_bytes: int) -> str:
        """Formate la taille en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _format_duration(self, seconds: float) -> str:
        """Formate la durée en format lisible"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def clear(self):
        """Réinitialise les métriques"""
        self._update_metric_value(self.size_label, "-- → --")
        self._update_metric_value(self.reduction_label, "--%")
        self._update_metric_value(self.duration_label, "--:--")
        self._update_metric_value(self.channels_label, "--")
        self._update_metric_value(self.samplerate_label, "-- Hz")
        self._update_metric_value(self.bitdepth_label, "-- bits")


class VisualizationFrame(QFrame):
    """Frame principal contenant toutes les visualisations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("🎵 VISUALISATION AUDIO")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #f0f0f0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Waveforms
        self.original_waveform = WaveformWidget("ORIGINAL", "#27ae60")
        self.compressed_waveform = WaveformWidget("COMPRESSÉ", "#e74c3c")
        
        layout.addWidget(self.original_waveform)
        layout.addWidget(self.compressed_waveform)
        
        # Métriques
        self.metrics = MetricsWidget()
        layout.addWidget(self.metrics)
    
    def set_original_audio(self, audio_segment: AudioSegment):
        """Définit l'audio original"""
        self.original_waveform.set_audio_data(audio_segment)
    
    def set_compressed_audio(self, audio_segment: AudioSegment):
        """Définit l'audio compressé"""
        self.compressed_waveform.set_audio_data(audio_segment)
    
    def update_metrics(self, original_info: dict, compressed_info: dict, reduction_rate: float):
        """Met à jour les métriques"""
        self.metrics.update_metrics(original_info, compressed_info, reduction_rate)
    
    def clear(self):
        """Efface toutes les visualisations"""
        self.original_waveform.clear()
        self.compressed_waveform.clear()
        self.metrics.clear()