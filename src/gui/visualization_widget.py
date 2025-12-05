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
        self.setMinimumHeight(80)  # Réduit un peu pour laisser plus d'espace
        self.setMaximumHeight(110)
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


class SizeBarChart(QWidget):
    """Diagramme en bâtons pour comparer les tailles original vs compressé"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_size = 0
        self.compressed_size = 0
        self.setMinimumHeight(180)  # AUGMENTÉ pour plus de visibilité
        self.setMaximumHeight(220)  # AUGMENTÉ pour plus de visibilité
        
        # Titre
        self.title = "📊 COMPARAISON DES TAILLES"
        self.original_label = "ORIGINAL"
        self.compressed_label = "COMPRESSÉ"
        self.original_color = QColor("#27ae60")  # Vert
        self.compressed_color = QColor("#e74c3c")  # Rouge
    
    def set_sizes(self, original_size: int, compressed_size: int):
        """Définit les tailles à afficher"""
        self.original_size = original_size
        self.compressed_size = compressed_size
        self.update()
    
    def clear(self):
        """Efface les données"""
        self.original_size = 0
        self.compressed_size = 0
        self.update()
    
    def _format_size(self, size_bytes: int) -> str:
        """Formate la taille en unités lisibles"""
        if size_bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def paintEvent(self, event):
        """Dessine le diagramme en bâtons"""
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
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(9, 22, self.title)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(8, 21, self.title)
        
        if self.original_size == 0 and self.compressed_size == 0:
            # Message quand pas de données
            painter.setPen(QColor("#666666"))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Light))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aucune donnée de taille")
            return
        
        # Dimensions AGRANDIES
        width = self.width() - 40
        height = self.height() - 80  # Plus d'espace pour les barres
        x_offset = 20
        y_offset = 50  # Décalé vers le bas pour plus de hauteur de barre
        max_height = height - 30
        
        # Trouver la plus grande taille pour l'échelle
        max_size = max(self.original_size, self.compressed_size)
        if max_size == 0:
            return
        
        # Bar settings AGRANDIES
        bar_width = width // 4  # Barres plus larges
        gap = bar_width // 2
        
        # Position des barres
        original_x = x_offset + gap
        compressed_x = original_x + bar_width + gap
        
        # Calcul des hauteurs
        original_height = int((self.original_size / max_size) * max_height)
        compressed_height = int((self.compressed_size / max_size) * max_height)
        
        # S'assurer que les barres ont une hauteur minimum pour être visibles
        min_bar_height = 20
        original_height = max(original_height, min_bar_height)
        compressed_height = max(compressed_height, min_bar_height)
        
        # Barre originale (vert)
        self._draw_bar(painter, 
                      original_x, y_offset + max_height - original_height,
                      bar_width, original_height,
                      self.original_color, self.original_label,
                      self._format_size(self.original_size))
        
        # Barre compressée (rouge)
        self._draw_bar(painter,
                      compressed_x, y_offset + max_height - compressed_height,
                      bar_width, compressed_height,
                      self.compressed_color, self.compressed_label,
                      self._format_size(self.compressed_size))
        
        # Ligne de base plus épaisse
        baseline_y = y_offset + max_height
        painter.setPen(QPen(QColor("#444444"), 3))
        painter.drawLine(x_offset, baseline_y, x_offset + width, baseline_y)
        
        # Échelle à gauche
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.setFont(QFont("Segoe UI", 7))
        for i in range(4):
            y = y_offset + max_height - (i * max_height // 3)
            size_value = (i * max_size // 3)
            size_text = self._format_size(size_value)
            painter.drawText(x_offset - 45, y - 5, 40, 10, 
                           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                           size_text)
            painter.drawLine(x_offset - 5, y, x_offset, y)
        
        # Légende améliorée
        legend_y = baseline_y + 20
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        # Calcul de la réduction
        if self.original_size > 0:
            reduction_rate = ((self.original_size - self.compressed_size) / self.original_size) * 100
            reduction_text = f"📉 RÉDUCTION: {reduction_rate:.1f}%"
        else:
            reduction_text = "📉 RÉDUCTION: --%"
        
        painter.setPen(QColor("#3498db"))
        painter.drawText(self.rect().adjusted(10, 0, -10, -10), 
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
                        reduction_text)
    
    def _draw_bar(self, painter, x, y, width, height, color, label, value_text):
        """Dessine une barre individuelle"""
        # Effet 3D avec gradient plus prononcé
        gradient = QLinearGradient(x, y, x, y + height)
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(0.3, color.lighter(110))
        gradient.setColorAt(0.7, color)
        gradient.setColorAt(1, color.darker(120))
        
        painter.fillRect(x, y, width, height, gradient)
        
        # Bordure plus visible
        painter.setPen(QPen(color.darker(150), 2))
        painter.drawRect(x, y, width, height)
        
        # Effet de brillance
        highlight_color = color.lighter(180)
        highlight_color.setAlpha(100)
        painter.setPen(QPen(highlight_color, 1))
        painter.drawLine(x + 1, y + 1, x + width - 2, y + 1)
        painter.drawLine(x + 1, y + 1, x + 1, y + height - 2)
        
        # Label au-dessus de la barre (plus grand)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(x, y - 25, width, 20, 
                        Qt.AlignmentFlag.AlignCenter, label)
        
        # Valeur à l'intérieur de la barre (toujours affichée)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        
        # Positionner le texte au milieu de la barre ou au-dessus si barre trop petite
        if height > 25:
            text_y = y + (height // 2) - 8
            painter.drawText(x, text_y, width, 16,
                           Qt.AlignmentFlag.AlignCenter, value_text)
        else:
            # Si barre trop petite, afficher au-dessus
            painter.drawText(x, y - 35, width, 20,
                           Qt.AlignmentFlag.AlignCenter, value_text)


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
        
        self.setFixedHeight(70)  # Légèrement réduit pour libérer de l'espace
        self.setMaximumHeight(75)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)  # Espacement réduit
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Icône + Titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI", 12))
        self.icon_label.setStyleSheet("QLabel { color: #3498db; background: transparent; }")
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        self.title_label.setStyleSheet("QLabel { color: #999999; background: transparent; }")
        
        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        # Valeur
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
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
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {color} !important;
                background: transparent !important;
                border: none !important;
                font-size: 13px !important;
                font-weight: bold !important;
                padding: 0px !important;
                margin: 0px !important;
            }}
        """)
        self.value_label.setVisible(True)
        self.update()
        self.repaint()


class MetricsWidget(QFrame):
    """Widget de métriques compact avec taux de réduction intégré"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # Espacement réduit
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre
        title = QLabel("📊 MÉTRIQUES")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                padding: 3px;
                background: transparent;
                border: none;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Grille de cartes
        grid = QGridLayout()
        grid.setSpacing(8)  # Espacement réduit
        grid.setContentsMargins(3, 3, 3, 3)
        
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
        
        # Initialiser
        self.clear()
    
    def update_metrics(self, original_info: dict, compressed_info: dict, reduction_rate: float):
        """Met à jour toutes les métriques"""
        try:
            # Taille
            orig_size = self._format_size(original_info.get('size', 0))
            comp_size = self._format_size(compressed_info.get('size', 0))
            size_text = f"{orig_size} → {comp_size}"
            self.size_card.set_value(size_text, "#3498db")
            
            # Réduction
            reduction_text = f"{reduction_rate:.1f}%"
            # Changer la couleur selon le taux
            if reduction_rate >= 80:
                reduction_color = "#e74c3c"
            elif reduction_rate >= 60:
                reduction_color = "#f39c12"
            elif reduction_rate >= 40:
                reduction_color = "#f1c40f"
            else:
                reduction_color = "#7f8c8d"
            self.reduction_card.set_value(reduction_text, reduction_color)
            
            # Durée
            duration = original_info.get('duration', 0)
            duration_text = self._format_duration(duration)
            self.duration_card.set_value(duration_text, "#27ae60")
            
            # Canaux
            channels = original_info.get('channels', 0)
            channels_text = "Mono" if channels == 1 else "Stéréo"
            self.channels_card.set_value(channels_text, "#f39c12")
            
            # Sample Rate
            sr = original_info.get('sample_rate', 0)
            sr_text = f"{sr//1000} kHz" if sr > 0 else "--"
            self.samplerate_card.set_value(sr_text, "#9b59b6")
            
            # Bit Depth
            bit_depth = original_info.get('sample_width', 0) * 8
            bit_text = f"{bit_depth} bits" if bit_depth > 0 else "--"
            self.bitdepth_card.set_value(bit_text, "#1abc9c")
            
            # Force le rafraîchissement
            self.update()
            self.repaint()
            
        except Exception as e:
            print(f"❌ ERREUR update_metrics: {e}")
    
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
        self.size_card.set_value("--", "#ffffff")
        self.reduction_card.set_value("--", "#ffffff")
        self.duration_card.set_value("--", "#ffffff")
        self.channels_card.set_value("--", "#ffffff")
        self.samplerate_card.set_value("--", "#ffffff")
        self.bitdepth_card.set_value("--", "#ffffff")
        self.update()
        self.repaint()


class VisualizationFrame(QFrame):
    """Frame principal avec visualisations compactes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            VisualizationFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #151515);
                border: 2px solid #2a2a2a;
                border-radius: 12px;
                padding: 12px;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Espacement réduit pour mieux répartir
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Titre principal plus compact
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🎵 VISUALISATION AUDIO")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        subtitle = QLabel("Analyse comparative")
        subtitle.setFont(QFont("Segoe UI", 8, QFont.Weight.Light))
        subtitle.setStyleSheet("""
            QLabel {
                color: #888888;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        title_left = QVBoxLayout()
        title_left.setSpacing(2)
        title_left.addWidget(title)
        title_left.addWidget(subtitle)
        
        title_layout.addLayout(title_left)
        title_layout.addStretch()
        
        layout.addWidget(title_container)
        
        # Waveforms (réduites)
        self.original_waveform = WaveformWidget("🎵 ORIGINAL", "#27ae60")
        self.compressed_waveform = WaveformWidget("🗜️ COMPRESSÉ", "#e74c3c")
        
        layout.addWidget(self.original_waveform)
        layout.addWidget(self.compressed_waveform)
        
        # Métriques (réduites)
        self.metrics = MetricsWidget()
        layout.addWidget(self.metrics)
        
        # Diagramme en bâtons de taille (AGRANDI)
        self.size_chart = SizeBarChart()
        layout.addWidget(self.size_chart, 2)  # Facteur d'étirement = 2
        
        layout.addStretch()
    
    def set_original_audio(self, audio_segment: AudioSegment):
        """Définit l'audio original"""
        self.original_waveform.set_audio_data(audio_segment)
    
    def set_compressed_audio(self, audio_segment: AudioSegment):
        """Définit l'audio compressé"""
        self.compressed_waveform.set_audio_data(audio_segment)
    
    def update_metrics(self, original_info: dict, compressed_info: dict, reduction_rate: float):
        """Met à jour les métriques ET le diagramme de taille"""
        print("[VIZ] Mise à jour métriques + diagramme de taille")
        
        # Mettre à jour les métriques
        self.metrics.update_metrics(original_info, compressed_info, reduction_rate)
        
        # Mettre à jour le diagramme de taille
        original_size = original_info.get('size', 0)
        compressed_size = compressed_info.get('size', 0)
        self.size_chart.set_sizes(original_size, compressed_size)
    
    def clear(self):
        """Efface toutes les visualisations"""
        self.original_waveform.clear()
        self.compressed_waveform.clear()
        self.metrics.clear()
        self.size_chart.clear()