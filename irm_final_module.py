import numpy as np
from bitarray import bitarray
from collections import Counter
import heapq


def delta_encode(signal: np.ndarray) -> np.ndarray:
    """Encode le signal avec Delta encoding (stocke les différences)."""
    residuals = np.zeros_like(signal, dtype=np.int16)
    residuals[0] = signal[0]
    for i in range(1, len(signal)):
        residuals[i] = signal[i] - signal[i - 1]
    return residuals


def delta_decode(residuals: np.ndarray) -> np.ndarray:
    """Décode les résidus Delta pour reconstruire le signal."""
    signal = np.zeros_like(residuals, dtype=np.int16)
    signal[0] = residuals[0]
    for i in range(1, len(signal)):
        signal[i] = signal[i - 1] + residuals[i]
    return signal


def rle_encode(residuals: np.ndarray) -> list:
    """Encode avec RLE: [(valeur, nombre_répétitions), ...]"""
    if len(residuals) == 0:
        return []
    
    rle_data = []
    current_value = residuals[0]
    count = 1
    
    for value in residuals[1:]:
        if value == current_value and count < 32767:
            count += 1
        else:
            rle_data.append((current_value, count))
            current_value = value
            count = 1
    
    rle_data.append((current_value, count))
    return rle_data


def rle_decode(rle_data: list, total_length: int) -> np.ndarray:
    """Décode les données RLE."""
    residuals = []
    for value, count in rle_data:
        residuals.extend([value] * count)
    return np.array(residuals[:total_length], dtype=np.int16)


def build_huffman_tree(frequencies):
    """Construit l'arbre de Huffman."""
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
    """Génère les codes de Huffman à partir de l'arbre."""
    return {symbol: code for symbol, code in tree}


def huffman_encode_rle(rle_data: list) -> tuple:
    """Encode les paires RLE avec Huffman."""
    symbols = [f"{value},{count}" for value, count in rle_data]
    frequencies = Counter(symbols)
    
    tree = build_huffman_tree(frequencies)
    codes = generate_huffman_codes(tree)
    
    encoded = bitarray()
    for symbol in symbols:
        encoded.extend(codes[symbol])
    
    return encoded, codes


def huffman_decode_rle(encoded_bits: bitarray, huffman_codes: dict, total_pairs: int) -> list:
    """Décode le flux de bits Huffman vers des paires RLE."""
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