import sys, hashlib

def load(p):
    """TLC -dump texte : un état = en-tête 'State N:' (ignoré, ordinal propre au run)
    + lignes corps '/\\ var = valeur'. Le dump contient des doublons -> set."""
    states, cur = set(), []
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("State ") and line.rstrip().endswith(":"):
                if cur:
                    states.add(hashlib.md5("".join(cur).encode()).digest())
                cur = []
            elif line.strip():
                cur.append(line)
        if cur:
            states.add(hashlib.md5("".join(cur).encode()).digest())
    return states

A = load(sys.argv[1])   # dump_avant.txt.dump
B = load(sys.argv[2])   # dump_apres.txt.dump
i = len(A & B)
print(f"|avant| distinct = {len(A):,}")
print(f"|apres| distinct = {len(B):,}")
print(f"|intersection|   = {i:,}")
print(f"reuse vs espace nouveau : {i/len(B):.1%}")
print(f"reuse vs espace ancien  : {i/len(A):.1%}")
