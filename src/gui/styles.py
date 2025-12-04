"""
Module de styles et thèmes pour l'interface graphique
"""

from PySide6.QtGui import QPalette, QColor


class AppStyles:
    """Styles de l'application"""
    
    # Couleurs
    COLORS = {
        'primary': '#3498db',
        'success': '#27ae60',
        'danger': '#e74c3c',
        'warning': '#f39c12',
        'info': '#9b59b6',
        'dark': '#2a2a2a',
        'darker': '#1a1a1a',
        'light': '#f0f0f0',
        'gray': '#aaaaaa'
    }
    
    @staticmethod
    def get_dark_palette() -> QPalette:
        """Retourne la palette de couleurs sombre"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(33, 33, 33))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        return palette
    
    @staticmethod
    def button_style(color: str) -> str:
        """
        Génère le style pour un bouton
        
        Args:
            color: Couleur du bouton (hex)
            
        Returns:
            str: Style CSS
        """
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}cc;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #999;
            }}
        """
    
    @staticmethod
    def frame_style() -> str:
        """Style pour les frames"""
        return """
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """
    
    @staticmethod
    def progress_bar_style() -> str:
        """Style pour la barre de progression"""
        return """
            QProgressBar {
                border: none;
                background-color: #444;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """
    
    @staticmethod
    def label_style(size: int = 10, bold: bool = False, color: str = '#f0f0f0') -> str:
        """
        Style pour les labels
        
        Args:
            size: Taille de la police
            bold: Gras
            color: Couleur du texte
            
        Returns:
            str: Style CSS
        """
        weight = 'bold' if bold else 'normal'
        return f"""
            QLabel {{
                color: {color};
                font-size: {size}pt;
                font-weight: {weight};
            }}
        """


class Icons:
    """Icônes et symboles"""
    
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    COMPRESS = "🗜️"
    FILE = "📁"
    SUCCESS = "✅"
    ERROR = "❌"
    INFO = "ℹ️"