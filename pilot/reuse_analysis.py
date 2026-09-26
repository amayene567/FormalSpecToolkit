import sys, hashlib

def load(p):
    s = set()
    with open(p, encoding="utf-8", errors="replace") as f:
        for l in f:
            l = l.strip()
            if l:
                s.add(hashlib.md5(l.encode()).digest())
    return s

A = load(sys.argv[1])   # dump_avant.txt
B = load(sys.argv[2])   # dump_apres.txt
i = len(A & B)
print(f"|avant|        = {len(A):,}")
print(f"|apres|        = {len(B):,}")
print(f"|intersection| = {i:,}")
print(f"reuse vs espace nouveau : {i/len(B):.1%}")
print(f"reuse vs espace ancien  : {i/len(A):.1%}")
