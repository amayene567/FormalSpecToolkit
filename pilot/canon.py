#!/usr/bin/env python3
r"""
canon.py - canonicalize TLC state dumps modulo a symmetry on model values.

Reads a TLC dump (produced with -dump), where each state is a block:
    State 17:
    /\ var1 = value
    /\ var2 = value that may wrap
       onto continuation lines
    (blank line)

For each state it prints one MD5 hash (hex) of a canonical form:
  - values are parsed (sets, sequences, functions a :> b @@ ..., records),
  - sets and function domains are re-sorted after renaming,
  - the minimum serialization over all permutations of SERVERS is kept.

Usage:
  python3 canon.py DUMP [--limit N] [--no-perm] > hashes.txt
    --limit N   only process the first N states (for tests)
    --no-perm   normalize only, no permutation (sanity check: should
                reproduce the old textual intersection)
Progress is written to stderr every 200,000 states.
"""
import sys, re, hashlib, itertools, argparse

SERVERS = ["n1", "n2", "n3"]   # model values of CONSTANT Server in the .cfg

TOKEN_RE = re.compile(r'\s*(<<|>>|:>|@@|\|->|"(?:[^"\\]|\\.)*"|[{}()\[\],]|[^\s{}()\[\],<>:@|"]+)')

def tokenize(s):
    pos, out = 0, []
    s = s.strip()
    while pos < len(s):
        m = TOKEN_RE.match(s, pos)
        if not m:
            raise ValueError("cannot tokenize at: %r" % s[pos:pos + 40])
        out.append(m.group(1))
        pos = m.end()
    return out

class Parser:
    def __init__(self, toks):
        self.t, self.i = toks, 0
    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None
    def next(self):
        tok = self.t[self.i]; self.i += 1; return tok
    def expect(self, x):
        tok = self.next()
        if tok != x:
            raise ValueError("expected %r, got %r" % (x, tok))
    def value(self):
        tok = self.next()
        if tok == "{":
            items = []
            if self.peek() != "}":
                items.append(self.value())
                while self.peek() == ",":
                    self.next(); items.append(self.value())
            self.expect("}")
            return ("set", tuple(items))
        if tok == "<<":
            items = []
            if self.peek() != ">>":
                items.append(self.value())
                while self.peek() == ",":
                    self.next(); items.append(self.value())
            self.expect(">>")
            return ("seq", tuple(items))
        if tok == "(":
            pairs = []
            k = self.value(); self.expect(":>"); v = self.value()
            pairs.append((k, v))
            while self.peek() == "@@":
                self.next()
                k = self.value(); self.expect(":>"); v = self.value()
                pairs.append((k, v))
            self.expect(")")
            return ("fun", tuple(pairs))
        if tok == "[":
            fields = []
            if self.peek() != "]":
                name = self.next(); self.expect("|->"); fields.append((name, self.value()))
                while self.peek() == ",":
                    self.next()
                    name = self.next(); self.expect("|->"); fields.append((name, self.value()))
            self.expect("]")
            return ("rec", tuple(fields))
        return ("atom", tok)

def parse_value(s):
    p = Parser(tokenize(s))
    v = p.value()
    if p.peek() is not None:
        raise ValueError("trailing tokens in %r" % s[:80])
    return v

def ser(v, ren):
    kind, x = v
    if kind == "atom":
        return ren.get(x, x)
    if kind == "set":
        return "{" + ",".join(sorted(ser(e, ren) for e in x)) + "}"
    if kind == "seq":
        return "<<" + ",".join(ser(e, ren) for e in x) + ">>"
    if kind == "fun":
        return "(" + "@@".join(sorted(ser(k, ren) + ":>" + ser(w, ren) for k, w in x)) + ")"
    if kind == "rec":
        return "[" + ",".join(sorted(n + "|->" + ser(w, ren) for n, w in x)) + "]"
    raise ValueError(kind)

def state_blocks(path):
    """Yield list of (var, value_string) per state, joining wrapped lines."""
    cur, var_lines = None, []
    def flush():
        out = []
        for line in var_lines:
            body = line[3:] if line.startswith("/\\ ") else line
            name, _, val = body.partition(" = ")
            out.append((name.strip(), val))
        return out
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.startswith("State ") and line.rstrip().endswith(":"):
                if cur is not None:
                    yield flush()
                cur, var_lines = line, []
            elif not line.strip():
                continue
            elif line.startswith("/\\ "):
                var_lines.append(line)
            else:
                if not var_lines:
                    raise ValueError("continuation line before any variable: %r" % line[:80])
                var_lines[-1] += " " + line.strip()
        if cur is not None:
            yield flush()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-perm", action="store_true")
    a = ap.parse_args()
    perms = [dict()] if a.no_perm else \
        [dict(zip(SERVERS, p)) for p in itertools.permutations(SERVERS)]
    out = sys.stdout
    n = 0
    for block in state_blocks(a.dump):
        parsed = sorted((name, parse_value(val)) for name, val in block)
        best = min("|".join(name + "=" + ser(v, ren) for name, v in parsed) for ren in perms)
        out.write(hashlib.md5(best.encode()).hexdigest() + "\n")
        n += 1
        if n % 200000 == 0:
            print("%d states" % n, file=sys.stderr, flush=True)
        if a.limit and n >= a.limit:
            break
    print("done: %d states" % n, file=sys.stderr)

if __name__ == "__main__":
    main()