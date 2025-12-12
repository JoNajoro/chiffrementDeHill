import sympy as sp
import base64

# --- Fonction de chiffrement Hill ANSI + Base64 ---
def hill_chiffrement_ansi_base64(matrice_cle, message):
    """
    matrice_cle : sympy.Matrix carrée (n x n)
    message : texte (ANSI 0-255)
    
    retourne : texte chiffré encodé en Base64 et longueur originale du message
    """
    taille = matrice_cle.shape[0]

    # Convertir chaque caractère en code ANSI (0-255)
    message_codes = [ord(c) for c in message]

    # Ajouter des espaces pour que la longueur soit multiple de la taille de la matrice
    while len(message_codes) % taille != 0:
        message_codes.append(ord(' '))

    texte_chiffre = ""
    for i in range(0, len(message_codes), taille):
        bloc = sp.Matrix(message_codes[i:i+taille])
        bloc_chiffre = (matrice_cle * bloc) % 256
        texte_chiffre += ''.join([chr(int(c)) for c in bloc_chiffre])

    # Encoder en Base64 pour rendre le texte lisible
    texte_chiffre_bytes = bytes([ord(c) for c in texte_chiffre])
    texte_chiffre_base64 = base64.b64encode(texte_chiffre_bytes).decode('ascii')

    # Retourner le texte chiffré et la longueur originale
    return texte_chiffre_base64, len(message)


# --- Fonction de déchiffrement Hill ANSI + Base64 ---
def hill_dechiffrement_ansi_base64(matrice_cle, texte_chiffre_base64):
    """
    matrice_cle : sympy.Matrix carrée (n x n)
    texte_chiffre_base64 : texte chiffré encodé en Base64
    
    retourne : texte déchiffré (ANSI 0-255)
    """
    taille = matrice_cle.shape[0]

    # Décoder le Base64 pour récupérer les caractères chiffrés
    texte_chiffre_bytes = base64.b64decode(texte_chiffre_base64)
    texte_chiffre = ''.join([chr(b) for b in texte_chiffre_bytes])

    # Convertir en codes ANSI
    texte_codes = [ord(c) for c in texte_chiffre]

    # Calculer l'inverse modulo 256 de la matrice clé
    matrice_inverse = matrice_cle.inv_mod(256)

    texte_dechiffre = ""
    for i in range(0, len(texte_codes), taille):
        bloc = sp.Matrix(texte_codes[i:i+taille])
        bloc_dechiffre = (matrice_inverse * bloc) % 256
        texte_dechiffre += ''.join([chr(int(c)) for c in bloc_dechiffre])

    # Supprimer les éventuels espaces ajoutés pour le padding
    return texte_dechiffre.rstrip()
