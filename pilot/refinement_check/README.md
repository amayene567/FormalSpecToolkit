# Refinement check: SERVER-47430 child refines parent

Checks that MongoReplReconfig at commit dd27888039 (child) refines the safety part of
the spec at its parent ba6cbcc3b1: `Parent!Init` and `[][Parent!Next]_vars`.

1. `./make_modules.sh /path/to/mongo-clone` regenerates the three MongoDB modules.
2. `java -XX:+UseParallelGC -jar tla2tools.jar -workers 2 MCRefinesParent.tla`

Result (TLC 2.19, tla2tools v1.7.4): no error; 41,496,087 states generated,
2,413,165 distinct (`refines_parent.log`, 39 min on 2 cores).

Control: the converse check (parent refines child) fails after 3 states
(`control_parent_refines_child.log`). To reproduce it, swap the roles: use the
parent commit's modules and instantiate the child module.
