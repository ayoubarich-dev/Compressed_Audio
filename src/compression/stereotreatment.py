"""
Module de traitement des signaux stéréo
Optimise la compression en détectant les canaux similaires
"""

import numpy as np


def channelsDistance(left, right):
    """
    Calcule les métriques de distance entre deux canaux audio.
    
    Args:
        left: Canal gauche
        right: Canal droit
        
    Returns:
        dict: Métriques de similarité entre les canaux
    """
    abs_diff = np.abs(left - right)
    mae = np.mean(abs_diff)
    correlation = np.corrcoef(left, right)[0, 1]
    
    # Ratio d'énergie dans la différence
    mono = (left + right) / 2
    diff_signal = left - right
    energy_ratio = np.sum(diff_signal**2) / np.sum(mono**2)

    metrics = {
        'mean_absolute_diff': mae,
        'correlation': correlation,
        'energy_ratio': energy_ratio,
        'recommend_mono': energy_ratio < 0.2
    }
    return metrics


def process_stereo_sound(stereo_array):
    """
    Traite un signal stéréo en analysant la distance entre canaux.
    
    Si les canaux sont similaires (energy_ratio < 0.2):
        - Mode mono: garde un seul canal
    Sinon:
        - Mode stéréo: encode left et (left-right)
    
    Args:
        stereo_array: Array stéréo entrelacé [L,R,L,R,...]
        
    Returns:
        tuple: (metadata, processed_array)
    """
    left = stereo_array[0::2]
    right = stereo_array[1::2]
    
    metrics = channelsDistance(left, right)

    if metrics["recommend_mono"]:
        # Canaux similaires -> mode mono
        return {'mode': 'm'}, left
    
    # Canaux différents -> encode left et différence
    new_arr = np.empty(len(stereo_array), dtype=stereo_array.dtype)
    new_arr[0::2] = left
    new_arr[1::2] = left - right
    return {'mode': 's'}, new_arr


def Back_to_real_stereo(array, mode):
    """
    Reconstruit le signal stéréo à partir du format compressé.
    
    Args:
        array: Signal traité
        mode: 'm' (mono) ou 's' (stéréo)
        
    Returns:
        np.ndarray: Signal stéréo reconstruit [L,R,L,R,...]
    """
    if mode == 'm':
        # Mode mono -> duplique le canal
        new_arr = np.empty(len(array) * 2, dtype=array.dtype)
        new_arr[0::2] = array
        new_arr[1::2] = array
    elif mode == 's':
        # Mode stéréo -> reconstruit à partir de left et différence
        new_arr = np.empty(len(array) * 2, dtype=array.dtype)
        left = array[0::2]
        diffright = array[1::2]
        right = left - diffright
        new_arr[0::2] = left
        new_arr[1::2] = right
    return new_arr