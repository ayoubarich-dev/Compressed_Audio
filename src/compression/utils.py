"""
Fonctions utilitaires pour la compression audio
"""

import numpy as np
import os

def taux_reduction(original, compresse):
    
    taille_originale = os.path.getsize(original)
    taille_compressee = os.path.getsize(compresse)
    
    taux = (1 - taille_compressee / taille_originale) * 100
    
    return np.round(taux, 2)