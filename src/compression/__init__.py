"""Module de compression audio"""

from .stereotreatment import process_stereo_sound, Back_to_real_stereo
from .quantification import (
    compute_mean, normalisation, quantification,
    dequantification, denormalisation, decompute_mean
)
from .encoding import (
    delta_encode, delta_decode, rle_encode, rle_decode,
    huffman_encode_rle, huffman_decode_rle
)
from .utils import taux_reduction

__all__ = [
    'process_stereo_sound', 'Back_to_real_stereo',
    'compute_mean', 'normalisation', 'quantification',
    'dequantification', 'denormalisation', 'decompute_mean',
    'delta_encode', 'delta_decode', 'rle_encode', 'rle_decode',
    'huffman_encode_rle', 'huffman_decode_rle',
    'taux_reduction'
]