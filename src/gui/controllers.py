"""
Contrôleurs pour la logique de l'interface graphique
Séparation entre UI et logique métier
"""

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QApplication
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QObject, Signal

from core.compressor import AudioCompressor
from core.audio_processor import AudioProcessor
from compression.utils import taux_reduction
from pydub import AudioSegment


class AudioController(QObject):
    """Contrôleur pour les opérations audio"""
    
    # Signaux
    file_selected = Signal(str)  # Fichier sélectionné
    compression_started = Signal()
    compression_progress = Signal(int)  # Progression 0-100
    compression_finished = Signal(float)  # Taux de compression
    compression_error = Signal(str)  # Message d'erreur
    decompression_finished = Signal(str)  # Chemin du fichier décompressé
    
    # Nouveaux signaux pour la visualisation
    original_audio_loaded = Signal(object)  # AudioSegment original
    compressed_audio_loaded = Signal(object)  # AudioSegment compressé
    metrics_updated = Signal(dict, dict, float)  # (original_info, compressed_info, reduction_rate)
    
    def __init__(self):
        super().__init__()
        self.original_audio_path = None
        self.compressed_audio_path = None
        self.original_audio_segment = None
        self.compressed_audio_segment = None
        
        # Lecteur audio
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
    
    def browse_file(self, parent_widget) -> bool:
        """
        Ouvre un dialogue pour sélectionner un fichier
        
        Args:
            parent_widget: Widget parent pour le dialogue
            
        Returns:
            bool: True si un fichier a été sélectionné
        """
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Choisir un fichier audio",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )
        
        if file_path:
            self.original_audio_path = file_path
            self.file_selected.emit(Path(file_path).name)
            
            # Charger l'audio pour la visualisation
            try:
                self.original_audio_segment = AudioSegment.from_file(file_path)
                self.original_audio_loaded.emit(self.original_audio_segment)
            except Exception as e:
                self.compression_error.emit(f"Erreur de chargement: {str(e)}")
            
            return True
        return False
    
    def compress_file(self, parent_widget):
        """
        Compresse le fichier sélectionné
        
        Args:
            parent_widget: Widget parent pour les dialogues
        """
        if not self.original_audio_path:
            self.compression_error.emit("Aucun fichier sélectionné")
            return
        
        # Dialogue pour sauvegarder
        save_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Enregistrer le fichier compressé",
            "",
            "Fichiers IRM (*.IRM)"
        )
        
        if not save_path:
            return
        
        try:
            self.compression_started.emit()
            
            # Compression
            stats = AudioCompressor.compress(self.original_audio_path, save_path)
            
            # Simulation de progression
            for i in range(1, 101):
                self.compression_progress.emit(i)
                QApplication.processEvents()
            
            self.compressed_audio_path = save_path
            
            # Calcul du taux
            taux = taux_reduction(self.original_audio_path, save_path)
            self.compression_finished.emit(taux)
            
            # Décompression pour la visualisation
            try:
                self.compressed_audio_segment = AudioCompressor.decompress(save_path)
                self.compressed_audio_loaded.emit(self.compressed_audio_segment)
                
                # Mise à jour des métriques
                original_info = AudioProcessor.get_file_info(self.original_audio_path)
                compressed_info = {
                    'size': Path(save_path).stat().st_size,
                    'duration': len(self.compressed_audio_segment) / 1000.0,
                    'channels': self.compressed_audio_segment.channels,
                    'sample_rate': self.compressed_audio_segment.frame_rate,
                    'sample_width': self.compressed_audio_segment.sample_width
                }
                self.metrics_updated.emit(original_info, compressed_info, taux)
                
            except Exception as e:
                print(f"Erreur de visualisation: {str(e)}")
            
        except Exception as e:
            self.compression_error.emit(str(e))
    
    def play_original(self):
        """Lit le fichier audio original"""
        if self.original_audio_path:
            self.player.setSource(QUrl.fromLocalFile(self.original_audio_path))
            self.player.play()
    
    def decompress_and_play(self, parent_widget):
        """
        Décompresse et lit un fichier .IRM
        
        Args:
            parent_widget: Widget parent pour le dialogue
        """
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Choisir un fichier compressé",
            "",
            "Fichiers IRM (*.IRM)"
        )
        
        if not file_path:
            return
        
        try:
            # Décompression
            audio = AudioCompressor.decompress(file_path)
            
            # Export temporaire
            temp_file = AudioProcessor.export_for_playback(audio)
            
            # Lecture
            self.player.setSource(QUrl.fromLocalFile(temp_file))
            self.player.play()
            
            self.decompression_finished.emit(Path(file_path).name)
            
        except Exception as e:
            self.compression_error.emit(f"Erreur de décompression: {str(e)}")
    
    def stop_playback(self):
        """Arrête la lecture"""
        self.player.stop()
    
    def cleanup(self):
        """Nettoie les ressources"""
        self.player.stop()
        AudioProcessor.cleanup_temp_files()