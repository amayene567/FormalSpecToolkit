---- MODULE MCRefinesParent ----
\* Checks that the child spec (commit dd27888039) refines the safety part of the
\* parent spec (commit ba6cbcc3b1): every initial state is a parent initial state,
\* and every step is a parent step or a stuttering step.
EXTENDS MCMongoReplReconfig

Parent == INSTANCE MongoReplReconfigParent

ParentInit   == Parent!Init
ParentSteps  == [][Parent!Next]_vars
====
