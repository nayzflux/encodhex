# AES 256
from .key import key_expansion

# Chiffrement AES 256 (ECB)
# Chiffre un texte en clair avec une clé AES 256 bits
def encrypt(plaintext: str, key: str) -> str:
    # Gestion de la clé

    # Convertir la clé en octets
    key_bytes = key.encode()

    # Vérifier la longueur de la clé
    if len(key) != 32:
        raise ValueError("La clé doit être de 32 octets (256 bits).")

    # Générer les clés de ronde avec l'algorithme d'expansion de clé
    round_keys = key_expansion(key_bytes)

    # Gestion du texte en clair

    # Convertir le texte en clair en octets
    plaintext_bytes = plaintext.encode()

    # Compléter le texte en clair pour qu'il soit un multiple de 16
    padding_length = 16 - (len(plaintext_bytes) % 16)
    plaintext_bytes += bytes([padding_length] * padding_length)

    # Diviser le texte en blocs de 16 octets
    blocks = divide_blocks(plaintext_bytes)

    # Chiffrement de chaque bloc de 16 octets
    encrypted_blocks = []
    for block in blocks:
        # Transformer le bloc en matrice 4x4
        # Les 4 premiers octets forment la première colonne, les 4 suivants la deuxième, etc.
        mat = transform_block_to_matrix(block)

        # Round initial
        add_round_key(mat, round_keys[0])
        
        # 14 rounds
        for n in range(1, 14):
            substitute_bytes(mat)
            shift_rows(mat)
            mix_columns(mat)
            add_round_key(mat, round_keys[n])
        
        # Round final sans mix columns
        substitute_bytes(mat)
        shift_rows(mat)
        add_round_key(mat, round_keys[14])

        # Récupérer les octects chiffrés de la matrice
        encrypted_bytes = bytes(mat[i][j] for j in range(4) for i in range(4))

        # Ajouter le bloc chiffré à la liste des blocs chiffrés
        encrypted_blocks.append(encrypted_bytes)

    # Joindre tous les blocs chiffrés
    encrypted_bytes = b''.join(encrypted_blocks)

    # Gestion de texte chiffré
    encrypted_text = ""

    # Encoder les blocs chiffrés en hexadécimal
    encrypted_text = encrypted_bytes.hex()
    
    return encrypted_text

# Déchiffrement AES 256 (ECB)
# Déchiffre un texte chiffré avec une clé AES 256 bits
# Le texte chiffré doit être en hexadécimal
def decrypt(encrypted_text: str, key: str) -> str:
    # Gestion de la clé

    # Convertir la clé en octets
    key_bytes = key.encode()

    # Vérifier la longueur de la clé
    if len(key) != 32:
        raise ValueError("La clé doit être de 32 octets (256 bits).")

    # Générer les clés de ronde avec l'algorithme d'expansion de clé
    round_keys = key_expansion(key_bytes)

    # Gestion du texte chiffré

    # Convertir le texte chiffré en octets
    encrypted_bytes = bytes.fromhex(encrypted_text)

    # Diviser le texte chiffré en blocs de 16 octets
    blocks = divide_blocks(encrypted_bytes)

    # Déchiffrement de chaque bloc de 16 octets
    decrypted_blocks = []
    for block in blocks:
        # Transformer le bloc en matrice 4x4
        mat = transform_block_to_matrix(block)

        # Round initial
        add_round_key(mat, round_keys[14])
        
        # 14 rounds
        for n in range(13, 0, -1):
            inv_shift_rows(mat)
            inv_substitute_bytes(mat)
            add_round_key(mat, round_keys[n])
            inv_mix_columns(mat)
        
        # Round final sans mix columns
        inv_shift_rows(mat)
        inv_substitute_bytes(mat)
        add_round_key(mat, round_keys[0])

        # Récupérer les octects déchiffrés de la matrice
        decrypted_bytes = bytes(mat[i][j] for j in range(4) for i in range(4))

        # Ajouter le bloc déchiffré à la liste des blocs déchiffrés
        decrypted_blocks.append(decrypted_bytes)

    # Joindre tous les blocs déchiffrés
    decrypted_bytes = b''.join(decrypted_blocks)

    # Gestion de texte déchiffré
    decrypted_text = decrypted_bytes.hex()
    
    # Supprimer le remplissage
    padding_length = decrypted_bytes[-1]
    decrypted_bytes = decrypted_bytes[:-padding_length]

    # Convertir les octets déchiffrés en texte
    decrypted_text = decrypted_bytes.decode()

    return decrypted_text

# Table de substitution S-Box
S_BOX = [
        [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
        [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
        [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
        [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
        [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
        [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
        [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
        [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
        [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
        [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
        [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
        [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
        [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
        [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
        [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
        [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
]

INV_S_BOX = [
        [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb],
        [0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb],
        [0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e],
        [0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25],
        [0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92],
        [0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84],
        [0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06],
        [0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b],
        [0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73],
        [0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e],
        [0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b],
        [0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4],
        [0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f],
        [0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef],
        [0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61],
        [0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]
]

def divide_blocks(plain_bytes):
    # Diviser le texte en blocs de 16 octets
    blocks = []
    for i in range(0, len(plain_bytes), 16):
        # Prendre les octets de i à i+16
        block = plain_bytes[i:i + 16]
        blocks.append(block)
    return blocks

# Transformation des blocs en matrices 4x4
# Les 4 premiers octets forment la première colonne, les 4 suivants la deuxième, etc.
def transform_block_to_matrix(block):
    mat = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    # AES utilise un ordre par colonnes, pas par lignes
    for i in range(4):
        for j in range(4):
            mat[i][j] = block[j*4 + i]
    return mat

def substitute_bytes(mat):
    for i in range(4):
        for j in range(4):
            byte = mat[i][j]

            row = (byte >> 4) & 0x0F  # Partie haute (4 bits de gauche) = ligne
            col = byte & 0x0F         # Partie basse (4 bits de droite) = colonne

            sub_byte = S_BOX[row][col]

            mat[i][j] = sub_byte

# Inverser la substitution des octets
def inv_substitute_bytes(mat):
    for i in range(4):
        for j in range(4):
            byte = mat[i][j]

            row = (byte >> 4) & 0x0F  # Partie haute (4 bits de gauche) = ligne
            col = byte & 0x0F         # Partie basse (4 bits de droite) = colonne

            sub_byte = INV_S_BOX[row][col]

            mat[i][j] = sub_byte

# Décaler une ligne vers la gauche de n positions
def shift_row(row, n):
    return row[n:] + row[:n]

# Décaler une ligne vers la droite de n positions
def inv_shift_row(row, n):
    return row[-n:] + row[:-n]

# Décalage de toutes les lignes d'une matrice vers la gauche
# La première ligne ne bouge pas
# La deuxième ligne est décalée de 1 vers la gauche
# La troisième ligne est décalée de 2 vers la gauche
# La quatrième ligne est décalée de 3 vers la gauche
def shift_rows(mat):
    for i in range(4):
        # Décalage de la ligne i vers la gauche de i positions
        mat[i] = shift_row(mat[i], i)

# Inverser le décalage de toutes les lignes d'une matrice vers la droite
# La première ligne ne bouge pas
# La deuxième ligne est décalée de 1 vers la droite
# La troisième ligne est décalée de 2 vers la droite
# La quatrième ligne est décalée de 3 vers la droite
def inv_shift_rows(mat):
    for i in range(4):
        # Décalage de la ligne i vers la droite de i positions
        mat[i] = inv_shift_row(mat[i], i)

MIX_MATRIX = [
    [2, 3, 1, 1],
    [1, 2, 3, 1],
    [1, 1, 2, 3],
    [3, 1, 1, 2]
]

# Multiplication dans GF(2^8)
def galois_multiply(a, b):
    p = 0
    for _ in range(8):
        if b & 1:  # Si le bit le plus bas de b est 1
            p ^= a  # XOR avec a
        carry = a & 0x80  # Vérifier si le bit le plus significatif est 1
        a <<= 1  # Décalage à gauche
        if carry:  # Si le bit le plus significatif était 1
            a ^= 0x1b  # XOR avec le polynôme irréductible
        b >>= 1  # Décalage à droite
    return p & 0xFF  # Retourner les 8 bits de poids faible

# Multiplier une colonne par la matrice de mixage dans GF(2^8)
def mix_single_column(column):
    a = column[0]
    b = column[1]
    c = column[2]
    d = column[3]

    return [
        galois_multiply(a, 2) ^ galois_multiply(b, 3) ^ c ^ d,
        a ^ galois_multiply(b, 2) ^ galois_multiply(c, 3) ^ d,
        a ^ b ^ galois_multiply(c, 2) ^ galois_multiply(d, 3),
        galois_multiply(a, 3) ^ b ^ c ^ galois_multiply(d, 2)
    ]

# Multiplier chaque colonne de la matrice par la matrice de mixage
def mix_columns(matrix):
    for i in range(4):  # Pour chaque colonne
        column = [matrix[j][i] for j in range(4)]  # Extraire la colonne
        mixed_column = mix_single_column(column)  # Appliquer MixColumns
        for j in range(4):
            matrix[j][i] = mixed_column[j]  # Remettre la colonne dans la matrice

# Inverser la multiplication d'une colonne par la matrice de mixage dans GF(2^8)
def inv_mix_single_column(column):
    a = column[0]
    b = column[1]
    c = column[2]
    d = column[3]

    return [
        galois_multiply(a, 14) ^ galois_multiply(b, 11) ^ galois_multiply(c, 13) ^ galois_multiply(d, 9),
        galois_multiply(a, 9) ^ galois_multiply(b, 14) ^ galois_multiply(c, 11) ^ galois_multiply(d, 13),
        galois_multiply(a, 13) ^ galois_multiply(b, 9) ^ galois_multiply(c, 14) ^ galois_multiply(d, 11),
        galois_multiply(a, 11) ^ galois_multiply(b, 13) ^ galois_multiply(c, 9) ^ galois_multiply(d, 14)
    ]

# Inverser la multiplication de chaque colonne de la matrice par la matrice de mixage
def inv_mix_columns(matrix):
    for i in range(4):  # Pour chaque colonne
        column = [matrix[j][i] for j in range(4)]  # Extraire la colonne
        mixed_column = inv_mix_single_column(column)  # Appliquer InvMixColumns
        for j in range(4):
            matrix[j][i] = mixed_column[j]  # Remettre la colonne dans la matrice

# Ajouter la clé de ronde
def add_round_key(mat, round_key):
    for i in range(4):
        for j in range(4):
            mat[i][j] = mat[i][j] ^ round_key[i][j]