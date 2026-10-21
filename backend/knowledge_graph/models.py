"""
M2 — Knowledge Graph Engine — Node & Relationship Type Constants
=================================================================
Single source of truth for all Neo4j label and relationship type strings.

Rule: NEVER use raw string literals like "CLASS" or "CONTAINS" anywhere
in M2 code. Always use these constants so renaming is a one-line change.
"""


class NodeLabel:
    """Neo4j node label strings (Phase 1 + Phase 4)."""
    # Phase 1 — Basic Software Understanding
    REPOSITORY  = "Repository"
    FOLDER      = "Folder"
    FILE        = "File"
    CLASS       = "Class"
    FUNCTION    = "Function"
    README      = "Readme"

    # Phase 4 — Architecture Intelligence
    SYSTEM      = "System"
    COMPONENT   = "Component"
    SERVICE     = "Service"
    TECHNOLOGY  = "Technology"
    REQUIREMENT = "Requirement"
    DOCUMENT    = "Document"

    # Mapping from M1/M3 EntityType strings → Neo4j labels
    FROM_ENTITY_TYPE: dict[str, str] = {}   # filled below


# Build the reverse map from M1 EntityType → Neo4j label
NodeLabel.FROM_ENTITY_TYPE = {
    # Phase 1
    "REPOSITORY":  NodeLabel.REPOSITORY,
    "FOLDER":      NodeLabel.FOLDER,
    "FILE":        NodeLabel.FILE,
    "CLASS":       NodeLabel.CLASS,
    "FUNCTION":    NodeLabel.FUNCTION,
    "README":      NodeLabel.README,
    "PROJECT":     "Project",
    "PACKAGE":     "Package",
    "MODULE":      "Module",
    "METHOD":      "Method",
    # Phase 4 — Architecture Intelligence
    "SYSTEM":      NodeLabel.SYSTEM,
    "COMPONENT":   NodeLabel.COMPONENT,
    "SERVICE":     NodeLabel.SERVICE,
    "TECHNOLOGY":  NodeLabel.TECHNOLOGY,
    "REQUIREMENT": NodeLabel.REQUIREMENT,
    "DOCUMENT":    NodeLabel.DOCUMENT,
}


class RelType:
    """Neo4j relationship type strings (Phase 1 + Phase 4)."""
    # Phase 1
    CONTAINS    = "CONTAINS"
    HAS_README  = "HAS_README"
    DEFINES     = "DEFINES"
    IMPORTS     = "IMPORTS"
    CALLS       = "CALLS"
    EXTENDS     = "EXTENDS"
    IMPLEMENTS  = "IMPLEMENTS"
    DEPENDS_ON  = "DEPENDS_ON"
    DOCUMENTED_BY = "DOCUMENTED_BY"

    # Phase 3 — Requirement Intelligence
    PART_OF         = "PART_OF"
    IMPLEMENTED_BY  = "IMPLEMENTED_BY"
    USES            = "USES"

    # Phase 4 — Architecture Intelligence
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    EXPOSES           = "EXPOSES"
    TESTED_BY         = "TESTED_BY"

    # Mapping from M1/M3 RelationshipType strings → Neo4j rel types
    FROM_REL_TYPE: dict[str, str] = {}   # filled below


RelType.FROM_REL_TYPE = {
    # Phase 1
    "CONTAINS":          RelType.CONTAINS,
    "HAS_README":        RelType.HAS_README,
    "DEFINES":           RelType.DEFINES,
    "IMPORTS":           RelType.IMPORTS,
    "CALLS":             RelType.CALLS,
    "EXTENDS":           RelType.EXTENDS,
    "IMPLEMENTS":        RelType.IMPLEMENTS,
    "DEPENDS_ON":        RelType.DEPENDS_ON,
    "DOCUMENTED_BY":     RelType.DOCUMENTED_BY,
    # Phase 3
    "PART_OF":           RelType.PART_OF,
    "IMPLEMENTED_BY":    RelType.IMPLEMENTED_BY,
    "USES":              RelType.USES,
    # Phase 4
    "COMMUNICATES_WITH": RelType.COMMUNICATES_WITH,
    "EXPOSES":           RelType.EXPOSES,
    "TESTED_BY":         RelType.TESTED_BY,
}

# ─── Architectural node types set (for queries / filtering) ──────────────────
ARCH_NODE_TYPES = {
    NodeLabel.SYSTEM,
    NodeLabel.COMPONENT,
    NodeLabel.SERVICE,
    NodeLabel.TECHNOLOGY,
}
