"""
Widgets personnalisés pour l'interface graphique - Version compacte
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .styles import AppStyles


class ControlFrame(QFrame):
    """Frame de contrôle compact"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border: 1px solid #383838;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                border: 1px solid #404040;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(title_label)
        
        # Container pour les boutons
        self.button_layout = QHBoxLayout()
        layout.addLayout(self.button_layout)
    
    def add_button(self, button: QPushButton):
        """Ajoute un bouton au frame"""
        self.button_layout.addWidget(button)


class StyledButton(QPushButton):
    """Bouton compact avec effets"""
    
    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._lighten_color(color)}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color)};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
            QPushButton:disabled {{
                background: #555;
                color: #999;
            }}
        """)
    
    def _darken_color(self, color: str) -> str:
        """Assombrit une couleur"""
        from PySide6.QtGui import QColor
        c = QColor(color)
        return c.darker(120).name()
    
    def _lighten_color(self, color: str) -> str:
        """Éclaircit une couleur"""
        from PySide6.QtGui import QColor
        c = QColor(color)
        return c.lighter(110).name()


class FileInfoFrame(QFrame):
    """Frame d'information sur le fichier compact"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border: 2px dashed #383838;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                border: 2px dashed #404040;
            }
        """)
        
        self.setMaximumHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Icône
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setStyleSheet("border: none;")
        
        # Info fichier
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        self.file_label = QLabel("Aucun fichier")
        self.file_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.file_label.setStyleSheet("color: #888888; border: none;")
        self.file_label.setWordWrap(True)
        
        helper_label = QLabel("Cliquez pour sélectionner")
        helper_label.setFont(QFont("Segoe UI", 8))
        helper_label.setStyleSheet("color: #666666; border: none;")
        
        info_layout.addWidget(self.file_label)
        info_layout.addWidget(helper_label)
        
        # Bouton
        self.browse_button = StyledButton("SÉLECTIONNER", AppStyles.COLORS['primary'])
        self.browse_button.setMinimumWidth(120)
        
        layout.addWidget(icon_label)
        layout.addLayout(info_layout, 1)
        layout.addWidget(self.browse_button)
    
    def set_file_name(self, name: str):
        """Définit le nom du fichier"""
        # Limiter la longueur du nom
        if len(name) > 30:
            name = name[:27] + "..."
        self.file_label.setText(name)
        self.file_label.setStyleSheet("color: #3498db; border: none;")
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 12px;
            }
        """)
    
    def reset(self):
        """Réinitialise l'affichage"""
        self.file_label.setText("Aucun fichier")
        self.file_label.setStyleSheet("color: #888888; border: none;")
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border: 2px dashed #383838;
                border-radius: 8px;
                padding: 12px;
            }
        """)


class StyledProgressBar(QProgressBar):
    """Barre de progression compacte"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFixedHeight(25)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 12px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #9b59b6, stop:1 #e74c3c);
                border-radius: 12px;
            }
        """)
    
    def reset(self):
        """Réinitialise la barre"""
        self.setValue(0)


class CompressionInfoLabel(QLabel):
    """Label pour afficher les informations compact"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.setMinimumHeight(50)
        self.setMaximumHeight(60)
        self.setStyleSheet("""
            QLabel {
                background: transparent;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.hide()
    
    def show_compression_rate(self, rate: float):
        """Affiche le taux de compression"""
        self.setText(f"✅ {rate:.1f}%")
        self.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {AppStyles.COLORS['success']}33, stop:1 {AppStyles.COLORS['success']}11);
                border: 2px solid {AppStyles.COLORS['success']};
                border-radius: 8px;
                color: {AppStyles.COLORS['success']};
                padding: 10px;
            }}
        """)
        self.show()
    
    def show_error(self, message: str):
        """Affiche un message d'erreur"""
        # Limiter la longueur du message
        if len(message) > 40:
            message = message[:37] + "..."
        self.setText(f"❌ {message}")
        self.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {AppStyles.COLORS['danger']}33, stop:1 {AppStyles.COLORS['danger']}11);
                border: 2px solid {AppStyles.COLORS['danger']};
                border-radius: 8px;
                color: {AppStyles.COLORS['danger']};
                padding: 10px;
            }}
        """)
        self.show()
    
    def show_success(self, message: str):
        """Affiche un message de succès"""
        # Limiter la longueur du message
        if len(message) > 40:
            message = message[:37] + "..."
        self.setText(f"✅ {message}")
        self.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {AppStyles.COLORS['success']}33, stop:1 {AppStyles.COLORS['success']}11);
                border: 2px solid {AppStyles.COLORS['success']};
                border-radius: 8px;
                color: {AppStyles.COLORS['success']};
                padding: 10px;
            }}
        """)
        self.show()
    
    def clear_message(self):
        """Efface le message"""
        self.hide()
        self.setText("")