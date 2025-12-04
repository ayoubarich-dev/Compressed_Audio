"""
Module de traitement audio
Gère la lecture et l'export de fichiers audio
"""

import os
from pathlib import Path
from pydub import AudioSegment


class AudioProcessor:
    """Classe pour le traitement des fichiers audio"""
    
    SUPPORTED_FORMATS = ['.mp3', '.wav', '.ogg', '.flac']
    TEMP_FILE = "temp_decompressed.wav"
    
    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """
        Vérifie si le format est supporté
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            bool: True si supporté
        """
        ext = Path(file_path).suffix.lower()
        return ext in AudioProcessor.SUPPORTED_FORMATS
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Récupère les informations d'un fichier audio
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            dict: Informations du fichier
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier introuvable: {file_path}")
        
        sound = AudioSegment.from_file(file_path)
        
        return {
            'path': file_path,
            'name': Path(file_path).name,
            'size': os.path.getsize(file_path),
            'duration': len(sound) / 1000.0,  # en secondes
            'channels': sound.channels,
            'sample_rate': sound.frame_rate,
            'sample_width': sound.sample_width
        }
    
    @staticmethod
    def export_for_playback(audio: AudioSegment, output_path: str = None) -> str:
        """
        Exporte l'audio pour la lecture
        
        Args:
            audio: AudioSegment à exporter
            output_path: Chemin de sortie (optionnel)
            
        Returns:
            str: Chemin du fichier exporté
        """
        if output_path is None:
            output_path = AudioProcessor.TEMP_FILE
        
        audio.export(output_path, format="wav")
        return output_path
    
    @staticmethod
    def cleanup_temp_files():
        """Nettoie les fichiers temporaires"""
        if os.path.exists(AudioProcessor.TEMP_FILE):
            try:
                os.remove(AudioProcessor.TEMP_FILE)
            except:
                pass
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Formate la taille en format lisible
        
        Args:
            size_bytes: Taille en bytes
            
        Returns:
            str: Taille formatée (ex: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Formate la durée en format lisible
        
        Args:
            seconds: Durée en secondes
            
        Returns:
            str: Durée formatée (ex: "3:45")
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"