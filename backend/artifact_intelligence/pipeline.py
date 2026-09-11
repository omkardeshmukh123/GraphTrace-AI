"""
M1 — Artifact Intelligence — Output Pipeline
=============================================
Owner: Member 1 (Artifact Intelligence)

Converts M1's ArtifactData into the shared ArtifactGraph contract defined
in backend/app/models.py, which is then consumed by Member 3's analysis
controller (backend/app/analysis.py).

This is the Common Artifact Output described in GT_Modules.md (Module 1.6):
  "Define common JSON/data format, normalize extracted information,
   send structured artifact information to Member 2."

Steps:
  1. Run M1's ArtifactAnalyzer on the repository_root directory.
  2. Map M1 entity types → M3 node types.
  3. Translate M1 string IDs → stable uuid5 IDs via make_node_id().
  4. Parse optional Markdown SRS into REQUIREMENT nodes.
  5. Deduplicate and return a validated ArtifactGraph.

Called by M3's plugin system via backend/app/config.py:
  GRAPHTRACE_PARSER=backend.artifact_intelligence.pipeline:parse_project
"""

import re
from pathlib import Path

from backend.app.models import ArtifactGraph, Node, Relationship, make_node_id

# M1 internal imports — within the same package
from backend.artifact_intelligence.analyzer import ArtifactAnalyzer
from backend.artifact_intelligence.models import EntityType, RelationshipType as M1RelType


# ─── Type mapping: M1 EntityType → M3 NodeType ────────────────────────────────
_ENTITY_TYPE_MAP: dict[str, str] = {
    EntityType.REPOSITORY: "PROJECT",
    EntityType.FOLDER:     "PACKAGE",
    EntityType.FILE:       "FILE",
    EntityType.CLASS:      "CLASS",
    EntityType.FUNCTION:   "FUNCTION",
    EntityType.README:     "DOCUMENT",
}

# ─── Relationship type mapping: M1 → M3 ────────────────────────────────────────
_REL_TYPE_MAP: dict[str, str] = {
    M1RelType.CONTAINS:   "CONTAINS",
    M1RelType.DEFINES:    "CONTAINS",    # FILE defines CLASS → CONTAINS in M3
    M1RelType.HAS_README: "DOCUMENTED_BY",
}


def parse_project(
    *,
    project_id: str,
    repository_root: Path,
    requirements_text: str | None,
) -> ArtifactGraph:
    """
    Entry point for M3's analysis pipeline (called via plugin system).

    Runs M1 analysis on repository_root, normalizes the output into the shared
    ArtifactGraph format, and parses any SRS requirements from requirements_text.

    Returns:
        ArtifactGraph conforming to backend/app/models.py contract.
    """
    # ── Step 1: Run M1 analysis ──────────────────────────────────────────────
    analyzer = ArtifactAnalyzer()
    m1_data = analyzer.analyze_directory(repository_root)

    # ── Step 2: Build ID translation table ──────────────────────────────────
    # M1 uses string IDs like "file:proj:src/auth.py"
    # M3 requires uuid5-based opaque IDs via make_node_id()
    id_map: dict[str, str] = {}
    m3_nodes: list[Node] = []

    # PROJECT node must come first and have id == project_id
    # Find the M1 REPOSITORY entity
    repo_entity = next(
        (e for e in m1_data.entities if e.type == EntityType.REPOSITORY), None
    )
    project_name = (
        repo_entity.properties.get("title") or repo_entity.name
        if repo_entity else repository_root.name
    )

    # Map the repository entity to project_id directly (required by M3 contract)
    if repo_entity:
        id_map[repo_entity.id] = project_id

    # ── Step 3: Convert all M1 entities → M3 Nodes ──────────────────────────
    for entity in m1_data.entities:
        node_type = _ENTITY_TYPE_MAP.get(entity.type)
        if not node_type:
            continue  # Skip unmapped types

        # Use project_id directly for the repo/project node
        if entity.type == EntityType.REPOSITORY:
            m3_id = project_id
        else:
            # Build a stable reference string for uuid5
            rel_path = entity.properties.get("relative_path", entity.name)
            if entity.type in (EntityType.CLASS, EntityType.FUNCTION):
                parent_class = entity.properties.get("parent_class", "")
                if parent_class:
                    reference = f"{rel_path}::{parent_class}.{entity.name}"
                else:
                    reference = f"{rel_path}::{entity.name}"
            else:
                reference = str(rel_path)
            m3_id = make_node_id(project_id, node_type, reference)

        id_map[entity.id] = m3_id

        # Build M3-compatible properties
        props = {}
        if entity.properties.get("relative_path"):
            props["path"] = entity.properties["relative_path"]
        if entity.properties.get("language"):
            props["language"] = entity.properties["language"]
        if entity.properties.get("description"):
            props["description"] = entity.properties["description"]
        if entity.properties.get("technologies"):
            props["technologies"] = entity.properties["technologies"]
        if entity.properties.get("is_method"):
            props["is_method"] = entity.properties["is_method"]
        if entity.properties.get("parent_class"):
            props["parent_class"] = entity.properties["parent_class"]
        # reference field used by manual mappings (e.g. auth.py::AuthService.login)
        if entity.type in (EntityType.CLASS, EntityType.FUNCTION):
            rel_path = entity.properties.get("relative_path", "")
            parent_class = entity.properties.get("parent_class", "")
            if parent_class:
                props["reference"] = f"{rel_path}::{parent_class}.{entity.name}"
            else:
                props["reference"] = f"{rel_path}::{entity.name}"
        elif entity.type == EntityType.FILE:
            props["reference"] = entity.properties.get("relative_path", entity.name)
        if entity.type == EntityType.REPOSITORY:
            props["source"] = "repository"

        m3_nodes.append(Node(
            id=m3_id,
            type=node_type,
            name=entity.name,
            properties=props,
        ))

    # PROJECT node: must be present with id == project_id
    if not any(n.id == project_id for n in m3_nodes):
        m3_nodes.insert(0, Node(
            id=project_id,
            type="PROJECT",
            name=project_name,
            properties={"source": "repository"},
        ))
    else:
        # Ensure source property is set on the PROJECT node (immutable Pydantic-safe)
        for idx, node in enumerate(m3_nodes):
            if node.id == project_id:
                if node.properties.get("source") != "repository":
                    m3_nodes[idx] = node.model_copy(update={"properties": {**node.properties, "source": "repository"}})
                break

    # ── Step 4: Convert M1 relationships → M3 Relationships ──────────────────
    m3_relationships: list[Relationship] = []
    seen_rels: set[tuple[str, str, str]] = set()

    for rel in m1_data.relationships:
        m3_source = id_map.get(rel.source)
        m3_target = id_map.get(rel.target)
        m3_type = _REL_TYPE_MAP.get(rel.type)

        if not m3_source or not m3_target or not m3_type:
            continue

        # Skip self-loops
        if m3_source == m3_target:
            continue

        key = (m3_source, m3_type, m3_target)
        if key in seen_rels:
            continue
        seen_rels.add(key)

        m3_relationships.append(Relationship(
            source=m3_source,
            target=m3_target,
            type=m3_type,
        ))

    # ── Step 5: Parse requirements from Markdown SRS ──────────────────────────
    if requirements_text:
        req_nodes, req_rels = _parse_requirements(
            requirements_text, project_id, m3_nodes, id_map
        )
        m3_nodes.extend(req_nodes)
        m3_relationships.extend(req_rels)

    # ── Step 6: Deduplicate node IDs ─────────────────────────────────────────
    seen_ids: set[str] = set()
    unique_nodes: list[Node] = []
    for node in m3_nodes:
        if node.id not in seen_ids:
            seen_ids.add(node.id)
            unique_nodes.append(node)

    # Ensure PROJECT node is first
    unique_nodes.sort(key=lambda n: (0 if n.id == project_id else 1, n.type, n.name))

    return ArtifactGraph(
        project_id=project_id,
        nodes=unique_nodes,
        relationships=m3_relationships,
    )


# ─── Requirements Markdown Parser ────────────────────────────────────────────

def _parse_requirements(
    text: str,
    project_id: str,
    existing_nodes: list[Node],
    id_map: dict[str, str],
) -> tuple[list[Node], list[Relationship]]:
    """
    Extract REQUIREMENT nodes from a Markdown SRS document.

    Detects patterns like:
      ## REQ-001: User Login
      - **REQ-001**: ...
      REQ-001 ...
    """
    req_pattern = re.compile(
        # Matches:
        #   ## REQ-001: Title
        #   **REQ-003**: Title
        #   REQ-004 Title
        r"(?:^|\n)(?:#{1,4}\s+|\*{0,2})(REQ-\d+)\*{0,2}[:\s–\-]+([^\n]{3,200})",
        re.MULTILINE,
    )

    nodes: list[Node] = []
    rels: list[Relationship] = []
    seen_refs: set[str] = set()

    for match in req_pattern.finditer(text):
        ref = match.group(1).strip()       # e.g. "REQ-001"
        name = match.group(2).strip()[:200]  # requirement title

        if ref in seen_refs:
            continue
        seen_refs.add(ref)

        req_id = make_node_id(project_id, "REQUIREMENT", ref)
        nodes.append(Node(
            id=req_id,
            type="REQUIREMENT",
            name=name,
            properties={"reference": ref, "source": "srs"},
        ))

        # Connect REQUIREMENT to PROJECT via PART_OF
        rels.append(Relationship(
            source=req_id,
            target=project_id,
            type="PART_OF",
        ))

    return nodes, rels
