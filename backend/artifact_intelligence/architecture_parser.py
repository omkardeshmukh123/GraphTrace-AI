"""
M1 — Artifact Intelligence — Architecture Parser (Phase 4)
============================================================
Owner: Member 1 (Artifact Intelligence)

Phase 4 Goal (GT_Modules.md):
  Extract the ARCHITECTURAL layer that sits between Requirements and Code:
    - SYSTEM  : the top-level project system
    - COMPONENT: a logical subsystem (Frontend, Backend, Auth Service, etc.)
    - SERVICE  : a deployed/standalone runtime service
    - TECHNOLOGY: framework / database / tool used by a component

  Relationships produced:
    SYSTEM  -[CONTAINS]->       COMPONENT
    COMPONENT -[CONTAINS]->     SERVICE
    COMPONENT -[USES]->         TECHNOLOGY
    SERVICE   -[COMMUNICATES_WITH]-> SERVICE
    COMPONENT -[PART_OF]->      SYSTEM
    COMPONENT -[EXPOSES]->      (API entry points, optional)

Detection strategy (no LLM — pure static analysis):
  1. README.md  — section headings like "Architecture", "Services", "Components"
  2. Folder structure — top-level directories map to components
  3. Config files   — docker-compose.yml, package.json, pyproject.toml, pom.xml
  4. Well-known patterns — e.g. /frontend, /backend, /api, /auth, /db

Called by ArtifactAnalyzer._run_parsers() in analyzer.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import (
    ArtifactData, Entity, Relationship,
    EntityType, RelationshipType,
)


# ─── Phase 4 entity type constants ───────────────────────────────────────────
class ArchEntityType:
    SYSTEM      = "SYSTEM"
    COMPONENT   = "COMPONENT"
    SERVICE     = "SERVICE"
    TECHNOLOGY  = "TECHNOLOGY"


class ArchRelType:
    CONTAINS         = "CONTAINS"
    PART_OF          = "PART_OF"
    USES             = "USES"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    EXPOSES          = "EXPOSES"


# ─── Known folder → component name mapping ────────────────────────────────────
FOLDER_COMPONENT_MAP: dict[str, dict[str, str]] = {
    "frontend":       {"name": "Frontend",               "category": "presentation"},
    "ui":             {"name": "UI Layer",               "category": "presentation"},
    "client":         {"name": "Client App",             "category": "presentation"},
    "web":            {"name": "Web App",                "category": "presentation"},
    "components":     {"name": "UI Components",          "category": "presentation"},
    "hooks":          {"name": "React Hooks",            "category": "presentation"},
    "views":          {"name": "View Layer",             "category": "presentation"},
    "pages":          {"name": "Page Routing",           "category": "presentation"},
    "store":          {"name": "State Management",       "category": "presentation"},
    "backend":        {"name": "Backend",                "category": "application"},
    "src":            {"name": "Application Core",       "category": "application"},
    "api":            {"name": "API Layer",              "category": "application"},
    "server":         {"name": "Server",                 "category": "application"},
    "app":            {"name": "Application",            "category": "application"},
    "service":        {"name": "Service Layer",          "category": "application"},
    "services":       {"name": "Services",               "category": "application"},
    "functions":      {"name": "Edge & Cloud Functions", "category": "application"},
    "domain":         {"name": "Domain Layer",           "category": "application"},
    "controllers":    {"name": "Controllers",            "category": "application"},
    "handlers":       {"name": "Request Handlers",       "category": "application"},
    "routes":         {"name": "API Routes",             "category": "application"},
    "pkg":            {"name": "Packages",               "category": "application"},
    "internal":       {"name": "Internal Services",      "category": "application"},
    "supabase":       {"name": "Supabase Platform",      "category": "infrastructure"},
    "integrations":   {"name": "Integration Layer",      "category": "infrastructure"},
    "lib":            {"name": "Core Library & Utils",   "category": "application"},
    "auth":           {"name": "Auth Service",           "category": "security"},
    "authentication": {"name": "Auth Service",           "category": "security"},
    "gateway":        {"name": "API Gateway",            "category": "infrastructure"},
    "db":             {"name": "Database Layer",         "category": "data"},
    "database":       {"name": "Database Layer",         "category": "data"},
    "models":         {"name": "Data Models",            "category": "data"},
    "migrations":     {"name": "DB Migrations",          "category": "data"},
    "core":           {"name": "Core Engine",            "category": "application"},
    "engine":         {"name": "Processing Engine",      "category": "application"},
    "workers":        {"name": "Background Workers",     "category": "infrastructure"},
    "queue":          {"name": "Message Queue",          "category": "infrastructure"},
    "ml":             {"name": "ML Module",              "category": "intelligence"},
    "ai":             {"name": "AI Module",              "category": "intelligence"},
    "scripts":        {"name": "Scripts",                "category": "tooling"},
    "utils":          {"name": "Utilities",              "category": "tooling"},
    "tests":          {"name": "Test Suite",             "category": "quality"},
    "test":           {"name": "Test Suite",             "category": "quality"},
    "docs":           {"name": "Documentation",          "category": "documentation"},
    "infra":          {"name": "Infrastructure",         "category": "infrastructure"},
    "deploy":         {"name": "Deployment",             "category": "infrastructure"},
    "config":         {"name": "Configuration",          "category": "infrastructure"},
}

# ─── Known technology → category mapping ─────────────────────────────────────
TECH_CATEGORIES: dict[str, str] = {
    # Web / UI frameworks
    "fastapi":       "web-framework",   "flask":        "web-framework",
    "django":        "web-framework",   "starlette":    "web-framework",
    "express":       "web-framework",   "nestjs":       "web-framework",
    "react":         "ui-framework",    "next.js":      "ui-framework",
    "vue":           "ui-framework",    "angular":      "ui-framework",
    "tailwind":      "ui-framework",    "tailwindcss":  "ui-framework",
    "vite":          "build-tool",      "webpack":      "build-tool",
    # Databases & Backend-as-a-Service
    "supabase":      "backend-service", "firebase":     "backend-service",
    "neo4j":         "graph-database",  "postgresql":   "relational-db",
    "mysql":         "relational-db",   "mongodb":      "document-db",
    "redis":         "cache",           "sqlite":       "relational-db",
    "elasticsearch": "search-engine",   "prisma":       "orm",
    "drizzle":       "orm",
    # AI / LLM
    "langchain":     "llm-framework",   "llamaindex":   "llm-framework",
    "openai":        "llm-api",         "huggingface":  "ml-platform",
    "faiss":         "vector-db",       "chroma":       "vector-db",
    # Infrastructure & Tooling
    "docker":        "containerization","kubernetes":   "orchestration",
    "nginx":         "web-server",      "gunicorn":     "web-server",
    "vitest":        "testing",         "jest":         "testing",
    "playwright":    "testing",         "cypress":      "testing",
    # Languages & Runtimes
    "python":        "language",        "javascript":   "language",
    "typescript":    "language",        "java":         "language",
    "go":            "language",        "rust":         "language",
    "node.js":       "runtime",         "node":         "runtime",
    # Protocols
    "graphql":       "api-protocol",    "rest":         "api-protocol",
    "grpc":          "api-protocol",    "websocket":    "api-protocol",
}

# Patterns to detect services inside docker-compose / README
SERVICE_NAME_BLACKLIST = {
    "version", "volumes", "networks", "configs", "secrets", "extends",
}


class ArchitectureParser:
    """
    Phase 4 M1 parser — extracts architecture-level entities from static files.

    Produces:
      - SYSTEM entity (1 per project)
      - COMPONENT entities (logical layers / subsystems)
      - SERVICE entities (from docker-compose / process config)
      - TECHNOLOGY entities (frameworks, databases, tools)
      - PART_OF / CONTAINS / USES / COMMUNICATES_WITH relationships
    """

    def parse(
        self,
        root_path: Path,
        project_id: str,
        project_name: str,
        readme_technologies: list[str] | None = None,
    ) -> ArtifactData:
        """
        Main entry point called by ArtifactAnalyzer.

        Args:
            root_path:           Extracted project directory.
            project_id:          Stable project UUID.
            project_name:        Human-readable project name.
            readme_technologies: Technology list already extracted by ReadmeParser.

        Returns:
            ArtifactData with SYSTEM/COMPONENT/SERVICE/TECHNOLOGY entities.
        """
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        # ── 1. System entity ─────────────────────────────────────────────────
        system_id = f"system:{project_id}"
        system_entity = Entity(
            id=system_id,
            type=ArchEntityType.SYSTEM,
            name=project_name,
            properties={
                "project_id": project_id,
                "description": f"Top-level system for project {project_name}",
            },
        )
        entities.append(system_entity)

        # ── 2. Folder-based component detection ──────────────────────────────
        folder_components = self._detect_folder_components(
            root_path, project_id, system_id
        )
        entities.extend(folder_components["entities"])
        relationships.extend(folder_components["relationships"])
        component_ids: dict[str, str] = folder_components["component_ids"]

        # ── 3. Services extraction (Docker-compose + Code Services) ──────────
        services_data = self._parse_services(root_path, project_id, system_id, component_ids)
        entities.extend(services_data["entities"])
        relationships.extend(services_data["relationships"])

        # ── 4. Technology detection ──────────────────────────────────────────
        all_techs: set[str] = set()
        if readme_technologies:
            all_techs.update(t.lower() for t in readme_technologies)

        # Also scan requirements.txt / package.json / pyproject.toml
        file_techs = self._detect_tech_from_config_files(root_path)
        all_techs.update(file_techs)

        tech_entities, tech_rels = self._build_tech_entities(
            all_techs, project_id, component_ids, system_id
        )
        entities.extend(tech_entities)
        relationships.extend(tech_rels)

        # ── 5. API surface detection ─────────────────────────────────────────
        api_entities, api_rels = self._detect_api_surface(
            root_path, project_id, component_ids
        )
        entities.extend(api_entities)
        relationships.extend(api_rels)

        # ── 6. Deduplicate ───────────────────────────────────────────────────
        seen_ids: set[str] = set()
        unique_entities: list[Entity] = []
        for e in entities:
            if e.id not in seen_ids:
                seen_ids.add(e.id)
                unique_entities.append(e)

        seen_rels: set[tuple[str, str, str]] = set()
        unique_rels: list[Relationship] = []
        for r in relationships:
            key = (r.source, r.type, r.target)
            if key not in seen_rels and r.source != r.target:
                seen_rels.add(key)
                unique_rels.append(r)

        print(
            f"[M1 ArchParser] {len(unique_entities)} arch entities, "
            f"{len(unique_rels)} arch relationships"
        )

        return ArtifactData(
            entities=unique_entities,
            relationships=unique_rels,
            metadata={
                "arch_components": len([e for e in unique_entities if e.type == ArchEntityType.COMPONENT]),
                "arch_services": len([e for e in unique_entities if e.type == ArchEntityType.SERVICE]),
                "arch_technologies": len([e for e in unique_entities if e.type == ArchEntityType.TECHNOLOGY]),
            },
        )

    # ─── Folder-based component detection ─────────────────────────────────────

    def _detect_folder_components(
        self,
        root_path: Path,
        project_id: str,
        system_id: str,
    ) -> dict:
        entities: list[Entity] = []
        relationships: list[Relationship] = []
        component_ids: dict[str, str] = {}   # folder_name → component entity id

        try:
            top_dirs = [
                d for d in root_path.iterdir()
                if d.is_dir() and not d.name.startswith(".")
                   and d.name not in {"__pycache__", "node_modules", "venv", ".git", "dist", "build"}
            ]
        except PermissionError:
            return {"entities": entities, "relationships": relationships, "component_ids": component_ids}

        # Check frontend indicators in root
        is_root_frontend = any(
            (root_path / f).exists()
            for f in ["vite.config.ts", "vite.config.js", "tailwind.config.ts", "tailwind.config.js", "postcss.config.js"]
        )

        for folder in top_dirs:
            fname = folder.name.lower()
            if fname not in FOLDER_COMPONENT_MAP:
                continue

            info = dict(FOLDER_COMPONENT_MAP[fname])
            # If src is used with frontend config or UI subfolders, categorize as Frontend UI
            if fname == "src":
                has_ui_subfolders = any(
                    (folder / sub).is_dir() for sub in ["components", "hooks", "pages", "views", "ui"]
                )
                if is_root_frontend or has_ui_subfolders:
                    info["name"] = "Frontend UI"
                    info["category"] = "presentation"

            comp_id = f"component:{project_id}:{fname}"
            component_ids[fname] = comp_id

            # Gather sub-folder names as sub-components hint
            try:
                sub_folders = [
                    d.name for d in folder.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                ]
            except PermissionError:
                sub_folders = []

            comp_entity = Entity(
                id=comp_id,
                type=ArchEntityType.COMPONENT,
                name=info["name"],
                properties={
                    "folder": fname,
                    "category": info["category"],
                    "path": str(folder.relative_to(root_path)).replace("\\", "/"),
                    "sub_folders": sub_folders[:20],
                },
            )
            entities.append(comp_entity)

            # COMPONENT -[PART_OF]-> SYSTEM
            relationships.append(Relationship(
                source=comp_id,
                type=ArchRelType.PART_OF,
                target=system_id,
            ))
            # SYSTEM -[CONTAINS]-> COMPONENT
            relationships.append(Relationship(
                source=system_id,
                type=ArchRelType.CONTAINS,
                target=comp_id,
            ))
            # COMPONENT -[CONTAINS]-> FOLDER (link to code tree)
            relationships.append(Relationship(
                source=comp_id,
                type=ArchRelType.CONTAINS,
                target=f"folder:{project_id}:{fname}",
            ))

        # Check for modular sub-components in src and supabase
        sub_modules = [
            ("src/integrations", "integrations", "Integration Layer", "infrastructure"),
            ("src/lib", "lib", "Core Library & Security", "security"),
            ("supabase/functions", "functions", "Edge & Cloud Functions", "application"),
            ("src/test", "test", "Quality & Test Suite", "quality"),
        ]
        for subpath, subkey, subname, subcat in sub_modules:
            p = root_path / Path(subpath)
            if p.is_dir() and subkey not in component_ids:
                sub_comp_id = f"component:{project_id}:{subkey}"
                component_ids[subkey] = sub_comp_id
                entities.append(Entity(
                    id=sub_comp_id,
                    type=ArchEntityType.COMPONENT,
                    name=subname,
                    properties={
                        "folder": subpath,
                        "category": subcat,
                        "path": subpath,
                    },
                ))
                relationships.append(Relationship(source=sub_comp_id, type=ArchRelType.PART_OF, target=system_id))
                relationships.append(Relationship(source=system_id, type=ArchRelType.CONTAINS, target=sub_comp_id))

        # Universal fallback: if no components detected, create Application Core
        if not entities:
            fallback_id = f"component:{project_id}:app_core"
            component_ids["app_core"] = fallback_id
            entities.append(Entity(
                id=fallback_id,
                type=ArchEntityType.COMPONENT,
                name="Application Core",
                properties={"folder": ".", "category": "application", "path": "."},
            ))
            relationships.append(Relationship(source=fallback_id, type=ArchRelType.PART_OF, target=system_id))
            relationships.append(Relationship(source=system_id, type=ArchRelType.CONTAINS, target=fallback_id))

        # Detect inter-component COMMUNICATES_WITH from known patterns
        COMM_PAIRS = [
            ("frontend", "backend"),
            ("frontend", "src"),
            ("frontend", "api"),
            ("frontend", "supabase"),
            ("frontend", "integrations"),
            ("frontend", "functions"),
            ("integrations", "supabase"),
            ("integrations", "functions"),
            ("integrations", "lib"),
            ("client", "api"),
            ("client", "backend"),
            ("client", "src"),
            ("web", "backend"),
            ("web", "src"),
            ("backend", "db"),
            ("backend", "database"),
            ("src", "db"),
            ("src", "database"),
            ("api", "db"),
            ("service", "db"),
            ("auth", "db"),
            ("backend", "workers"),
            ("src", "workers"),
        ]
        for src_folder, tgt_folder in COMM_PAIRS:
            if src_folder in component_ids and tgt_folder in component_ids:
                relationships.append(Relationship(
                    source=component_ids[src_folder],
                    type=ArchRelType.COMMUNICATES_WITH,
                    target=component_ids[tgt_folder],
                ))

        return {
            "entities": entities,
            "relationships": relationships,
            "component_ids": component_ids,
        }

    # ─── Service extraction (Docker-compose + Edge Functions + Code Services) ─

    def _parse_services(
        self,
        root_path: Path,
        project_id: str,
        system_id: str,
        component_ids: dict[str, str],
    ) -> dict:
        """Extract runtime services from docker-compose, edge functions, or code service files."""
        entities: list[Entity] = []
        relationships: list[Relationship] = []
        service_ids: dict[str, str] = {}

        # 1. First attempt docker-compose
        docker_res = self._parse_docker_compose(root_path, project_id, system_id)
        entities.extend(docker_res["entities"])
        relationships.extend(docker_res["relationships"])
        for e in docker_res["entities"]:
            service_ids[e.properties.get("service_name", e.name.lower())] = e.id

        # 2a. Detect Edge & Serverless Functions (e.g. supabase/functions/*/index.ts)
        edge_patterns = [
            "**/functions/*/index.ts", "**/functions/*/index.js",
            "**/functions/*/*.py", "**/functions/*/*.go"
        ]
        for pat in edge_patterns:
            try:
                for match in root_path.glob(pat):
                    if match.is_file():
                        fn_dir = match.parent.name
                        svc_key = fn_dir.lower().replace("-", "_")
                        clean_name = fn_dir.replace("-", " ").replace("_", " ").title() + " Service"
                        if svc_key in service_ids:
                            continue
                        svc_id = f"service:{project_id}:{svc_key}"
                        service_ids[svc_key] = svc_id
                        rel_path = str(match.relative_to(root_path)).replace("\\", "/")
                        entities.append(Entity(
                            id=svc_id,
                            type=ArchEntityType.SERVICE,
                            name=clean_name,
                            properties={"service_name": svc_key, "source_file": rel_path},
                        ))
                        relationships.append(Relationship(
                            source=svc_id,
                            type=ArchRelType.PART_OF,
                            target=system_id,
                        ))
                        # Connect parent component -[CONTAINS]-> SERVICE & -[EXPOSES]-> SERVICE
                        connected = False
                        for folder_key in ("functions", "supabase", "backend", "api", "src"):
                            if folder_key in component_ids:
                                comp_id = component_ids[folder_key]
                                relationships.append(Relationship(source=comp_id, type=ArchRelType.CONTAINS, target=svc_id))
                                relationships.append(Relationship(source=comp_id, type=ArchRelType.EXPOSES, target=svc_id))
                                connected = True
                                break
                        if not connected and component_ids:
                            first_comp = list(component_ids.values())[0]
                            relationships.append(Relationship(source=first_comp, type=ArchRelType.CONTAINS, target=svc_id))
                            relationships.append(Relationship(source=first_comp, type=ArchRelType.EXPOSES, target=svc_id))
            except Exception:
                pass

        # 2b. Detect Client Gateways (e.g. client.ts, client.js)
        try:
            for match in root_path.glob("**/client.*"):
                if match.is_file() and not match.name.startswith("test"):
                    rel_path = str(match.relative_to(root_path)).replace("\\", "/")
                    parent_name = match.parent.name
                    svc_key = f"{parent_name}_client" if parent_name not in ("src", "lib") else "api_client"
                    clean_name = svc_key.replace("_", " ").title() + " Service"
                    if svc_key not in service_ids:
                        svc_id = f"service:{project_id}:{svc_key}"
                        service_ids[svc_key] = svc_id
                        entities.append(Entity(
                            id=svc_id,
                            type=ArchEntityType.SERVICE,
                            name=clean_name,
                            properties={"service_name": svc_key, "source_file": rel_path},
                        ))
                        relationships.append(Relationship(source=svc_id, type=ArchRelType.PART_OF, target=system_id))
                        for folder_key in ("integrations", "frontend", "src", "client"):
                            if folder_key in component_ids:
                                comp_id = component_ids[folder_key]
                                relationships.append(Relationship(source=comp_id, type=ArchRelType.CONTAINS, target=svc_id))
                                relationships.append(Relationship(source=comp_id, type=ArchRelType.EXPOSES, target=svc_id))
                                break
        except Exception:
            pass

        # 2c. Detect code-level services (e.g. auth_service.py, order_service.py, api_gateway.py, *.service.ts)
        service_patterns = [
            "**/*_service.py", "**/*_gateway.py", "**/*_logger.py",
            "**/*.service.ts", "**/*.service.js", "**/*.controller.ts",
        ]
        found_service_files: list[Path] = []
        for pat in service_patterns:
            try:
                for match in root_path.glob(pat):
                    if match.is_file() and not match.name.startswith("test_"):
                        found_service_files.append(match)
            except Exception:
                pass

        for sfile in found_service_files:
            base = sfile.stem.split(".")[0]  # handle .service.ts
            clean_name = base.replace("_", " ").replace("-", " ").title().replace(" ", "")
            svc_key = base.lower().replace("-", "_")

            if svc_key in service_ids:
                continue

            svc_id = f"service:{project_id}:{svc_key}"
            service_ids[svc_key] = svc_id

            rel_path = str(sfile.relative_to(root_path)).replace("\\", "/")
            svc_entity = Entity(
                id=svc_id,
                type=ArchEntityType.SERVICE,
                name=clean_name,
                properties={
                    "service_name": svc_key,
                    "source_file": rel_path,
                },
            )
            entities.append(svc_entity)

            # SERVICE -[PART_OF]-> SYSTEM
            relationships.append(Relationship(
                source=svc_id,
                type=ArchRelType.PART_OF,
                target=system_id,
            ))

            # Connect parent component -[CONTAINS]-> SERVICE & -[EXPOSES]-> SERVICE
            for folder_key, comp_id in component_ids.items():
                if rel_path.startswith(folder_key + "/") or rel_path.startswith(folder_key + "\\"):
                    relationships.append(Relationship(
                        source=comp_id,
                        type=ArchRelType.CONTAINS,
                        target=svc_id,
                    ))
                    relationships.append(Relationship(
                        source=comp_id,
                        type=ArchRelType.EXPOSES,
                        target=svc_id,
                    ))
                    break

        # 3. Known inter-service communication patterns
        SVC_COMMS = [
            ("api_gateway", "auth_service"),
            ("api_gateway", "order_service"),
            ("api_gateway", "inventory_service"),
            ("api_gateway", "payment_gateway"),
            ("order_service", "payment_gateway"),
            ("order_service", "inventory_service"),
            ("order_service", "notification_service"),
            ("order_service", "audit_logger"),
            ("auth_service", "audit_logger"),
            ("validate_key", "vault"),
        ]
        for src_k, tgt_k in SVC_COMMS:
            if src_k in service_ids and tgt_k in service_ids:
                relationships.append(Relationship(
                    source=service_ids[src_k],
                    type=ArchRelType.COMMUNICATES_WITH,
                    target=service_ids[tgt_k],
                ))

        # Connect client gateways to other services
        client_svcs = [k for k in service_ids if "client" in k or "gateway" in k]
        other_svcs = [k for k in service_ids if k not in client_svcs]
        for c_k in client_svcs:
            for o_k in other_svcs:
                relationships.append(Relationship(
                    source=service_ids[c_k],
                    type=ArchRelType.COMMUNICATES_WITH,
                    target=service_ids[o_k],
                ))

        return {"entities": entities, "relationships": relationships}

    def _parse_docker_compose(
        self,
        root_path: Path,
        project_id: str,
        system_id: str,
    ) -> dict:
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        compose_files = [
            root_path / "docker-compose.yml",
            root_path / "docker-compose.yaml",
            root_path / "docker-compose.prod.yml",
        ]

        for compose_file in compose_files:
            if not compose_file.exists():
                continue
            try:
                content = compose_file.read_text(encoding="utf-8", errors="ignore")
                services = self._extract_docker_services(content, project_id, system_id)
                entities.extend(services["entities"])
                relationships.extend(services["relationships"])
                break  # Parse only first found
            except Exception:
                continue

        return {"entities": entities, "relationships": relationships}

    def _extract_docker_services(
        self,
        content: str,
        project_id: str,
        system_id: str,
    ) -> dict:
        """
        Parse docker-compose YAML (with regex, no yaml lib required).
        Extracts service names and their image/port properties.
        """
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        # Match service names under `services:` block
        # services:
        #   web:       ← service name (2-space indent)
        #   db:
        in_services = False
        service_indent_level = None
        current_service: str | None = None
        service_props: dict[str, Any] = {}
        service_entities: dict[str, str] = {}  # name → id

        for line in content.splitlines():
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())

            if stripped == "services:":
                in_services = True
                service_indent_level = None
                continue

            if not in_services:
                continue

            # Stop if we hit a top-level key that isn't services
            if indent == 0 and stripped and not stripped.startswith("#"):
                if not stripped.startswith("services"):
                    in_services = False
                continue

            # Service-level entries: 2-space indent
            if service_indent_level is None and indent > 0 and stripped.endswith(":"):
                service_indent_level = indent

            if service_indent_level and indent == service_indent_level and stripped.endswith(":"):
                # New service
                if current_service and current_service not in SERVICE_NAME_BLACKLIST:
                    svc_id = f"service:{project_id}:{current_service}"
                    svc_entity = Entity(
                        id=svc_id,
                        type=ArchEntityType.SERVICE,
                        name=current_service.capitalize(),
                        properties={
                            "service_name": current_service,
                            **{k: v for k, v in service_props.items() if v},
                        },
                    )
                    entities.append(svc_entity)
                    service_entities[current_service] = svc_id
                    relationships.append(Relationship(
                        source=svc_id,
                        type=ArchRelType.PART_OF,
                        target=system_id,
                    ))

                current_service = stripped[:-1].strip()
                service_props = {}

            elif current_service and stripped.startswith("image:"):
                service_props["image"] = stripped.split(":", 1)[1].strip()
            elif current_service and stripped.startswith("ports:"):
                pass  # collect from next lines
            elif current_service and re.match(r"^\-\s+\d+:\d+", stripped):
                service_props.setdefault("ports", [])
                service_props["ports"].append(stripped.lstrip("- ").strip())

        # Last service
        if current_service and current_service not in SERVICE_NAME_BLACKLIST:
            svc_id = f"service:{project_id}:{current_service}"
            svc_entity = Entity(
                id=svc_id,
                type=ArchEntityType.SERVICE,
                name=current_service.capitalize(),
                properties={"service_name": current_service, **service_props},
            )
            entities.append(svc_entity)
            service_entities[current_service] = svc_id
            relationships.append(Relationship(
                source=svc_id,
                type=ArchRelType.PART_OF,
                target=system_id,
            ))

        # Add COMMUNICATES_WITH between known service pairs
        svc_names = list(service_entities.keys())
        DB_KEYWORDS = {"db", "database", "postgres", "mysql", "mongo", "redis", "neo4j"}
        WEB_KEYWORDS = {"web", "api", "backend", "app", "server", "frontend"}
        for src in svc_names:
            if src in WEB_KEYWORDS:
                for tgt in svc_names:
                    if tgt != src and tgt in DB_KEYWORDS:
                        relationships.append(Relationship(
                            source=service_entities[src],
                            type=ArchRelType.COMMUNICATES_WITH,
                            target=service_entities[tgt],
                        ))

        return {"entities": entities, "relationships": relationships}

    # ─── Technology detection from config files ────────────────────────────────

    def _detect_tech_from_config_files(self, root_path: Path) -> set[str]:
        """Scan requirements.txt, package.json, pyproject.toml for tech names."""
        found: set[str] = set()

        # Python requirements
        for req_file in ["requirements.txt", "requirements-dev.txt", "requirements-prod.txt"]:
            path = root_path / req_file
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore").lower()
                    for tech in TECH_CATEGORIES:
                        if tech in content:
                            found.add(tech)
                except Exception:
                    pass

        # Node package.json
        pkg_path = root_path / "package.json"
        if not pkg_path.exists():
            # Try looking in frontend/ subdirectory
            pkg_path = root_path / "frontend" / "package.json"

        if pkg_path.exists():
            try:
                data = json.loads(pkg_path.read_text(encoding="utf-8", errors="ignore"))
                all_deps: dict = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }
                dep_names = " ".join(all_deps.keys()).lower()
                for tech in TECH_CATEGORIES:
                    if tech in dep_names:
                        found.add(tech)
                # Special cases
                if "react" in dep_names:
                    found.add("react")
                if "vite" in dep_names:
                    found.add("vite")
                if "next" in dep_names:
                    found.add("next.js")
            except Exception:
                pass

        # pyproject.toml
        pyproject = root_path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8", errors="ignore").lower()
                for tech in TECH_CATEGORIES:
                    if tech in content:
                        found.add(tech)
            except Exception:
                pass

        # Config files presence detection
        config_checks = [
            ("tailwind.config.ts", ["tailwind", "tailwindcss"]),
            ("tailwind.config.js", ["tailwind", "tailwindcss"]),
            ("vite.config.ts", ["vite"]),
            ("vite.config.js", ["vite"]),
            ("vitest.config.ts", ["vitest"]),
            ("vitest.config.js", ["vitest"]),
            ("tsconfig.json", ["typescript"]),
            ("docker-compose.yml", ["docker"]),
            ("Dockerfile", ["docker"]),
        ]
        for cfg_file, techs in config_checks:
            if (root_path / cfg_file).exists():
                found.update(techs)

        if (root_path / "supabase").is_dir():
            found.update(["supabase", "postgresql"])

        return found

    def _build_tech_entities(
        self,
        all_techs: set[str],
        project_id: str,
        component_ids: dict[str, str],
        system_id: str,
    ) -> tuple[list[Entity], list[Relationship]]:
        """Convert detected tech names into TECHNOLOGY entities with USES rels."""
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        # Tech → component affinity (which component uses which tech)
        TECH_TO_COMPONENT: dict[str, list[str]] = {
            "react":       ["frontend", "ui", "client", "web", "src"],
            "next.js":     ["frontend", "ui", "client", "src"],
            "vue":         ["frontend", "ui", "client", "src"],
            "angular":     ["frontend", "ui", "client", "src"],
            "vite":        ["frontend", "ui", "client", "src"],
            "tailwind":    ["frontend", "ui", "client", "src"],
            "tailwindcss": ["frontend", "ui", "client", "src"],
            "typescript":  ["frontend", "supabase", "integrations", "lib", "src"],
            "javascript":  ["frontend", "src", "client"],
            "node.js":     ["supabase", "functions", "backend", "frontend", "src"],
            "node":        ["supabase", "functions", "backend", "frontend", "src"],
            "supabase":    ["supabase", "functions", "integrations"],
            "fastapi":     ["backend", "api", "app", "server", "src"],
            "flask":       ["backend", "api", "app", "src"],
            "django":      ["backend", "api", "app", "src"],
            "neo4j":       ["backend", "db", "database", "core", "src"],
            "redis":       ["backend", "workers", "db", "src"],
            "postgresql":  ["supabase", "db", "database", "backend", "src"],
            "mongodb":     ["db", "database", "backend", "src"],
            "langchain":   ["backend", "core", "ai", "ml", "src"],
            "openai":      ["integrations", "backend", "core", "ai", "ml", "src", "supabase"],
            "faiss":       ["backend", "core", "ai", "ml", "src"],
            "chroma":      ["backend", "core", "ai", "ml", "src"],
            "vitest":      ["test", "tests"],
            "jest":        ["test", "tests"],
            "go":          ["supabase", "backend", "core", "src"],
            "docker":      [None],
            "kubernetes":  [None],
        }

        for tech in all_techs:
            tech_id = f"technology:{project_id}:{tech.replace('.', '_')}"
            category = TECH_CATEGORIES.get(tech, "tool")
            tech_entity = Entity(
                id=tech_id,
                type=ArchEntityType.TECHNOLOGY,
                name=tech.title(),
                properties={
                    "tech_name": tech,
                    "category": category,
                },
            )
            entities.append(tech_entity)

            # Connect tech to relevant components
            affinity_folders = TECH_TO_COMPONENT.get(tech)
            linked = False
            if affinity_folders:
                for folder in affinity_folders:
                    if folder and folder in component_ids:
                        relationships.append(Relationship(
                            source=component_ids[folder],
                            type=ArchRelType.USES,
                            target=tech_id,
                        ))
                        linked = True

            if not linked:
                # Connect to SYSTEM as fallback
                relationships.append(Relationship(
                    source=system_id,
                    type=ArchRelType.USES,
                    target=tech_id,
                ))

        return entities, relationships

    # ─── API surface detection ────────────────────────────────────────────────

    def _detect_api_surface(
        self,
        root_path: Path,
        project_id: str,
        component_ids: dict[str, str],
    ) -> tuple[list[Entity], list[Relationship]]:
        """
        Detect API route files and create EXPOSES relationships from backend component.
        Scans for common API definition patterns.
        """
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        # Patterns that indicate API route definition files
        api_file_patterns = [
            "**/routes/*.py", "**/routers/*.py", "**/api/*.py",
            "**/views.py", "**/endpoints.py", "**/controllers/*.py",
            "**/controllers.py", "**/api_gateway.py",
            "**/routes/*.ts", "**/routes/*.js", "**/controllers/*.ts",
        ]

        backend_comp_id = (
            component_ids.get("backend")
            or component_ids.get("api")
            or component_ids.get("server")
            or component_ids.get("app")
            or component_ids.get("src")
            or component_ids.get("core")
        )

        if not backend_comp_id:
            return entities, relationships

        api_files_found: list[str] = []
        try:
            for pattern in api_file_patterns:
                for match in root_path.glob(pattern):
                    relative = str(match.relative_to(root_path)).replace("\\", "/")
                    api_files_found.append(relative)
        except Exception:
            pass

        if api_files_found:
            # Create a synthetic API Surface entity
            api_surface_id = f"component:{project_id}:api_surface"
            api_entity = Entity(
                id=api_surface_id,
                type=ArchEntityType.COMPONENT,
                name="API Surface",
                properties={
                    "category": "api",
                    "route_files": api_files_found[:10],
                    "route_file_count": len(api_files_found),
                    "description": "REST API routes exposed by the backend",
                },
            )
            entities.append(api_entity)

            # Backend EXPOSES API Surface
            relationships.append(Relationship(
                source=backend_comp_id,
                type=ArchRelType.EXPOSES,
                target=api_surface_id,
            ))

        return entities, relationships
