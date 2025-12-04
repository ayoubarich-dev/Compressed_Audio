"""
Module de quantification des signaux audio
Prépare le signal pour la compression en réduisant sa précision
"""

import numpy as np


def compute_mean(sound_array):
    """
    Calcule et retire la moyenne du signal (centrage).
    
    Args:
        sound_array: Signal audio original
        
    Returns:
        tuple: (signal_centré, moyenne)
    """
    mean = np.mean(sound_array)
    centered_sound_arr = sound_array - mean
    return centered_sound_arr, mean


def normalisation(centered_sound_arr):
    """
    Normalise le signal entre -1 et 1.
    
    Args:
        centered_sound_arr: Signal centré
        
    Returns:
        tuple: (signal_normalisé, valeur_max)
    """
    saved_max = np.max(np.abs(centered_sound_arr))
    signal_normalized = centered_sound_arr / saved_max
    return signal_normalized, saved_max


def quantification(signal_normalized, L=256):
    """
    Quantifie le signal à L niveaux (par défaut 256 = 8 bits).
    
    Réduit la précision du signal pour faciliter la compression.
    
    Args:
        signal_normalized: Signal normalisé [-1, 1]
        L: Nombre de niveaux de quantification
        
    Returns:
        np.ndarray: Signal quantifié [0, L-1]
    """
    signal_scaled = (signal_normalized + 1) / 2  # [-1,1] -> [0,1]
    signal_quantized = np.round(signal_scaled * (L - 1)).astype(int)
    return signal_quantized


def dequantification(quantized_reconstructed, L=256):
    """
    Inverse la quantification.
    
    Args:
        quantized_reconstructed: Signal quantifié [0, L-1]
        L: Nombre de niveaux utilisés
        
    Returns:
        np.ndarray: Signal normalisé [-1, 1]
    """
    signal_scaled_reconstructed = quantized_reconstructed / (L - 1)
    signal_normalized_reconstructed = (signal_scaled_reconstructed * 2) - 1
    return signal_normalized_reconstructed


def denormalisation(signal_normalized_reconstructed, saved_max):
    """
    Inverse la normalisation.
    
    Args:
        signal_normalized_reconstructed: Signal normalisé [-1, 1]
        saved_max: Valeur maximale sauvegardée
        
    Returns:
        np.ndarray: Signal dénormalisé
    """
    centered_reconstructed = signal_normalized_reconstructed * saved_max
    return centered_reconstructed


def decompute_mean(centered_reconstructed, mean):
    """
    Ajoute la moyenne pour reconstruire le signal original.
    
    Args:
        centered_reconstructed: Signal centré
        mean: Moyenne sauvegardée
        
    Returns:
        np.ndarray: Signal reconstruit
    """
    sound_reconstructed = centered_reconstructed + mean
    return sound_reconstructed