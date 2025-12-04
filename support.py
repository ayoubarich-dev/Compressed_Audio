import numpy as np
import os

def taux_reduction(original, compresse):
    """Calcule le taux de compression entre deux fichiers."""
    taille1 = os.path.getsize(original)
    taille2 = os.path.getsize(compresse)
    return np.round((1 - taille2 / taille1) * 100, 2)