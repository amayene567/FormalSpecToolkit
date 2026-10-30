#!/usr/bin/env bash
# Regenerates pilot/specs/ from mongodb/mongo. The MongoDB specifications are not
# redistributed in this repository (see README).
# Usage (from the repository root): pilot/fetch_specs.sh /path/to/mongo-clone [OUTDIR]
set -euo pipefail
REPO="$1"; OUT="${2:-pilot/specs}"
R1=src/mongo/db/repl/tla_plus/RaftMongo
R2=src/mongo/db/repl/tla_plus/MongoReplReconfig
R1_AVANT=d422e688b9e4b7a933dcafdd779f8f957dc357ab   # parent of 348880238d
R1_APRES=348880238de3229826053491b1163c88dc3a0575   # SERVER-45853
R2_AVANT=ba6cbcc3b17dfa9ab83722f7505e0bcdc3a4efe2   # parent of dd27888039
R2_APRES=dd278880390a0dda81ef7e9866be4c16b7571b4a   # SERVER-47430
for c in $R1_AVANT $R1_APRES $R2_AVANT $R2_APRES; do
  git -C "$REPO" cat-file -e "$c^{commit}" 2>/dev/null || git -C "$REPO" fetch -q --depth 1 --filter=blob:none origin "$c"
done
get() { mkdir -p "$OUT/$1"; for f in $4; do git -C "$REPO" show "$2:$3/$f" > "$OUT/$1/$f"; done; }

# Result 1 (RaftMongo)
F1="RaftMongo.tla MCRaftMongo.tla MCRaftMongo.cfg"
get r1_avant            $R1_AVANT $R1 "$F1"
get r1_apres            $R1_APRES $R1 "$F1"
get r1_invariants_seuls $R1_AVANT $R1 "MCRaftMongo.tla"
get r1_invariants_seuls $R1_APRES $R1 "RaftMongo.tla"   # child version, as in our run (comments only differ)
# Constructed configuration: the child configuration without its PROPERTY line
# (and the blank line after it), i.e. the parent obligations plus the 2 invariants.
git -C "$REPO" show "$R1_APRES:$R1/MCRaftMongo.cfg" \
  | sed '/^PROPERTY CommitPointEventuallyPropagates$/,+1d' > "$OUT/r1_invariants_seuls/MCRaftMongo.cfg"

# Result 2 (MongoReplReconfig): 3-server reduction (r2_*) and shipped 4 servers (r2_*_4s)
F2="MongoReplReconfig.tla MCMongoReplReconfig.tla MCMongoReplReconfig.cfg"
get r2_avant_4s $R2_AVANT $R2 "$F2"
get r2_apres_4s $R2_APRES $R2 "$F2"
get r2_avant    $R2_AVANT $R2 "$F2"
get r2_apres    $R2_APRES $R2 "$F2"
sed -i 's/{n1, n2, n3, n4}/{n1, n2, n3}/' "$OUT/r2_avant/MCMongoReplReconfig.cfg" "$OUT/r2_apres/MCMongoReplReconfig.cfg"
echo "Specs written to $OUT"
