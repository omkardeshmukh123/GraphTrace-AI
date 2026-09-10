"""
M1 — Artifact Intelligence — Analyzer (Orchestrator)
======================================================
The public entry point for M1.

Pipeline:
  1. ZipHandler  → extract + scan → ArtifactInventory
  2. ReadmeParser → README entities
  3. CodeParser  → Folder / File / Class / Function entities
  4. Merge all ArtifactData into one normalized output

This is what M2 (KnowledgeGraphBuilder) consumes.
"""

from pathlib import Path

from .zip_handler import ZipHandler, ArtifactInventory
from .readme_parser import ReadmeParser
from .code_parser import CodeParser
from .models import ArtifactData, Entity, Relationship, EntityType, RelationshipType


class ArtifactAnalyzer:
    """
    Orchestrates all M1 parsers and returns a single merged ArtifactData.
    """

    def __init__(
        self,
        upload_dir: str = "uploads",
        extracted_dir: str = "extracted",
    ):
        self.zip_handler = ZipHandler(upload_dir, extracted_dir)
        self.readme_parser = ReadmeParser()
        self.code_parser = CodeParser()

    # ─── Public API ───────────────────────────────────────────────────────────

    def analyze_zip(self, file_bytes: bytes, filename: str) -> ArtifactData:
        """
        Full pipeline: accept ZIP bytes, extract, parse, return ArtifactData.
        This is what the API layer calls.
        """
        inventory = self.zip_handler.save_and_extract(file_bytes, filename)
        return self._run_parsers(inventory)

    def analyze_directory(self, directory_path: str | Path) -> ArtifactData:
        """
        Analyze an already-extracted directory (used in tests / CLI).
        """
        inventory = self.zip_handler.extract_from_path(directory_path)
        return self._run_parsers(inventory)

    # ─── Internal pipeline ────────────────────────────────────────────────────

    def _run_parsers(self, inventory: ArtifactInventory) -> ArtifactData:
        """
        Run all parsers on the inventory and merge their outputs.
        """
        all_entities: list[Entity] = []
        all_relationships: list[Relationship] = []
        all_metadata: dict = {
            "project_id": inventory.project_id,
            "project_name": inventory.project_name,
            "root_path": str(inventory.root_path),
            "total_files": inventory.total_files,
            "language_counts": inventory.language_counts(),
            "code_file_count": len(inventory.code_files),
            "doc_file_count": len(inventory.doc_files),
            "config_file_count": len(inventory.config_files),
            "has_readme": inventory.readme_path is not None,
        }

        # ── Step 1: README parser ──────────────────────────────────────────
        if inventory.readme_path is not None:
            readme_data = self.readme_parser.parse(
                readme_path=inventory.readme_path,
                project_id=inventory.project_id,
                project_name=inventory.project_name,
                root_path=inventory.root_path,
            )
            all_entities.extend(readme_data.entities)
            all_relationships.extend(readme_data.relationships)
            all_metadata.update(readme_data.metadata)
        else:
            # No README — still create a bare REPOSITORY entity
            repo_entity = Entity(
                id=f"repository:{inventory.project_id}",
                type=EntityType.REPOSITORY,
                name=inventory.project_name,
                properties={
                    "project_id": inventory.project_id,
                    "root_path": str(inventory.root_path),
                    "has_readme": False,
                },
            )
            all_entities.append(repo_entity)

        # ── Step 2: Code parser ────────────────────────────────────────────
        code_data = self.code_parser.parse(
            code_files=inventory.code_files,
            root_path=inventory.root_path,
            project_id=inventory.project_id,
            project_name=inventory.project_name,
        )
        all_entities.extend(code_data.entities)
        all_relationships.extend(code_data.relationships)
        all_metadata["code_stats"] = code_data.metadata

        # ── Step 3: Deduplicate entities by id ────────────────────────────
        seen_ids: set[str] = set()
        unique_entities: list[Entity] = []
        for entity in all_entities:
            if entity.id not in seen_ids:
                seen_ids.add(entity.id)
                unique_entities.append(entity)

        # Deduplicate relationships by (source, type, target)
        seen_rels: set[tuple[str, str, str]] = set()
        unique_relationships: list[Relationship] = []
        for rel in all_relationships:
            key = (rel.source, rel.type, rel.target)
            if key not in seen_rels:
                seen_rels.add(key)
                unique_relationships.append(rel)

        result = ArtifactData(
            entities=unique_entities,
            relationships=unique_relationships,
            metadata=all_metadata,
        )

        print(f"[M1 Analyzer] {result.summary()}")
        return result
