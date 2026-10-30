#!/usr/bin/env bash
# Regenerates the MongoDB modules needed by MCRefinesParent.tla (not redistributed).
# Usage: ./make_modules.sh /path/to/mongo-clone   (needs both commits fetched)
set -euo pipefail
REPO="$1"
D=src/mongo/db/repl/tla_plus/MongoReplReconfig
PARENT=ba6cbcc3b17dfa9ab83722f7505e0bcdc3a4efe2
CHILD=dd278880390a0dda81ef7e9866be4c16b7571b4a
git -C "$REPO" show $CHILD:$D/MongoReplReconfig.tla   > MongoReplReconfig.tla
git -C "$REPO" show $CHILD:$D/MCMongoReplReconfig.tla > MCMongoReplReconfig.tla
git -C "$REPO" show $PARENT:$D/MongoReplReconfig.tla \
  | sed 's/MODULE MongoReplReconfig /MODULE MongoReplReconfigParent /' > MongoReplReconfigParent.tla
echo "Done. Run: java -XX:+UseParallelGC -jar tla2tools.jar -workers 2 MCRefinesParent.tla"
