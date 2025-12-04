"""
Widgets personnalisés pour l'interface graphique
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .styles import AppStyles


class ControlFrame(QFrame):
    """Frame de contrôle avec titre et boutons"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(AppStyles.frame_style())
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        
        # Container pour les boutons
        self.button_layout = QHBoxLayout()
        layout.addLayout(self.button_layout)
    
    def add_button(self, button: QPushButton):
        """Ajoute un bouton au frame"""
        self.button_layout.addWidget(button)


class StyledButton(QPushButton):
    """Bouton stylisé"""
    
    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet(AppStyles.button_style(color))


class FileInfoFrame(QFrame):
    """Frame d'information sur le fichier"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; padding: 10px;")
        
        layout = QHBoxLayout(self)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Segoe UI", 10))
        self.file_label.setStyleSheet("color: #aaaaaa;")
        
        self.browse_button = StyledButton("SELECT AUDIO", AppStyles.COLORS['primary'])
        
        layout.addWidget(self.file_label)
        layout.addWidget(self.browse_button)
    
    def set_file_name(self, name: str):
        """Définit le nom du fichier"""
        self.file_label.setText(name)
        self.file_label.setStyleSheet("color: #f0f0f0;")
    
    def reset(self):
        """Réinitialise l'affichage"""
        self.file_label.setText("No file selected")
        self.file_label.setStyleSheet("color: #aaaaaa;")


class StyledProgressBar(QProgressBar):
    """Barre de progression stylisée"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFixedHeight(25)
        self.setStyleSheet(AppStyles.progress_bar_style())
    
    def reset(self):
        """Réinitialise la barre"""
        self.setValue(0)


class CompressionInfoLabel(QLabel):
    """Label pour afficher les informations de compression"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.hide()
    
    def show_compression_rate(self, rate: float):
        """Affiche le taux de compression"""
        self.setText(f"TAUX DE COMPRESSION : {rate:.2f} %")
        self.setStyleSheet(f"color: {AppStyles.COLORS['danger']};")
        self.show()
    
    def show_error(self, message: str):
        """Affiche un message d'erreur"""
        self.setText(f"❌ {message}")
        self.setStyleSheet(f"color: {AppStyles.COLORS['danger']};")
        self.show()
    
    def show_success(self, message: str):
        """Affiche un message de succès"""
        self.setText(f"✅ {message}")
        self.setStyleSheet(f"color: {AppStyles.COLORS['success']};")
        self.show()
    
    def clear_message(self):
        """Efface le message"""
        self.hide()
        self.setText("")