"""
Widget de visualisation professionnel pour comparer l'audio original et compressé
"""

import numpy as np
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QLinearGradient, QPainterPath, QBrush
from pydub import AudioSegment


class WaveformWidget(QWidget):
    """Widget professionnel pour afficher une forme d'onde avec gradient"""
    
    def __init__(self, title: str, color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = QColor(color)
        self.samples = None
        self.setMinimumHeight(100)
        self.setMaximumHeight(130)
        self.animation_progress = 0
        
    def set_audio_data(self, audio_segment: AudioSegment):
        """Charge les données audio avec animation"""
        try:
            samples = np.array(audio_segment.get_array_of_samples())
            
            # Sous-échantillonnage intelligent
            target_points = min(3000, len(samples))
            if len(samples) > target_points:
                step = len(samples) // target_points
                self.samples = samples[::step]
            else:
                self.samples = samples
                
            # Normalisation
            if len(self.samples) > 0:
                max_val = np.max(np.abs(self.samples))
                if max_val > 0:
                    self.samples = self.samples / max_val
            
            self.animation_progress = 0
            self.animate_waveform()
            self.update()
        except Exception as e:
            print(f"[ERREUR] Chargement waveform: {e}")
    
    def animate_waveform(self):
        """Animation d'apparition progressive"""
        timer = QTimer(self)
        def update_progress():
            self.animation_progress = min(100, self.animation_progress + 10)
            self.update()
            if self.animation_progress >= 100:
                timer.stop()
        timer.timeout.connect(update_progress)
        timer.start(20)
    
    def clear(self):
        """Efface les données"""
        self.samples = None
        self.animation_progress = 0
        self.update()
    
    def paintEvent(self, event):
        """Dessine la forme d'onde avec style professionnel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fond avec gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#1a1a1a"))
        gradient.setColorAt(1, QColor("#0a0a0a"))
        painter.fillRect(self.rect(), gradient)
        
        # Bordure subtile
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 6, 6)
        
        # Titre avec ombre
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(9, 17, self.title)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(8, 16, self.title)
        
        if self.samples is None or len(self.samples) == 0:
            # Message stylisé
            painter.setPen(QColor("#666666"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Light))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aucune donnée")
            return
        
        # Dimensions
        width = self.width() - 20
        height = self.height() - 40
        x_offset = 10
        y_offset = 28
        center_y = y_offset + height / 2
        
        # Grille de fond
        painter.setPen(QPen(QColor("#222222"), 1, Qt.PenStyle.DotLine))
        for i in range(3):
            y = y_offset + (height * i / 2)
            painter.drawLine(x_offset, int(y), x_offset + width, int(y))
        
        # Ligne centrale accentuée
        painter.setPen(QPen(QColor("#444444"), 1.5))
        painter.drawLine(x_offset, int(center_y), x_offset + width, int(center_y))
        
        # Forme d'onde avec gradient et glow
        visible_width = int(width * self.animation_progress / 100)
        
        # Effet glow (ombre)
        glow_color = QColor(self.color)
        glow_color.setAlpha(50)
        painter.setPen(QPen(glow_color, 3))
        self._draw_waveform(painter, x_offset, center_y, visible_width, height)
        
        # Forme d'onde principale
        gradient_wave = QLinearGradient(0, y_offset, 0, y_offset + height)
        gradient_wave.setColorAt(0, self.color.lighter(120))
        gradient_wave.setColorAt(0.5, self.color)
        gradient_wave.setColorAt(1, self.color.darker(110))
        
        painter.setPen(QPen(QBrush(gradient_wave), 1.8))
        self._draw_waveform(painter, x_offset, center_y, visible_width, height)
        
        # Remplissage sous la courbe
        path = QPainterPath()
        points_per_pixel = len(self.samples) / width
        
        first_point = True
        for x in range(visible_width):
            start_idx = int(x * points_per_pixel)
            end_idx = int((x + 1) * points_per_pixel)
            
            if end_idx >= len(self.samples):
                end_idx = len(self.samples) - 1
            
            if start_idx < len(self.samples):
                segment = self.samples[start_idx:end_idx]
                if len(segment) > 0:
                    max_val = np.max(segment)
                    y = int(center_y - (max_val * height / 2))
                    
                    if first_point:
                        path.moveTo(x_offset + x, center_y)
                        first_point = False
                    path.lineTo(x_offset + x, y)
        
        # Compléter le chemin pour le remplissage
        if visible_width > 0:
            path.lineTo(x_offset + visible_width, center_y)
            path.closeSubpath()
        
        # Remplissage avec gradient transparent
        fill_gradient = QLinearGradient(0, y_offset, 0, y_offset + height)
        fill_color_top = QColor(self.color)
        fill_color_top.setAlpha(60)
        fill_color_bottom = QColor(self.color)
        fill_color_bottom.setAlpha(15)
        fill_gradient.setColorAt(0, fill_color_top)
        fill_gradient.setColorAt(1, fill_color_bottom)
        
        painter.fillPath(path, fill_gradient)
        
    def _draw_waveform(self, painter, x_offset, center_y, visible_width, height):
        """Dessine la forme d'onde"""
        points_per_pixel = len(self.samples) / (self.width() - 20)
        
        for x in range(visible_width):
            start_idx = int(x * points_per_pixel)
            end_idx = int((x + 1) * points_per_pixel)
            
            if end_idx >= len(self.samples):
                end_idx = len(self.samples) - 1
            
            if start_idx < len(self.samples):
                segment = self.samples[start_idx:end_idx]
                if len(segment) > 0:
                    min_val = np.min(segment)
                    max_val = np.max(segment)
                    
                    y1 = int(center_y - (max_val * height / 2))
                    y2 = int(center_y - (min_val * height / 2))
                    
                    painter.drawLine(x_offset + x, y1, x_offset + x, y2)


class MetricCard(QFrame):
    """Carte de métrique individuelle compacte"""
    
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        
        # Style simplifié avec CSS plus direct
        self.setStyleSheet("""
            MetricCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border: 1px solid #383838;
                border-radius: 8px;
            }
            MetricCard:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #303030, stop:1 #252525);
                border: 1px solid #404040;
            }
        """)
        
        self.setFixedHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(12, 10, 12, 10)  # Augmenté les marges
        
        # Icône + Titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI", 14))
        # Style direct sans CSS
        self.icon_label.setStyleSheet("QLabel { color: #3498db; background: transparent; }")
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Normal))
        self.title_label.setStyleSheet("QLabel { color: #999999; background: transparent; }")
        
        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Valeur - Style direct sans héritage
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))  # Taille augmentée
        self.value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()
    
    def set_value(self, value: str, color: str = "#ffffff"):
        """Définit la valeur avec visibilité garantie"""
        self.value_label.setText(str(value))
        # Style direct avec !important pour forcer l'application
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {color} !important;
                background: transparent !important;
                border: none !important;
                font-size: 14px !important;
                font-weight: bold !important;
                padding: 0px !important;
                margin: 0px !important;
            }}
        """)
        self.value_label.setVisible(True)
        self.update()
        self.repaint()


class MetricsWidget(QFrame):
    """Widget de métriques compact"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Style direct sans héritage
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre - Style direct
        title = QLabel("📊 MÉTRIQUES DE COMPRESSION")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                padding: 5px;
                background: transparent;
                border: none;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Grille de cartes
        grid = QGridLayout()
        grid.setSpacing(10)  # Espacement augmenté
        grid.setContentsMargins(5, 5, 5, 5)
        
        # Créer les cartes
        self.size_card = MetricCard("💾", "Taille")
        self.reduction_card = MetricCard("📉", "Réduction")
        self.duration_card = MetricCard("⏱️", "Durée")
        self.channels_card = MetricCard("🎚️", "Canaux")
        self.samplerate_card = MetricCard("📡", "Sample Rate")
        self.bitdepth_card = MetricCard("🎯", "Bit Depth")
        
        # Ligne 1
        grid.addWidget(self.size_card, 0, 0)
        grid.addWidget(self.reduction_card, 0, 1)
        grid.addWidget(self.duration_card, 0, 2)
        
        # Ligne 2
        grid.addWidget(self.channels_card, 1, 0)
        grid.addWidget(self.samplerate_card, 1, 1)
        grid.addWidget(self.bitdepth_card, 1, 2)
        
        layout.addLayout(grid)
        
        # Forcer l'initialisation des valeurs
        self.clear()
    
    def update_metrics(self, original_info: dict, compressed_info: dict, reduction_rate: float):
        """Met à jour toutes les métriques"""
        try:
            print("\n========== MISE À JOUR MÉTRIQUES ==========")
            
            # Taille
            orig_size = self._format_size(original_info.get('size', 0))
            comp_size = self._format_size(compressed_info.get('size', 0))
            size_text = f"{orig_size} → {comp_size}"
            print(f"✓ Taille: {size_text}")
            self.size_card.set_value(size_text, "#3498db")
            
            # Réduction
            reduction_text = f"{reduction_rate:.1f}%"
            print(f"✓ Réduction: {reduction_text}")
            self.reduction_card.set_value(reduction_text, "#e74c3c")
            
            # Durée
            duration = original_info.get('duration', 0)
            duration_text = self._format_duration(duration)
            print(f"✓ Durée: {duration_text}")
            self.duration_card.set_value(duration_text, "#27ae60")
            
            # Canaux
            channels = original_info.get('channels', 0)
            channels_text = "Mono" if channels == 1 else "Stéréo"
            print(f"✓ Canaux: {channels_text}")
            self.channels_card.set_value(channels_text, "#f39c12")
            
            # Sample Rate
            sr = original_info.get('sample_rate', 0)
            sr_text = f"{sr//1000} kHz" if sr > 0 else "--"
            print(f"✓ Sample Rate: {sr_text}")
            self.samplerate_card.set_value(sr_text, "#9b59b6")
            
            # Bit Depth
            bit_depth = original_info.get('sample_width', 0) * 8
            bit_text = f"{bit_depth} bits" if bit_depth > 0 else "--"
            print(f"✓ Bit Depth: {bit_text}")
            self.bitdepth_card.set_value(bit_text, "#1abc9c")
            
            print("========== FIN MISE À JOUR ==========\n")
            
            # Force le rafraîchissement immédiat
            self.update()
            self.repaint()
            
        except Exception as e:
            print(f"❌ ERREUR update_metrics: {e}")
            import traceback
            traceback.print_exc()
    
    def _format_size(self, size_bytes: int) -> str:
        """Formate la taille"""
        if size_bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _format_duration(self, seconds: float) -> str:
        """Formate la durée"""
        if seconds == 0:
            return "0:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def clear(self):
        """Réinitialise les métriques"""
        # Initialise avec des valeurs visibles
        self.size_card.set_value("--", "#ffffff")
        self.reduction_card.set_value("--", "#ffffff")
        self.duration_card.set_value("--", "#ffffff")
        self.channels_card.set_value("--", "#ffffff")
        self.samplerate_card.set_value("--", "#ffffff")
        self.bitdepth_card.set_value("--", "#ffffff")
        
        # Force le rafraîchissement
        self.update()
        self.repaint()


class VisualizationFrame(QFrame):
    """Frame principal avec visualisations compactes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Style amélioré avec bordures et fond
        self.setStyleSheet("""
            VisualizationFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #151515);
                border: 2px solid #2a2a2a;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre principal - Style direct
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🎵 VISUALISATION AUDIO")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))  # Taille augmentée
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        subtitle = QLabel("Analyse comparative en temps réel")
        subtitle.setFont(QFont("Segoe UI", 9, QFont.Weight.Light))
        subtitle.setStyleSheet("""
            QLabel {
                color: #888888;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        title_left = QVBoxLayout()
        title_left.setSpacing(3)
        title_left.addWidget(title)
        title_left.addWidget(subtitle)
        
        title_layout.addLayout(title_left)
        title_layout.addStretch()
        
        layout.addWidget(title_container)
        
        # Waveforms
        self.original_waveform = WaveformWidget("🎵 ORIGINAL", "#27ae60")
        self.compressed_waveform = WaveformWidget("🗜️ COMPRESSÉ", "#e74c3c")
        
        layout.addWidget(self.original_waveform)
        layout.addWidget(self.compressed_waveform)
        
        # Métriques
        self.metrics = MetricsWidget()
        layout.addWidget(self.metrics)
        
        layout.addStretch()
    
    def set_original_audio(self, audio_segment: AudioSegment):
        """Définit l'audio original"""
        self.original_waveform.set_audio_data(audio_segment)
    
    def set_compressed_audio(self, audio_segment: AudioSegment):
        """Définit l'audio compressé"""
        self.compressed_waveform.set_audio_data(audio_segment)
    
    def update_metrics(self, original_info: dict, compressed_info: dict, reduction_rate: float):
        """Met à jour les métriques"""
        print("[VIZ] Appel de update_metrics")
        self.metrics.update_metrics(original_info, compressed_info, reduction_rate)
    
    def clear(self):
        """Efface toutes les visualisations"""
        self.original_waveform.clear()
        self.compressed_waveform.clear()
        self.metrics.clear()