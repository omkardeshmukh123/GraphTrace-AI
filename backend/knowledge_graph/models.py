"""
M2 — Knowledge Graph Engine — Node & Relationship Type Constants
=================================================================
Single source of truth for all Neo4j label and relationship type strings.

Rule: NEVER use raw string literals like "CLASS" or "CONTAINS" anywhere
in M2 code. Always use these constants so renaming is a one-line change.
"""


class NodeLabel:
    """Neo4j node label strings (Phase 1)."""
    REPOSITORY  = "Repository"
    FOLDER      = "Folder"
    FILE        = "File"
    CLASS       = "Class"
    FUNCTION    = "Function"
    README      = "Readme"

    # Mapping from M1 EntityType strings → Neo4j labels
    FROM_ENTITY_TYPE: dict[str, str] = {}   # filled below


# Build the reverse map from M1 EntityType → Neo4j label
NodeLabel.FROM_ENTITY_TYPE = {
    "REPOSITORY": NodeLabel.REPOSITORY,
    "FOLDER":     NodeLabel.FOLDER,
    "FILE":       NodeLabel.FILE,
    "CLASS":      NodeLabel.CLASS,
    "FUNCTION":   NodeLabel.FUNCTION,
    "README":     NodeLabel.README,
}


class RelType:
    """Neo4j relationship type strings (Phase 1)."""
    CONTAINS    = "CONTAINS"
    HAS_README  = "HAS_README"
    DEFINES     = "DEFINES"

    # Mapping from M1 RelationshipType strings → Neo4j rel types
    FROM_REL_TYPE: dict[str, str] = {}   # filled below


RelType.FROM_REL_TYPE = {
    "CONTAINS":   RelType.CONTAINS,
    "HAS_README": RelType.HAS_README,
    "DEFINES":    RelType.DEFINES,
}
