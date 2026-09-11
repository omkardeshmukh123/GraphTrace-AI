"""
M1 — Artifact Intelligence — README Parser
============================================
Parses the project's README.md to extract:
  - Project name & description
  - Technology mentions (Python, FastAPI, React, etc.)
  - Section headings

Outputs:
  - One README Entity
  - One REPOSITORY Entity
  - HAS_README relationship: Repository → README

Phase 1: regex + markdown heading extraction.
Phase 6: full Documentation Intelligence (linked to code entities).
"""

import re
from pathlib import Path

from .models import (
    Entity, Relationship, ArtifactData,
    EntityType, RelationshipType,
)


# ─── Known technology keywords to detect ──────────────────────────────────────
TECH_KEYWORDS = [
    "Python", "FastAPI", "Flask", "Django",
    "JavaScript", "TypeScript", "React", "Next.js", "Vue", "Angular",
    "Node.js", "Express",
    "Java", "Spring", "Maven", "Gradle",
    "Go", "Rust",
    "Neo4j", "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Redis",
    "Docker", "Kubernetes",
    "GraphQL", "REST", "gRPC",
    "LangChain", "LlamaIndex", "OpenAI", "Llama",
    "Tree-sitter", "FAISS", "Chroma",
]


class ReadmeParser:
    """Parses README.md and produces README + REPOSITORY entities."""

    def parse(
        self,
        readme_path: Path,
        project_id: str,
        project_name: str,
        root_path: Path,
    ) -> ArtifactData:
        """
        Read the README file and produce an ArtifactData with:
          - 1 REPOSITORY entity
          - 1 README entity
          - 1 HAS_README relationship
        """
        content = readme_path.read_text(encoding="utf-8", errors="ignore")

        # ── Extract pieces ──────────────────────────────────────────────────
        title = self._extract_title(content, project_name)
        description = self._extract_description(content)
        sections = self._extract_sections(content)
        technologies = self._extract_technologies(content)

        # ── Build IDs ───────────────────────────────────────────────────────
        repo_id = f"repository:{project_id}"
        readme_id = f"readme:{project_id}"

        # ── Entities ────────────────────────────────────────────────────────
        repo_entity = Entity(
            id=repo_id,
            type=EntityType.REPOSITORY,
            name=project_name,
            properties={
                "project_id": project_id,
                "root_path": str(root_path),
                "title": title,
                "description": description,
                "technologies": technologies,
            },
        )

        readme_entity = Entity(
            id=readme_id,
            type=EntityType.README,
            name="README.md",
            properties={
                "path": str(readme_path),
                "relative_path": str(readme_path.relative_to(root_path)),
                "title": title,
                "description": description,
                "sections": sections,
                "technologies": technologies,
                "char_count": len(content),
            },
        )

        # ── Relationship ─────────────────────────────────────────────────────
        has_readme_rel = Relationship(
            source=repo_id,
            type=RelationshipType.HAS_README,
            target=readme_id,
        )

        return ArtifactData(
            entities=[repo_entity, readme_entity],
            relationships=[has_readme_rel],
            metadata={
                "readme_title": title,
                "readme_description": description,
                "readme_sections": sections,
                "readme_technologies": technologies,
            },
        )

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _extract_title(self, content: str, fallback: str) -> str:
        """Extract the first H1 heading as the project title."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else fallback

    def _extract_description(self, content: str) -> str:
        """
        Extract first non-heading paragraph after the title as description.
        Caps at 500 characters.
        """
        lines = content.splitlines()
        capture = False
        desc_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip the first H1
            if stripped.startswith("# ") and not capture:
                capture = True
                continue

            if not capture:
                continue

            # Stop at next heading
            if stripped.startswith("#"):
                break

            if stripped:
                desc_lines.append(stripped)
                combined = " ".join(desc_lines)
                if len(combined) >= 500:
                    return combined[:500]

        return " ".join(desc_lines)[:500]

    def _extract_sections(self, content: str) -> list[str]:
        """Extract all H2/H3 headings as section names."""
        matches = re.findall(r"^#{2,3}\s+(.+)$", content, re.MULTILINE)
        return [m.strip() for m in matches]

    def _extract_technologies(self, content: str) -> list[str]:
        """Detect known technology keywords in the README text."""
        found: list[str] = []
        content_lower = content.lower()
        for tech in TECH_KEYWORDS:
            if tech.lower() in content_lower:
                found.append(tech)
        return found
