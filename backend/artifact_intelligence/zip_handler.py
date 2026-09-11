"""
M1 — Artifact Intelligence — ZIP Handler
==========================================
Handles uploaded ZIP files:
  1. Save the uploaded file to disk
  2. Extract to a unique project folder
  3. Scan for artifact types (code, docs, config)
  4. Return the extracted root path + artifact inventory

Phase 1 scope: ZIP files only.
Future phases can add: Git URL cloning, directory upload.
"""

import os
import uuid
import zipfile
import shutil
from pathlib import Path
from dataclasses import dataclass, field


# ─── Supported file extension sets ────────────────────────────────────────────
CODE_EXTENSIONS = {
    ".py",   # Python
    ".js",   # JavaScript
    ".ts",   # TypeScript
    ".java", # Java (detected, not deeply parsed in Phase 1)
    ".go",   # Go  (detected, not deeply parsed in Phase 1)
}

DOC_EXTENSIONS = {".md", ".rst", ".txt"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}

# Folders to always skip
SKIP_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".pytest_cache",
    "venv", ".venv", "env",
    "dist", "build", ".eggs",
    ".idea", ".vscode",
}


@dataclass
class ArtifactInventory:
    """Summary of what was found in the extracted project."""
    project_id: str
    project_name: str
    root_path: Path
    code_files: list[Path] = field(default_factory=list)
    doc_files: list[Path] = field(default_factory=list)
    config_files: list[Path] = field(default_factory=list)
    readme_path: Path | None = None

    @property
    def total_files(self) -> int:
        return len(self.code_files) + len(self.doc_files) + len(self.config_files)

    def language_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self.code_files:
            ext = f.suffix.lower()
            lang = {
                ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                ".java": "Java", ".go": "Go",
            }.get(ext, ext)
            counts[lang] = counts.get(lang, 0) + 1
        return counts


class ZipHandler:
    """Handles ZIP file upload, extraction, and artifact scanning."""

    def __init__(self, upload_dir: str = "uploads", extracted_dir: str = "extracted"):
        self.upload_dir = Path(upload_dir)
        self.extracted_dir = Path(extracted_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)

    def save_and_extract(self, file_bytes: bytes, filename: str) -> ArtifactInventory:
        """
        Save uploaded bytes to disk, extract ZIP, scan for artifacts.
        Returns ArtifactInventory with the root path and file lists.
        """
        project_id = str(uuid.uuid4())

        # 1. Save ZIP
        zip_path = self.upload_dir / f"{project_id}.zip"
        zip_path.write_bytes(file_bytes)

        # 2. Extract
        extract_root = self.extracted_dir / project_id
        extract_root.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_root)

        # 3. Find the actual project root (handle single top-level folder in ZIP)
        project_root = self._resolve_project_root(extract_root)

        # 4. Determine project name
        project_name = self._infer_project_name(project_root, filename)

        # 5. Scan
        inventory = self._scan(project_id, project_name, project_root)
        return inventory

    def extract_from_path(self, path: str | Path) -> ArtifactInventory:
        """
        Directly scan an already-extracted directory (used in tests).
        """
        root = Path(path).resolve()
        project_id = str(uuid.uuid4())
        project_name = root.name
        return self._scan(project_id, project_name, root)

    def cleanup(self, project_id: str) -> None:
        """Remove extracted folder and uploaded ZIP after processing."""
        zip_path = self.upload_dir / f"{project_id}.zip"
        extract_path = self.extracted_dir / project_id
        if zip_path.exists():
            zip_path.unlink()
        if extract_path.exists():
            shutil.rmtree(extract_path)

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _resolve_project_root(self, extract_root: Path) -> Path:
        """
        If the ZIP contained a single top-level folder, treat that as the
        project root. Otherwise, use extract_root directly.
        """
        children = [c for c in extract_root.iterdir() if not c.name.startswith(".")]
        if len(children) == 1 and children[0].is_dir():
            return children[0]
        return extract_root

    def _infer_project_name(self, root: Path, original_filename: str) -> str:
        """
        Try README first, then folder name, then strip .zip extension.
        """
        readme = root / "README.md"
        if readme.exists():
            first_line = readme.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
            if first_line:
                title = first_line[0].lstrip("#").strip()
                if title:
                    return title
        if root.name and root.name not in {".", "extracted"}:
            return root.name
        return Path(original_filename).stem

    def _scan(self, project_id: str, project_name: str, root: Path) -> ArtifactInventory:
        """Walk the directory tree and classify every file."""
        inventory = ArtifactInventory(
            project_id=project_id,
            project_name=project_name,
            root_path=root,
        )

        for dirpath, dirnames, filenames in os.walk(root):
            # Skip unwanted directories (mutate in-place to prevent os.walk recursion)
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS and not d.startswith(".")
            ]

            for fname in filenames:
                fpath = Path(dirpath) / fname
                ext = fpath.suffix.lower()

                if ext in CODE_EXTENSIONS:
                    inventory.code_files.append(fpath)
                elif ext in DOC_EXTENSIONS:
                    inventory.doc_files.append(fpath)
                    # Track README specifically
                    if fpath.name.upper() in {"README.MD", "README.RST", "README.TXT"}:
                        if inventory.readme_path is None:
                            inventory.readme_path = fpath
                elif ext in CONFIG_EXTENSIONS:
                    inventory.config_files.append(fpath)

        return inventory
