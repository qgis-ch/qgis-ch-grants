import secrets
import string

# Konfiguration
ANZAHL_TOKENS = 200
TOKEN_LAENGE = 8
OUTPUT_FILE = 'tokens.txt'

# Alphabet ohne ähnliche Zeichen (Kein I, l, 1, 0, O)
alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_tokens(n, length):
    tokens = set()
    while len(tokens) < n:
        token = ''.join(secrets.choice(alphabet) for _ in range(length))
        tokens.add(token)
    return list(tokens)

if __name__ == "__main__":
    print(f"Generiere {ANZAHL_TOKENS} eindeutige Tokens...")
    tokens = generate_tokens(ANZAHL_TOKENS, TOKEN_LAENGE)
    
    with open(OUTPUT_FILE, 'w') as f:
        for t in tokens:
            f.write(f"{t}\n")
            
    print(f"Fertig! {len(tokens)} Tokens in '{OUTPUT_FILE}' gespeichert.")
    print(f"Beispiel: {tokens[0]}")
