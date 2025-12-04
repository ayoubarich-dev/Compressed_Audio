"""
Module de compression/décompression audio
Gère la logique de compression complète
"""

import struct
import zlib
import pickle
from bitarray import bitarray
from pydub import AudioSegment
import numpy as np

from compression.stereotreatment import process_stereo_sound, Back_to_real_stereo
from compression.quantification import (
    compute_mean, normalisation, quantification,
    dequantification, denormalisation, decompute_mean
)
from compression.encoding import (
    delta_encode, delta_decode, rle_encode, 
    rle_decode, huffman_encode_rle, huffman_decode_rle
)


class AudioCompressor:
    """Classe principale pour la compression audio"""
    
    @staticmethod
    def compress(input_path: str, output_path: str) -> dict:
        """
        Compresse un fichier audio
        
        Args:
            input_path: Chemin du fichier source
            output_path: Chemin du fichier compressé
            
        Returns:
            dict: Statistiques de compression
        """
        print(f"📁 Chargement: {input_path}")
        
        # 1. Chargement de l'audio
        sound = AudioSegment.from_file(input_path)
        sound_array = np.array(sound.get_array_of_samples())
        
        metadata = {
            'bits': sound_array.dtype.itemsize * 8,
            'channels': sound.channels,
            'framerate': sound.frame_rate,
            'frame_width': sound.frame_width,
            'original_samples': len(sound_array)
        }
        
        print(f"📊 Format: {metadata['channels']} canaux, {metadata['framerate']} Hz")

        # 2. Traitement stéréo
        if sound.channels == 2:
            result = process_stereo_sound(sound_array)
            print(f"🎧 Mode stéréo: {result[0]['mode']}")
            sound_processed = result[1]
        else:
            print("🎧 Mode mono")
            sound_processed = sound_array

        # 3. Sous-échantillonnage
        lowered_samples = sound_processed[0::2]
        print(f"📉 Échantillons: {len(sound_array)} → {len(lowered_samples)}")
        
        # 4-5. Prétraitement
        centered, mean = compute_mean(lowered_samples)
        normalized, max_val = normalisation(centered)
        quantized = quantification(normalized)
        
        # 6-8. Compression
        residuals = delta_encode(quantized)
        rle_data = rle_encode(residuals)
        encoded_bits, huffman_codes = huffman_encode_rle(rle_data)
        
        print(f"🗜️  RLE: {len(residuals)} → {len(rle_data)} paires")
        print(f"🗜️  Huffman: {len(encoded_bits)} bits")
        
        # Création du header
        header = struct.pack('!IIIffIIII',
                           sound.frame_rate,
                           len(lowered_samples),
                           len(rle_data),
                           max_val,
                           mean,
                           metadata['bits'],
                           metadata['channels'],
                           metadata['framerate'],
                           metadata['frame_width'])
        
        huffman_bytes = zlib.compress(pickle.dumps(huffman_codes))
        
        # Écriture du fichier
        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(struct.pack('!I', len(huffman_bytes)))
            f.write(huffman_bytes)
            f.write(encoded_bits.tobytes())
        
        stats = {
            'original_samples': metadata['original_samples'],
            'compressed_samples': len(lowered_samples),
            'rle_pairs': len(rle_data),
            'compressed_bits': len(encoded_bits),
            'compressed_bytes': len(encoded_bits.tobytes())
        }
        
        print(f"✅ Compression terminée")
        return stats
    
    @staticmethod
    def decompress(input_path: str) -> AudioSegment:
        """
        Décompresse un fichier .IRM
        
        Args:
            input_path: Chemin du fichier compressé
            
        Returns:
            AudioSegment: Audio décompressé
        """
        print(f"📁 Décompression: {input_path}")
        
        # Lecture du fichier
        with open(input_path, 'rb') as f:
            header = f.read(36)
            sample_rate, length, num_pairs, max_val, mean, bits, channels, framerate, frame_width = \
                struct.unpack('!IIIffIIII', header)
            
            print(f"📊 Format: {channels} canaux, {framerate} Hz")
            
            huffman_size = struct.unpack('!I', f.read(4))[0]
            huffman_codes = pickle.loads(zlib.decompress(f.read(huffman_size)))
            
            encoded_bits = bitarray()
            encoded_bits.frombytes(f.read())
            
            # Décodage
            rle_data = huffman_decode_rle(encoded_bits, huffman_codes, num_pairs)
            residuals = rle_decode(rle_data, length)
            pcm_data = delta_decode(residuals)
        
        # Reconstruction du signal
        dequantized = dequantification(pcm_data, 256)
        denormalized = denormalisation(dequantized, max_val)
        decompressed = decompute_mean(denormalized, mean)

        # Interpolation
        demi_data = np.array(decompressed, dtype=float)
        moyennes = (demi_data[:-1] + demi_data[1:]) / 2
        resultat = np.empty(len(demi_data) + len(moyennes), dtype=np.dtype(f'int{bits}'))
        resultat[0::2] = demi_data
        resultat[1::2] = moyennes.astype(np.int16)

        if len(demi_data) % 2 == 0:
            resultat = np.append(resultat, demi_data[-1])
        resultat = resultat.astype(np.dtype(f'int{bits}'))

        # Reconstruction stéréo
        if channels == 2:
            imitated_stereo = Back_to_real_stereo(resultat, 'm')
        else:
            imitated_stereo = resultat

        audio = AudioSegment(
            data=imitated_stereo.tobytes(),
            sample_width=frame_width,
            frame_rate=framerate,
            channels=channels
        )

        print("✅ Décompression terminée")
        return audio