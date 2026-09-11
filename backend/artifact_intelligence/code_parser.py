"""
M1 — Artifact Intelligence — Code Parser
==========================================
Walks the project's source tree and extracts:
  - FOLDER entities  (each unique directory)
  - FILE entities    (each source file)
  - CLASS entities   (regex-detected class definitions)
  - FUNCTION entities (regex-detected function / method definitions)

Relationships produced:
  - REPOSITORY → CONTAINS → FOLDER (top-level folders)
  - FOLDER → CONTAINS → FOLDER (nested)
  - FOLDER → CONTAINS → FILE
  - FILE → DEFINES → CLASS
  - FILE → DEFINES → FUNCTION  (top-level functions)
  - CLASS → CONTAINS → FUNCTION (methods inside a class)

Phase 1: regex-based (no Tree-sitter).
Phase 2: replace with Tree-sitter AST for precision.

Supported languages in Phase 1:
  - Python (.py)
  - JavaScript (.js)
  - TypeScript (.ts)
"""

import re
from pathlib import Path
from dataclasses import dataclass, field

from .models import (
    Entity, Relationship, ArtifactData,
    EntityType, RelationshipType,
)


# ─── Per-language regex patterns ──────────────────────────────────────────────
@dataclass
class LangPatterns:
    class_pattern: re.Pattern
    function_pattern: re.Pattern
    method_pattern: re.Pattern   # indented function inside a class


PYTHON_PATTERNS = LangPatterns(
    class_pattern=re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)[\s:(]", re.MULTILINE),
    function_pattern=re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE),
    method_pattern=re.compile(r"^    def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE),
)

JS_PATTERNS = LangPatterns(
    class_pattern=re.compile(
        r"(?:^|\n)(?:export\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE
    ),
    function_pattern=re.compile(
        r"(?:^|\n)(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        re.MULTILINE,
    ),
    method_pattern=re.compile(
        r"^\s{2,}(?:async\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{", re.MULTILINE
    ),
)

LANG_MAP: dict[str, tuple[str, LangPatterns]] = {
    ".py": ("Python", PYTHON_PATTERNS),
    ".js": ("JavaScript", JS_PATTERNS),
    ".ts": ("TypeScript", JS_PATTERNS),   # TS uses same surface patterns
}


@dataclass
class ParsedFile:
    """Intermediate result of parsing a single source file."""
    path: Path
    language: str
    classes: list[str] = field(default_factory=list)
    top_functions: list[str] = field(default_factory=list)
    methods_by_class: dict[str, list[str]] = field(default_factory=dict)


class CodeParser:
    """
    Regex-based code parser for Phase 1.
    Walks source files and extracts structural entities.
    """

    def parse(
        self,
        code_files: list[Path],
        root_path: Path,
        project_id: str,
        project_name: str,
    ) -> ArtifactData:
        """
        Parse all code files and produce entities + relationships.
        """
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        repo_id = f"repository:{project_id}"
        folder_ids: dict[Path, str] = {}   # path → entity id cache

        # ── 1. Collect all unique folders ─────────────────────────────────
        all_folders: set[Path] = set()
        for fp in code_files:
            # Every ancestor up to (but not including) root_path
            for parent in fp.parents:
                if parent == root_path or not str(parent).startswith(str(root_path)):
                    break
                all_folders.add(parent)

        # ── 2. Create FOLDER entities & CONTAINS relationships ─────────────
        for folder in sorted(all_folders, key=lambda p: len(p.parts)):
            rel_path = folder.relative_to(root_path)
            folder_id = f"folder:{project_id}:{rel_path}"
            folder_ids[folder] = folder_id

            entities.append(Entity(
                id=folder_id,
                type=EntityType.FOLDER,
                name=folder.name,
                properties={
                    "path": str(folder),
                    "relative_path": str(rel_path),
                    "project_id": project_id,
                },
            ))

            # Parent: either another folder or the repository root
            parent = folder.parent
            if parent == root_path:
                parent_id = repo_id
            else:
                parent_id = folder_ids.get(parent, repo_id)

            relationships.append(Relationship(
                source=parent_id,
                type=RelationshipType.CONTAINS,
                target=folder_id,
            ))

        # ── 3. Parse each file ─────────────────────────────────────────────
        for fp in code_files:
            ext = fp.suffix.lower()
            if ext not in LANG_MAP:
                continue  # Not a Phase 1 language

            language, patterns = LANG_MAP[ext]
            parsed = self._parse_file(fp, language, patterns)

            # ── FILE entity ────────────────────────────────────────────────
            rel_path = fp.relative_to(root_path)
            file_id = f"file:{project_id}:{rel_path}"

            entities.append(Entity(
                id=file_id,
                type=EntityType.FILE,
                name=fp.name,
                properties={
                    "path": str(fp),
                    "relative_path": str(rel_path),
                    "language": language,
                    "extension": ext,
                    "project_id": project_id,
                    "class_count": len(parsed.classes),
                    "function_count": len(parsed.top_functions),
                },
            ))

            # FILE → parent FOLDER or REPOSITORY
            folder_id = folder_ids.get(fp.parent, repo_id)
            relationships.append(Relationship(
                source=folder_id,
                type=RelationshipType.CONTAINS,
                target=file_id,
            ))

            # ── CLASS entities ─────────────────────────────────────────────
            for class_name in parsed.classes:
                class_id = f"class:{project_id}:{rel_path}:{class_name}"
                entities.append(Entity(
                    id=class_id,
                    type=EntityType.CLASS,
                    name=class_name,
                    properties={
                        "language": language,
                        "file_path": str(rel_path),
                        "project_id": project_id,
                    },
                ))
                relationships.append(Relationship(
                    source=file_id,
                    type=RelationshipType.DEFINES,
                    target=class_id,
                ))

                # ── METHOD entities inside this class ──────────────────────
                for method_name in parsed.methods_by_class.get(class_name, []):
                    method_id = f"function:{project_id}:{rel_path}:{class_name}.{method_name}"
                    entities.append(Entity(
                        id=method_id,
                        type=EntityType.FUNCTION,
                        name=method_name,
                        properties={
                            "language": language,
                            "file_path": str(rel_path),
                            "parent_class": class_name,
                            "is_method": True,
                            "project_id": project_id,
                        },
                    ))
                    relationships.append(Relationship(
                        source=class_id,
                        type=RelationshipType.CONTAINS,
                        target=method_id,
                    ))

            # ── Top-level FUNCTION entities ────────────────────────────────
            for func_name in parsed.top_functions:
                func_id = f"function:{project_id}:{rel_path}:{func_name}"
                entities.append(Entity(
                    id=func_id,
                    type=EntityType.FUNCTION,
                    name=func_name,
                    properties={
                        "language": language,
                        "file_path": str(rel_path),
                        "is_method": False,
                        "project_id": project_id,
                    },
                ))
                relationships.append(Relationship(
                    source=file_id,
                    type=RelationshipType.DEFINES,
                    target=func_id,
                ))

        # ── 4. Build summary metadata ──────────────────────────────────────
        metadata = {
            "parser": "regex-phase1",
            "folder_count": len(all_folders),
            "file_count": len(code_files),
            "supported_files": sum(
                1 for f in code_files if f.suffix.lower() in LANG_MAP
            ),
        }

        return ArtifactData(
            entities=entities,
            relationships=relationships,
            metadata=metadata,
        )

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _parse_file(self, path: Path, language: str, patterns: LangPatterns) -> ParsedFile:
        """Parse a single source file using regex patterns."""
        result = ParsedFile(path=path, language=language)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return result

        # ── Extract classes ────────────────────────────────────────────────
        classes = [m.group(1) for m in patterns.class_pattern.finditer(content)]
        result.classes = classes

        # ── Extract top-level functions (not indented / not methods) ───────
        all_functions = [m.group(1) for m in patterns.function_pattern.finditer(content)]
        all_methods = [m.group(1) for m in patterns.method_pattern.finditer(content)]
        method_set = set(all_methods)
        result.top_functions = [f for f in all_functions if f not in method_set]

        # ── Attribute methods to classes (simple heuristic) ────────────────
        # For Phase 1: assign all detected methods to the LAST class defined
        # before that method appears in the file. Good enough for typical files.
        if classes and all_methods:
            result.methods_by_class = self._assign_methods_to_classes(
                content, classes, patterns
            )
        return result

    def _assign_methods_to_classes(
        self,
        content: str,
        classes: list[str],
        patterns: LangPatterns,
    ) -> dict[str, list[str]]:
        """
        Heuristic: find position of each class definition and each method,
        then assign each method to the class that precedes it most closely.
        """
        # Map class name → character position of its definition
        class_positions: list[tuple[int, str]] = []
        for m in patterns.class_pattern.finditer(content):
            class_positions.append((m.start(), m.group(1)))
        class_positions.sort()

        methods_by_class: dict[str, list[str]] = {c: [] for c in classes}

        for m in patterns.method_pattern.finditer(content):
            method_name = m.group(1)
            method_pos = m.start()

            # Find the class with the largest start position still before method_pos
            current_class: str | None = None
            for pos, cls_name in class_positions:
                if pos < method_pos:
                    current_class = cls_name
                else:
                    break

            if current_class and current_class in methods_by_class:
                methods_by_class[current_class].append(method_name)

        return methods_by_class
