import sympy as sp
import base64

# --- Fonction pour convertir une matrice en Base64 ---
def matrice_en_base64(matrice):
    """
    matrice : sympy.Matrix carrée
    retourne : texte Base64 représentant la matrice (lisible et partageable)
    """
    # Convertir la matrice en liste d'entiers
    liste_valeurs = [int(matrice[i, j]) for i in range(matrice.rows) for j in range(matrice.cols)]
    
    # Convertir les entiers en bytes (0-255)
    matrice_bytes = bytes(liste_valeurs)
    
    # Encoder en Base64
    matrice_base64 = base64.b64encode(matrice_bytes).decode('ascii')
    
    return matrice_base64


# --- Fonction pour reconvertir un code Base64 en matrice SymPy ---
def base64_en_matrice(code_base64, taille):
    """
    code_base64 : texte Base64 représentant une matrice
    taille : taille de la matrice carrée (n)
    retourne : sympy.Matrix reconstruite
    """
    # Décoder le Base64 en bytes
    matrice_bytes = base64.b64decode(code_base64)
    
    # Convertir les bytes en liste d'entiers
    liste_valeurs = list(matrice_bytes)
    
    # Recréer la matrice SymPy
    matrice = sp.Matrix(taille, taille, liste_valeurs)
    
    return matrice