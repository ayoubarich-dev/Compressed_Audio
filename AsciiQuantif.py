import numpy as np
def compute_mean(sound_array):
    # Compute mean amplitude
    mean = np.mean(sound_array)
    centered_sound_arr = sound_array - mean
    return centered_sound_arr,mean
def normalisation(centered_sound_arr):
    # Normalisation
    saved_max=np.max(np.abs(centered_sound_arr))
    signal_normalized = centered_sound_arr / saved_max
    return signal_normalized,saved_max
def quantification(signal_normalized,L = 256):
    # Requantification à 8 bits
    signal_scaled = (signal_normalized + 1) / 2  # mise à l’échelle dans [0, 1]
    signal_quantized = np.round(signal_scaled * (L - 1)).astype(int)  # quantification
    return signal_quantized
def signal_to_text(signal_quantized):
    ascii_text = ''.join([chr(num) for num in signal_quantized.astype(int)])
    return ascii_text
def text_to_signal(ascii_text):
    # 1. Convert ASCII back to quantized values
    quantized_reconstructed = np.array([ord(char) for char in ascii_text])
    return quantized_reconstructed
def dequantification(quantized_reconstructed,L):
    # 2. Reverse the 8-bit quantization
    signal_scaled_reconstructed = quantized_reconstructed / (L - 1)  # Scale to [0, 1]
    signal_normalized_reconstructed = (signal_scaled_reconstructed * 2) - 1  # Scale to [-1, 1]
    return signal_normalized_reconstructed
def denormalisation(signal_normalized_reconstructed,saved_max):
    # 3. Denormalize using the saved maximum amplitude
    centered_reconstructed = signal_normalized_reconstructed * saved_max
    return centered_reconstructed
def decompute_mean(centered_reconstructed,mean):
    # 4. Add back the mean to reconstruct original signal
    sound_reconstructed = centered_reconstructed + mean
    return sound_reconstructed
