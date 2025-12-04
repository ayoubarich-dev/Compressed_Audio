"""
Module de styles et thèmes pour l'interface graphique moderne
"""

from PySide6.QtGui import QPalette, QColor


class AppStyles:
    """Styles modernes de l'application"""
    
    # Palette de couleurs moderne
    COLORS = {
        'primary': '#3498db',
        'success': '#27ae60',
        'danger': '#e74c3c',
        'warning': '#f39c12',
        'info': '#9b59b6',
        'dark': '#2a2a2a',
        'darker': '#1a1a1a',
        'light': '#f0f0f0',
        'gray': '#7f8c8d',
        'accent1': '#1abc9c',
        'accent2': '#e67e22',
        'purple': '#8e44ad'
    }
    
    @staticmethod
    def get_dark_palette() -> QPalette:
        """Retourne la palette de couleurs sombre moderne"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(52, 152, 219))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 152, 219))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Couleurs désactivées
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
        
        return palette


class Icons:
    """Icônes et symboles modernes"""
    
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    COMPRESS = "🗜️"
    FILE = "📁"
    FOLDER = "📂"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    MUSIC = "🎵"
    AUDIO = "🎧"
    MICROPHONE = "🎤"
    SPEAKER = "🔊"
    CHART = "📊"
    SETTINGS = "⚙️"
    DOWNLOAD = "💾"
    UPLOAD = "📤"
    WAVEFORM = "〰️"
    EQUALIZER = "🎚️"
    TIMER = "⏱️"
    SIGNAL = "📡"
    TARGET = "🎯"
    REDUCTION = "📉"
    
    @staticmethod
    def button_style(color: str) -> str:
        """
        Génère le style moderne pour un bouton avec gradient
        
        Args:
            color: Couleur du bouton (hex)
            
        Returns:
            str: Style CSS
        """
        from PySide6.QtGui import QColor
        c = QColor(color)
        darker = c.darker(120).name()
        lighter = c.lighter(110).name()
        
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {darker});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {lighter}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: {darker};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
            QPushButton:disabled {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #555555, stop:1 #444444);
                color: #999999;
            }}
        """
    
    @staticmethod
    def frame_style() -> str:
        """Style pour les frames modernes"""
        return """
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
        """
    
    @staticmethod
    def progress_bar_style() -> str:
        """Style pour la barre de progression moderne"""
        return """
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
        """
    
    @staticmethod
    def label_style(size: int = 10, bold: bool = False, color: str = '#f0f0f0') -> str:
        """
        Style moderne pour les labels
        
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
                background: transparent;
            }}
        """
    
    @staticmethod
    def card_style() -> str:
        """Style pour les cartes de métriques"""
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border: 1px solid #383838;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #303030, stop:1 #252525);
                border: 1px solid #404040;
            }
        """


class Icons:
    """Icônes et symboles modernes"""
    
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    COMPRESS = "🗜️"
    FILE = "📁"
    FOLDER = "📂"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    MUSIC = "🎵"
    AUDIO = "🎧"
    MICROPHONE = "🎤"
    SPEAKER = "🔊"
    CHART = "📊"
    SETTINGS = "⚙️"
    DOWNLOAD = "💾"
    UPLOAD = "📤"
    WAVEFORM = "〰️"
    EQUALIZER = "🎚️"
    TIMER = "⏱️"
    SIGNAL = "📡"
    TARGET = "🎯"
    REDUCTION = "📉"