"""
Audio Compressor - Point d'entrée de l'application
Compresseur audio utilisant Delta Encoding + RLE + Huffman
"""

import sys
from pathlib import Path

# Ajouter src au path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from gui.main_window import AudioCompressorWindow


def main():
    """Lance l'application Audio Compressor"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Audio Compressor")
    app.setOrganizationName("AudioCompressor")
    
    window = AudioCompressorWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()