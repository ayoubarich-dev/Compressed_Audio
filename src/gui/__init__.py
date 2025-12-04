"""Module d'interface graphique avec visualisations"""

from .main_window import AudioCompressorWindow
from .controllers import AudioController
from .widgets import (
    ControlFrame, StyledButton, FileInfoFrame,
    StyledProgressBar, CompressionInfoLabel
)
from .visualization_widget import (
    VisualizationFrame, WaveformWidget, MetricsWidget
)
from .styles import AppStyles, Icons

__all__ = [
    'AudioCompressorWindow', 'AudioController',
    'ControlFrame', 'StyledButton', 'FileInfoFrame',
    'StyledProgressBar', 'CompressionInfoLabel',
    'VisualizationFrame', 'WaveformWidget', 'MetricsWidget',
    'AppStyles', 'Icons'
]