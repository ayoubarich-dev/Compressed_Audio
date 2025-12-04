import numpy as np


def compute_mean(sound_array):
    """Calcule et retire la moyenne du signal."""
    mean = np.mean(sound_array)
    centered_sound_arr = sound_array - mean
    return centered_sound_arr, mean


def normalisation(centered_sound_arr):
    """Normalise le signal entre -1 et 1."""
    saved_max = np.max(np.abs(centered_sound_arr))
    signal_normalized = centered_sound_arr / saved_max
    return signal_normalized, saved_max


def quantification(signal_normalized, L=256):
    """Quantifie le signal à L niveaux (par défaut 256 = 8 bits)."""
    signal_scaled = (signal_normalized + 1) / 2
    signal_quantized = np.round(signal_scaled * (L - 1)).astype(int)
    return signal_quantized


def dequantification(quantized_reconstructed, L=256):
    """Inverse la quantification."""
    signal_scaled_reconstructed = quantized_reconstructed / (L - 1)
    signal_normalized_reconstructed = (signal_scaled_reconstructed * 2) - 1
    return signal_normalized_reconstructed


def denormalisation(signal_normalized_reconstructed, saved_max):
    """Inverse la normalisation."""
    centered_reconstructed = signal_normalized_reconstructed * saved_max
    return centered_reconstructed


def decompute_mean(centered_reconstructed, mean):
    """Ajoute la moyenne pour reconstruire le signal original."""
    sound_reconstructed = centered_reconstructed + mean
    return sound_reconstructed