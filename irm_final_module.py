import librosa
from bitarray import bitarray
import os
import struct
import pickle
from collections import Counter
import heapq
import scipy
import zlib
import numpy as np
ALLOWED_SIZES = [512, 1024, 2048]

def compute_zcr(window: np.ndarray) -> float:
    sign_changes = np.sum(np.diff(np.sign(window)) != 0)
    return sign_changes / len(window)

def compute_mad(window: np.ndarray) -> float:
    median_value = np.median(window)
    return np.median(np.abs(window - median_value))

def compute_variance(window: np.ndarray) -> float:
    return np.var(window)

def compute_spectral_centroid(window: np.ndarray, nyquist_freq: float) -> float:
    window = np.asarray(window, dtype=float)
    window *= np.hamming(len(window))  # Apply Hamming window
    fft = np.abs(np.fft.rfft(window))
    if np.sum(fft) > 1e-10:  # Avoid numerical instability
        freqs = np.linspace(0, nyquist_freq, len(fft))
        return np.sum(freqs * fft) / np.sum(fft)
    return 0
    
def compute_metrics(window: np.ndarray, nyquist_freq: float) -> dict:

    if len(window) == 0:
        raise ValueError("Input window must not be empty.")
    if nyquist_freq <= 0:
        raise ValueError("Nyquist frequency must be positive.")

    window = np.asarray(window, dtype=float)
    
    # Initialize metrics
    metrics = {
        'variance': compute_variance(window),
        'zcr': np.nan,
        'mad': np.nan,
        'spectral_centroid': np.nan
    }
    
    if len(window) > 1:
        metrics['zcr'] = compute_zcr(window)
        metrics['mad'] = compute_mad(window)
    if len(window) >= 512:
        metrics['spectral_centroid'] = compute_spectral_centroid(window, nyquist_freq)
    return metrics

def prepare_audio_signal(pcm_array: np.ndarray) -> np.ndarray:
    """
    Preprocess the input PCM audio signal by normalizing and centering it.
    
    Steps:
        1. Convert the signal to floating-point values.
        2. Remove DC offset (center the signal around zero).
        3. Normalize the signal to the range [-1, 1].
    
    Parameters:
        pcm_array (np.ndarray): Input audio signal as a 1D array of PCM samples.
    
    Returns:
        np.ndarray: Preprocessed audio signal as a normalized 1D NumPy array.
    """
    # Validate input
    if not isinstance(pcm_array, np.ndarray) or pcm_array.ndim != 1:
        raise ValueError("Input PCM array must be a 1D NumPy array.")
    
    # Convert to float
    pcm_array = pcm_array.astype(float)
    
    # Remove DC offset (center the signal around zero)
    mean_value = np.mean(pcm_array)
    centered = pcm_array - mean_value
    
    # Normalize to [-1, 1]
    max_amplitude = np.max(np.abs(centered))
    normalized = centered / max_amplitude if max_amplitude > 0 else centered
    
    return normalized
    
def compute_dynamic_thresholds(preprocessed_audio: np.ndarray, sample_rate: int = 44100,
                               zcr_limits=(0.05, 0.1), mad_limits=(0.001, 0.01),
                               variance_limits=(1e-6, 1e-4)) -> dict:
    """
    Compute dynamic thresholds for various audio metrics based on the preprocessed audio signal.
    
    Parameters:
        preprocessed_audio (np.ndarray): Preprocessed audio signal as a 1D NumPy array.
        sample_rate (int): Sampling rate of the audio signal (default: 44100 Hz).
        zcr_limits (tuple): Sensible limits for zero-crossing rate thresholds.
        mad_limits (tuple): Sensible limits for median absolute deviation thresholds.
        variance_limits (tuple): Sensible limits for variance thresholds.
    
    Returns:
        dict: A dictionary containing robust thresholds for each metric.
    """
    # Validate inputs
    if not isinstance(preprocessed_audio, np.ndarray) or preprocessed_audio.ndim != 1:
        raise ValueError("Preprocessed audio must be a 1D NumPy array.")
    if sample_rate <= 0:
        raise ValueError("Sample rate must be positive.")
    
    # Recompute metrics with preprocessed audio
    metric_ranges = {'zcr': [], 'mad': [], 'variance': [], 'spectral_centroid': []}
    for pos in range(0, len(preprocessed_audio), 512):
        segment = preprocessed_audio[pos:min(len(preprocessed_audio), pos + 512)]
        if len(segment) > 1:  # Require at least two samples
            metrics = compute_metrics(segment, sample_rate / 2)
            for key in metric_ranges:
                metric_ranges[key].append(metrics[key])
    
    # Calculate robust thresholds (ignore outliers)
    def get_robust_range(values, lower_percentile=5, upper_percentile=95):
        q_low, q_high = np.percentile(values, [lower_percentile, upper_percentile])
        return {
            'stable': float(q_low * 0.9),  # Conservative stable
            'complex': float(q_high * 1.1)  # Lenient complex
        }
    
    THRESHOLDS = {
        'zcr': get_robust_range(metric_ranges['zcr'], lower_percentile=5, upper_percentile=95),
        'mad': get_robust_range(metric_ranges['mad'], lower_percentile=10, upper_percentile=90),
        'variance': get_robust_range(metric_ranges['variance'], lower_percentile=10, upper_percentile=90)
    }
    
    # Handle spectral centroid separately
    sc_values = metric_ranges['spectral_centroid']
    sc_values = [v for v in sc_values if not np.isnan(v)]  # Remove NaN values
    if sc_values:
        sc_median = np.median(sc_values)
        THRESHOLDS['spectral_centroid'] = {
            'stable': max(sc_median * 0.5, 100),  # Conservative stable
            'complex': min(sc_median * 1.5, sample_rate / 2)  # Lenient complex
        }
    else:
        THRESHOLDS['spectral_centroid'] = {'stable': 100, 'complex': sample_rate / 2}  # Default values
    
    # Apply sensible limits
    THRESHOLDS['zcr'].update({
        'stable': min(THRESHOLDS['zcr']['stable'], zcr_limits[0]),
        'complex': max(THRESHOLDS['zcr']['complex'], zcr_limits[1])
    })
    THRESHOLDS['mad'].update({
        'stable': min(THRESHOLDS['mad']['stable'], mad_limits[0]),
        'complex': max(THRESHOLDS['mad']['complex'], mad_limits[1])
    })
    THRESHOLDS['variance'].update({
        'stable': min(THRESHOLDS['variance']['stable'], variance_limits[0]),
        'complex': max(THRESHOLDS['variance']['complex'], variance_limits[1])
    })
    
    # Debugging: Print computed thresholds
    print("Computed Thresholds:", THRESHOLDS)
    
    return THRESHOLDS
    

def split_audio(preprocessed_audio: np.ndarray, sample_rate: int = 44100) -> list:
    """
    Split the preprocessed audio into partitions of varying sizes based on dynamic thresholds.
    
    Parameters:
        preprocessed_audio (np.ndarray): Preprocessed audio signal as a 1D NumPy array.
        sample_rate (int): Sampling rate of the audio signal (default: 44100 Hz).
    
    Returns:
        list: A list of dictionaries representing the partitions.
    """
    # Compute dynamic thresholds
    THRESHOLDS = compute_dynamic_thresholds(preprocessed_audio, sample_rate)
    print("Dynamic Thresholds:", THRESHOLDS)
    
    # Initialize variables
    partitions = []
    current_pos = 0
    step_size = 512  # Step size for sliding window
    
    # Track the count of each partition size
    size_counts = {512: 0, 1024: 0, 2048: 0}
    
    while current_pos < len(preprocessed_audio):
        # Compute metrics for overlapping windows
        avg_metrics = {'zcr': [], 'mad': [], 'variance': [], 'spectral_centroid': []}
        for pos in range(current_pos, current_pos + 1024, step_size):
            segment = preprocessed_audio[pos:min(len(preprocessed_audio), pos + step_size)]
            if len(segment) > 1:  # Require at least two samples
                metrics = compute_metrics(segment, sample_rate / 2)
                for key in avg_metrics:
                    avg_metrics[key].append(metrics[key])
        
        # Average metrics over the window
        avg_metrics = {key: np.mean(values) for key, values in avg_metrics.items()}
        
        # Determine partition size based on thresholds
        is_complex = (
            avg_metrics['zcr'] > THRESHOLDS['zcr']['complex'] or
            avg_metrics['mad'] > THRESHOLDS['mad']['complex'] or
            avg_metrics['variance'] > THRESHOLDS['variance']['complex']
        )
        is_stable = (
            avg_metrics['zcr'] < THRESHOLDS['zcr']['stable'] and
            avg_metrics['mad'] < THRESHOLDS['mad']['stable'] and
            avg_metrics['variance'] < THRESHOLDS['variance']['stable']
        )
        
        if is_complex:
            chosen_size = 512
            print(f"Complex segment detected at {current_pos}, size={chosen_size}")
        elif is_stable:
            chosen_size = 2048
            print(f"Stable segment detected at {current_pos}, size={chosen_size}")
        else:
            chosen_size = 1024
            print(f"Default segment detected at {current_pos}, size={chosen_size}")
        
        # Update size counts
        size_counts[chosen_size] += 1
        
        # Add partition to the list
        partitions.append({
            'start': current_pos,
            'size': chosen_size,
            'original_length': min(chosen_size, len(preprocessed_audio) - current_pos),  # True data length
            'metrics': avg_metrics
        })
        
        # Move to the next position
        current_pos += chosen_size
    
    # Calculate total number of segments
    total_segments = sum(size_counts.values())
    
    # Compute and print percentages for each size
    print("\nPartition Size Distribution:")
    for size, count in size_counts.items():
        percentage = (count / total_segments) * 100 if total_segments > 0 else 0
        print(f"Size {size}: {count} segments ({percentage:.2f}%)")
    
    return partitions

def reconstruct_audio(partitions: list, pcm_array: np.ndarray) -> np.ndarray:
    """Rebuild original audio from partitions using original_length."""
    reconstructed = []
    for p in partitions:
        start = p['start']
        end = start + p['original_length']  # Ignore any padding
        chunk = pcm_array[start:end].copy()
        reconstructed.append(chunk)
    return np.concatenate(reconstructed)

def delta_encode(signal: np.ndarray) -> np.ndarray:
    """Encode signal using Delta encoding."""
    residuals = np.zeros_like(signal, dtype=np.int16)
    residuals[0] = signal[0]
    for i in range(1, len(signal)):
        residuals[i] = signal[i] - signal[i - 1]
    return residuals

def delta_decode(residuals: np.ndarray) -> np.ndarray:
    """Decode Delta residuals back to original signal."""
    signal = np.zeros_like(residuals, dtype=np.int16)
    signal[0] = residuals[0]
    for i in range(1, len(signal)):
        signal[i] = signal[i - 1] + residuals[i]
    return signal
def rle_encode(residuals: np.ndarray) -> list[tuple[int, int]]:
    """Encode residuals with RLE: (value, count)."""
    if len(residuals) == 0:
        return []
    
    rle_data = []
    current_value = residuals[0]
    count = 1
    
    for value in residuals[1:]:
        if value == current_value and count < 32767:  # Limit count to fit in int16
            count += 1
        else:
            rle_data.append((current_value, count))
            current_value = value
            count = 1
    
    rle_data.append((current_value, count))
    return rle_data

def rle_decode(rle_data: list[tuple[int, int]], total_length: int) -> np.ndarray:
    """Decode RLE data back to residuals."""
    residuals = []
    for value, count in rle_data:
        residuals.extend([value] * count)
    return np.array(residuals[:total_length], dtype=np.int16)
from bitarray import bitarray

def huffman_encode_rle(rle_data: list[tuple[int, int]]) -> tuple[bitarray, dict]:
    """Huffman encode RLE (value, count) pairs."""
    # Convert tuples to strings for unique symbols
    symbols = [f"{value},{count}" for value, count in rle_data]
    frequencies = Counter(symbols)
    
    tree = build_huffman_tree(frequencies)
    codes = generate_huffman_codes(tree)
    
    encoded = bitarray()
    for symbol in symbols:
        encoded.extend(codes[symbol])
    
    return encoded, codes

def huffman_decode_rle(encoded_bits: bitarray, huffman_codes: dict, total_pairs: int) -> list[tuple[int, int]]:
    """Decode Huffman bitstream back to RLE pairs."""
    code_to_symbol = {code: symbol for symbol, code in huffman_codes.items()}
    decoded = []
    current_code = ''
    
    for bit in encoded_bits:
        current_code += '1' if bit else '0'
        if current_code in code_to_symbol:
            symbol = code_to_symbol[current_code]
            value, count = map(int, symbol.split(','))
            decoded.append((value, count))
            current_code = ''
        if len(decoded) >= total_pairs:
            break
    
    return decoded
    
def write_compressed_audio(filename: str, pcm_data: np.ndarray, sample_rate: int):
    """Write compressed audio using Delta + RLE + Huffman."""
    residuals = delta_encode(pcm_data)
    rle_data = rle_encode(residuals)
    encoded_bits, huffman_codes = huffman_encode_rle(rle_data)
    
    header = struct.pack('!III', sample_rate, len(pcm_data), len(rle_data))
    huffman_bytes = zlib.compress(pickle.dumps(huffman_codes))
    
    with open(filename, 'wb') as f:
        f.write(header)  # 12 bytes
        f.write(struct.pack('!I', len(huffman_bytes)))
        f.write(huffman_bytes)
        f.write(encoded_bits.tobytes())
    
    print(f"Bitstream size: {len(encoded_bits)} bits ({len(encoded_bits.tobytes())} bytes)")

def read_compressed_audio(filename: str) -> np.ndarray:
    """Read and decompress audio."""
    with open(filename, 'rb') as f:
        header = f.read(12)
        sample_rate, length, num_pairs = struct.unpack('!III', header)
        
        huffman_size = struct.unpack('!I', f.read(4))[0]
        huffman_codes = pickle.loads(zlib.decompress(f.read(huffman_size)))
        
        encoded_bits = bitarray()
        encoded_bits.frombytes(f.read())
        rle_data = huffman_decode_rle(encoded_bits, huffman_codes, num_pairs)
        residuals = rle_decode(rle_data, length)
        pcm_data = delta_decode(residuals)
    
    return pcm_data, sample_rate
def write_compressed_audio(filename: str, pcm_data: np.ndarray, sample_rate: int):
    """Write compressed audio using Delta + RLE + Huffman."""
    residuals = delta_encode(pcm_data)
    rle_data = rle_encode(residuals)
    encoded_bits, huffman_codes = huffman_encode_rle(rle_data)
    
    header = struct.pack('!III', sample_rate, len(pcm_data), len(rle_data))
    huffman_bytes = zlib.compress(pickle.dumps(huffman_codes))
    
    with open(filename, 'wb') as f:
        f.write(header)  # 12 bytes
        f.write(struct.pack('!I', len(huffman_bytes)))
        f.write(huffman_bytes)
        f.write(encoded_bits.tobytes())
    
    print(f"Bitstream size: {len(encoded_bits)} bits ({len(encoded_bits.tobytes())} bytes)")

def read_compressed_audio(filename: str) -> np.ndarray:
    """Read and decompress audio."""
    with open(filename, 'rb') as f:
        header = f.read(12)
        sample_rate, length, num_pairs = struct.unpack('!III', header)
        
        huffman_size = struct.unpack('!I', f.read(4))[0]
        huffman_codes = pickle.loads(zlib.decompress(f.read(huffman_size)))
        
        encoded_bits = bitarray()
        encoded_bits.frombytes(f.read())
        rle_data = huffman_decode_rle(encoded_bits, huffman_codes, num_pairs)
        residuals = rle_decode(rle_data, length)
        pcm_data = delta_decode(residuals)
    
    return pcm_data, sample_rate
def build_huffman_tree(frequencies):
    heap = [[weight, [symbol, ""]] for symbol, weight in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heap[0][1:], key=lambda p: (len(p[-1]), p))

def generate_huffman_codes(tree):
    return {symbol: code for symbol, code in tree}

# Compression Algorithms
def huffman_compress(residuals: np.ndarray) -> tuple[bitarray, dict]:
    freq = Counter(residuals)
    tree = build_huffman_tree(freq)
    codes = generate_huffman_codes(tree)
    encoded = bitarray()
    for r in residuals:
        encoded.extend(codes[r])
    return encoded, codes

def huffman_decode(encoded_bits: bitarray, huffman_codes: dict, length: int) -> list:
    code_to_symbol = {code: symbol for symbol, code in huffman_codes.items()}
    decoded = []
    current_code = ''
    for bit in encoded_bits:
        current_code += '1' if bit else '0'
        if current_code in code_to_symbol:
            decoded.append(code_to_symbol[current_code])
            current_code = ''
        if len(decoded) >= length:
            break
    return decoded