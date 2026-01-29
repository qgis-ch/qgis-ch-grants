import os
import secrets
import string

# Konfiguration
ANZAHL_TOKENS = 200
TOKEN_LAENGE = 8
OUTPUT_FILE = "data/tokens.txt"

# Alphabet ohne ähnliche Zeichen (Kein I, l, 1, 0, O)
alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_tokens(n, length):
    tokens = set()
    while len(tokens) < n:
        token = ''.join(secrets.choice(alphabet) for _ in range(length))
        tokens.add(token)
    return list(tokens)

if __name__ == "__main__":
    tokens = generate_tokens(ANZAHL_TOKENS, TOKEN_LAENGE)
    
    for t in tokens:
        print(f"{t}")