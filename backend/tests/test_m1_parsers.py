"""
Tests — M1 Artifact Intelligence
==================================
Tests for:
  - ZipHandler: directory scanning, artifact classification
  - ReadmeParser: title, description, section, tech extraction
  - CodeParser: entity & relationship extraction from Python/JS files
  - ArtifactAnalyzer: end-to-end pipeline on sample_project/

Run with:
    cd backend
    pytest tests/test_m1_parsers.py -v
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from artifact_intelligence.zip_handler import ZipHandler
from artifact_intelligence.readme_parser import ReadmeParser
from artifact_intelligence.code_parser import CodeParser
from artifact_intelligence.analyzer import ArtifactAnalyzer
from artifact_intelligence.models import EntityType, RelationshipType

# Path to sample project (relative to this test file)
SAMPLE_PROJECT = Path(__file__).parent.parent.parent / "sample_project"


# ─── ZipHandler Tests ─────────────────────────────────────────────────────────

class TestZipHandler:

    def setup_method(self):
        self.handler = ZipHandler(upload_dir="uploads", extracted_dir="extracted")

    def test_scan_finds_python_files(self):
        inventory = self.handler.extract_from_path(SAMPLE_PROJECT)
        py_files = [f for f in inventory.code_files if f.suffix == ".py"]
        assert len(py_files) >= 3, "Should find at least 3 Python files in sample_project"

    def test_scan_finds_js_files(self):
        inventory = self.handler.extract_from_path(SAMPLE_PROJECT)
        js_files = [f for f in inventory.code_files if f.suffix == ".js"]
        assert len(js_files) >= 1, "Should find at least 1 JavaScript file"

    def test_scan_finds_readme(self):
        inventory = self.handler.extract_from_path(SAMPLE_PROJECT)
        assert inventory.readme_path is not None, "README.md should be detected"
        assert inventory.readme_path.name == "README.md"

    def test_language_counts(self):
        inventory = self.handler.extract_from_path(SAMPLE_PROJECT)
        counts = inventory.language_counts()
        assert "Python" in counts
        assert "JavaScript" in counts

    def test_skips_pycache(self, tmp_path):
        """Ensure __pycache__ directories are skipped."""
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.pyc").write_bytes(b"junk")
        (tmp_path / "real_file.py").write_text("class A: pass")

        inventory = self.handler.extract_from_path(tmp_path)
        assert not any("__pycache__" in str(f) for f in inventory.code_files)
        assert len(inventory.code_files) == 1


# ─── ReadmeParser Tests ───────────────────────────────────────────────────────

class TestReadmeParser:

    def setup_method(self):
        self.parser = ReadmeParser()
        self.readme_path = SAMPLE_PROJECT / "README.md"

    def test_extracts_title(self):
        data = self.parser.parse(self.readme_path, "proj-001", "fallback", SAMPLE_PROJECT)
        repo = next(e for e in data.entities if e.type == EntityType.REPOSITORY)
        assert repo.properties["title"] != ""

    def test_extracts_description(self):
        data = self.parser.parse(self.readme_path, "proj-001", "fallback", SAMPLE_PROJECT)
        readme = next(e for e in data.entities if e.type == EntityType.README)
        assert len(readme.properties.get("description", "")) > 10

    def test_detects_technologies(self):
        data = self.parser.parse(self.readme_path, "proj-001", "fallback", SAMPLE_PROJECT)
        readme = next(e for e in data.entities if e.type == EntityType.README)
        techs = readme.properties.get("technologies", [])
        assert "Python" in techs
        assert "FastAPI" in techs

    def test_extracts_sections(self):
        data = self.parser.parse(self.readme_path, "proj-001", "fallback", SAMPLE_PROJECT)
        readme = next(e for e in data.entities if e.type == EntityType.README)
        sections = readme.properties.get("sections", [])
        assert len(sections) > 0

    def test_creates_has_readme_relationship(self):
        data = self.parser.parse(self.readme_path, "proj-001", "fallback", SAMPLE_PROJECT)
        rel = next((r for r in data.relationships if r.type == RelationshipType.HAS_README), None)
        assert rel is not None

    def test_handles_missing_readme(self, tmp_path):
        """Parser should be skipped (analyzer handles this), not crash."""
        # ReadmeParser expects a valid path — this tests the no-readme branch in analyzer
        pass  # Covered by TestArtifactAnalyzer.test_no_readme_project


# ─── CodeParser Tests ─────────────────────────────────────────────────────────

class TestCodeParser:

    def setup_method(self):
        self.parser = CodeParser()

    def test_detects_python_classes(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        class_entities = [e for e in data.entities if e.type == EntityType.CLASS]
        class_names = [e.name for e in class_entities]

        assert "AuthService" in class_names
        assert "JWTService" in class_names
        assert "OrderService" in class_names
        assert "UserRepository" in class_names

    def test_detects_js_classes(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        class_names = [e.name for e in data.entities if e.type == EntityType.CLASS]
        assert "PaymentService" in class_names
        assert "CartManager" in class_names

    def test_detects_python_methods(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        func_entities = [e for e in data.entities if e.type == EntityType.FUNCTION]
        method_names = [e.name for e in func_entities]
        assert "login" in method_names
        assert "logout" in method_names

    def test_detects_top_level_functions(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        top_funcs = [
            e for e in data.entities
            if e.type == EntityType.FUNCTION and not e.properties.get("is_method", True)
        ]
        names = [e.name for e in top_funcs]
        assert "hash_password" in names
        assert "validate_email" in names

    def test_creates_folder_entities(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        folders = [e for e in data.entities if e.type == EntityType.FOLDER]
        folder_names = [e.name for e in folders]
        assert "src" in folder_names
        assert "frontend" in folder_names

    def test_creates_contains_relationships(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        contains_rels = [r for r in data.relationships if r.type == RelationshipType.CONTAINS]
        assert len(contains_rels) > 0

    def test_creates_defines_relationships(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        defines_rels = [r for r in data.relationships if r.type == RelationshipType.DEFINES]
        assert len(defines_rels) > 0

    def test_no_duplicate_entity_ids(self):
        handler = ZipHandler()
        inventory = handler.extract_from_path(SAMPLE_PROJECT)
        data = self.parser.parse(
            inventory.code_files, SAMPLE_PROJECT, "proj-001", "Sample"
        )
        ids = [e.id for e in data.entities]
        assert len(ids) == len(set(ids)), "Duplicate entity IDs found!"


# ─── ArtifactAnalyzer (End-to-End) Tests ─────────────────────────────────────

class TestArtifactAnalyzer:

    def setup_method(self):
        self.analyzer = ArtifactAnalyzer()

    def test_full_pipeline_on_sample_project(self):
        data = self.analyzer.analyze_directory(SAMPLE_PROJECT)

        assert len(data.entities) > 0
        assert len(data.relationships) > 0
        assert data.metadata.get("project_id") is not None

    def test_metadata_contains_expected_keys(self):
        data = self.analyzer.analyze_directory(SAMPLE_PROJECT)
        assert "project_id" in data.metadata
        assert "project_name" in data.metadata
        assert "language_counts" in data.metadata
        assert "has_readme" in data.metadata

    def test_readme_true_for_sample_project(self):
        data = self.analyzer.analyze_directory(SAMPLE_PROJECT)
        assert data.metadata.get("has_readme") is True

    def test_all_entity_types_present(self):
        data = self.analyzer.analyze_directory(SAMPLE_PROJECT)
        types = {e.type for e in data.entities}
        assert EntityType.REPOSITORY in types
        assert EntityType.README in types
        assert EntityType.FOLDER in types
        assert EntityType.FILE in types
        assert EntityType.CLASS in types
        assert EntityType.FUNCTION in types

    def test_no_readme_project(self, tmp_path):
        """Analyzer should still create a Repository entity even without README."""
        (tmp_path / "main.py").write_text("class App: pass")
        data = self.analyzer.analyze_directory(tmp_path)
        repo_entities = [e for e in data.entities if e.type == EntityType.REPOSITORY]
        assert len(repo_entities) == 1
        assert data.metadata.get("has_readme") is False

    def test_no_duplicate_entity_ids_after_merge(self):
        data = self.analyzer.analyze_directory(SAMPLE_PROJECT)
        ids = [e.id for e in data.entities]
        assert len(ids) == len(set(ids)), "Analyzer should deduplicate entities"
