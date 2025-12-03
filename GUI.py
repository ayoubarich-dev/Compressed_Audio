from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QFileDialog, QProgressBar
)
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl

from mehdi_compression import *
from stereotreatment import *
from AsciiQuantif import *
from support import *
from irm_final_module import *

def compression(nom_fichier,nom_fichier_bin):
    sound = AudioSegment.from_file(nom_fichier)

    sound_array = np.array(sound.get_array_of_samples())
    bits = sound_array.dtype.itemsize * 8

    channels = sound.channels

    framerate = sound.frame_rate

    frame_width = sound.frame_width

    if sound.channels == 2:
        result = process_stereo_sound(sound_array)
        print(result[0])
        sound_processed_array = result[1]
    else:
        sound_processed_array = sound_array

    lowered_samples_processed_array = sound_processed_array[0::2]
    centered, mean = compute_mean(lowered_samples_processed_array)
    normali, Max = normalisation(centered)
    quanti = quantification(normali)
    residuals = delta_encode(quanti)
    rle_data = rle_encode(residuals)
    encoded_bits, huffman_codes = huffman_encode_rle(rle_data)
    header = struct.pack('!IIIffIIII', sound.frame_rate, len(lowered_samples_processed_array), len(rle_data),Max, mean,sound_array.dtype.itemsize * 8,sound.channels,framerate,frame_width)
    huffman_bytes = zlib.compress(pickle.dumps(huffman_codes))
    
    with open(nom_fichier_bin, 'wb') as f:
        f.write(header)  # 36 bytes
        f.write(struct.pack('!I', len(huffman_bytes)))
        f.write(huffman_bytes)
        f.write(encoded_bits.tobytes())
    
    print(f"Bitstream size: {len(encoded_bits)} bits ({len(encoded_bits.tobytes())} bytes)")
    
def decompression(nom_fichier_bin):
    """Read and decompress audio."""
    with open(nom_fichier_bin, 'rb') as f:
        header = f.read(36)
        sample_rate, length, num_pairs ,Max,mean,bits,channels,framerate,frame_width= struct.unpack('!IIIffIIII', header)
        
        huffman_size = struct.unpack('!I', f.read(4))[0]
        huffman_codes = pickle.loads(zlib.decompress(f.read(huffman_size)))
        
        encoded_bits = bitarray()
        encoded_bits.frombytes(f.read())
        rle_data = huffman_decode_rle(encoded_bits, huffman_codes, num_pairs)
        residuals = rle_decode(rle_data, length)
        pcm_data = delta_decode(residuals)
    # Lecture des données compressées
    #raja3_kolchi = biniary_to_sequnece(nom_fichier_bin)
    #lass9_decode = raja3_kolchi['las9']
    #Max = raja3_kolchi['max']
    #mean = raja3_kolchi['mean']

    # Décompression
    #text = decode_huffmane(lass9_decode)
    #signal_back = text_to_signal(text)
    dequan = dequantification(pcm_data, 256)
    denorm = denormalisation(dequan, Max)
    decomp = decompute_mean(denorm, mean)

    # Reconstruction de signal (interpolation simple)
    demi_data = np.array(decomp, dtype=float)
    moyennes = (demi_data[:-1] + demi_data[1:]) / 2
    resultat = np.empty(len(demi_data) + len(moyennes), dtype=np.dtype(f'int{bits}'))
    resultat[0::2] = demi_data
    resultat[1::2] = moyennes.astype(np.int16)

    if len(demi_data) % 2 == 0:
        resultat = np.append(resultat, demi_data[-1])
    resultat = resultat.astype(np.dtype(f'int{bits}'))

    if channels == 2:
        imitated_stereo = Back_to_real_stereo(resultat, 'm')
    else:
        imitated_stereo = resultat

    # Conversion en AudioSegment
    back_to_audio = AudioSegment(
        data=imitated_stereo.tobytes(),
        sample_width=frame_width,
        frame_rate=framerate,
        channels=channels
    )


    
    return back_to_audio

class AudioCompressorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Audio Compressor")
        self.apply_dark_theme()
        
        # Progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #444;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.showMaximized()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Titre
        header_layout = QHBoxLayout()
        title_label = QLabel("AUDIO COMPRESSOR")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Sélection fichier
        file_frame = QFrame()
        file_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; padding: 10px;")
        file_layout = QHBoxLayout(file_frame)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Segoe UI", 10))
        self.file_label.setStyleSheet("color: #aaaaaa;")
        
        browse_button = QPushButton("SELECT AUDIO")
        browse_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_button.setMinimumHeight(40)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6aa5;
            }
        """)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(browse_button)
        
        # Boutons : original | compression | compressé
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        # Original
        original_frame = self.create_control_frame("ORIGINAL AUDIO")
        original_controls = QHBoxLayout()
        play_original_btn = self.create_button("PLAY", "#27ae60")
        original_controls.addWidget(play_original_btn)
        original_frame.layout().addLayout(original_controls)
        
        # Compression
        compress_frame = self.create_control_frame("COMPRESSION")
        compress_controls = QHBoxLayout()
        compress_btn = self.create_button("COMPRESS", "#e74c3c")
        compress_controls.addWidget(compress_btn)
        compress_frame.layout().addLayout(compress_controls)
        
        # Compressed
        compressed_frame = self.create_control_frame("COMPRESSED AUDIO")
        compressed_controls = QHBoxLayout()
        play_compressed_btn = self.create_button("PLAY", "#9b59b6")
        compressed_controls.addWidget(play_compressed_btn)
        compressed_frame.layout().addLayout(compressed_controls)
        
        controls_layout.addWidget(original_frame)
        controls_layout.addWidget(compress_frame)
        controls_layout.addWidget(compressed_frame)
        
        # Layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(file_frame)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.progress_bar)

        # Étiquette de taux de compression
        self.compression_label = QLabel("")
        self.compression_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compression_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.compression_label.setStyleSheet("color: #e74c3c;")
        main_layout.addWidget(self.compression_label)
        
        # Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Connexions
        browse_button.clicked.connect(self.browse_file)
        play_original_btn.clicked.connect(lambda: self.play_audio("original"))
        compress_btn.clicked.connect(self.compress_audio)
        play_compressed_btn.clicked.connect(self.play_compressed)
        
        self.original_audio_path = None
        self.compressed_audio_path = None
        self.showFullScreen()

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(33, 33, 33))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        self.setPalette(palette)

    def create_control_frame(self, title):
        frame = QFrame()
        frame.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; padding: 15px;")
        layout = QVBoxLayout(frame)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        return frame

    def create_button(self, text, color):
        button = QPushButton(text)
        button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(40)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {color}cc;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """)
        return button

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier audio", "", "Audio Files (*.mp3 *.wav *.ogg *.flac)")
        if file_path:
            self.original_audio_path = file_path
            self.file_label.setText(Path(file_path).name)
            self.progress_bar.setValue(100)
            self.compression_label.setText("")

    def play_audio(self, source_type):
        if source_type == "original" and self.original_audio_path:
            self.player.setSource(QUrl.fromLocalFile(self.original_audio_path))
            self.player.play()

    def compress_audio(self):
        if self.original_audio_path:
            save_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier compressé", "", "Fichiers Binaires (*.IRM)")
            if not save_path:
                return
            self.progress_bar.setValue(0)
            self.compression_label.setText("")
            QApplication.processEvents()
            try:
                compression(self.original_audio_path, save_path)
                for i in range(1, 101):
                    self.progress_bar.setValue(i)
                    QApplication.processEvents()
                self.file_label.setText(f"Fichier compressé enregistré : {Path(save_path).name}")
                self.compressed_audio_path = save_path
                taux = taux_reduction(self.original_audio_path, save_path)
                self.compression_label.setText(f"TAUX DE COMPRESSION : {taux:.2f} %")
            except Exception as e:
                self.file_label.setText(f"Erreur : {e}")
                self.compression_label.setText("")

    def play_compressed(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier compressé", "", "Fichiers IRM (*.IRM)")
        if file_path:
            try:
                segment = decompression(file_path)
                segment.export("decompression.wav", format="wav")
                self.player.setSource(QUrl.fromLocalFile("decompression.wav"))
                self.player.play()
            except Exception as e:
                self.file_label.setText(f"Erreur : {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
        super().keyPressEvent(event)

# === LANCEMENT ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AudioCompressorApp()
    window.show()
    sys.exit(app.exec())