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


# --- Fonction pour générer une matrice inversible aléatoire ---
def generer_matrice_inversible(taille):
    """
    taille : taille de la matrice carrée (n)
    retourne : sympy.Matrix inversible dont le déterminant est premier avec 256
    """
    import random
    
    while True:
        # Générer une matrice aléatoire
        matrice = sp.Matrix(taille, taille, lambda i, j: random.randint(0, 255))
        
        # Calculer le déterminant
        det = int(matrice.det())
        
        # Vérifier si le déterminant est premier avec 256 (gcd(det, 256) == 1)
        if sp.gcd(det, 256) == 1:
            return matrice


# --- Fonction pour reconvertir un code Base64 en matrice SymPy ---
def base64_en_matrice(code_base64, taille=None):
    """
    code_base64 : texte Base64 représentant une matrice
    taille : taille de la matrice carrée (n) - si None, la taille est déterminée par la longueur de la clé
    retourne : sympy.Matrix reconstruite
    """
    # Décoder le Base64 en bytes
    matrice_bytes = base64.b64decode(code_base64)
    
    # Convertir les bytes en liste d'entiers
    liste_valeurs = list(matrice_bytes)
    
    # Déterminer la taille de la matrice en fonction de la longueur de la clé
    if taille is None:
        if len(code_base64) == 36:
            taille = 5
        elif len(code_base64) == 300:
            taille = 15
        elif len(code_base64) == 3336:
            taille = 50
        else:
            raise ValueError("Longueur de clé non supportée")
    
    # Recréer la matrice SymPy
    matrice = sp.Matrix(taille, taille, liste_valeurs)
    
    return matrice