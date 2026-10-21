"""Bounded graph traversals shared by the local and Neo4j adapters."""

from collections import deque
import re

from backend.app.errors import AppError
from backend.app.models import (
    ARCH_TYPES, CODE_TYPES, DEPENDENCY_TYPES,
    ArchitectureStats, ArchitectureView, ArtifactGraph,
    ComponentDependencyView, ComponentSummary, DependencyView, GraphView,
    Node, PathView, Relationship, RequirementSummary, TechItem,
    TechStackView, TraceabilityView,
)


def find_node(graph: ArtifactGraph, node_id: str) -> Node:
    for node in graph.nodes:
        if node.id == node_id:
            return node
    raise AppError(404, "node_not_found", "Node does not exist in this project.")


def filter_graph(graph: ArtifactGraph, node_types: list[str] | None, relationship_types: list[str] | None, search: str | None) -> GraphView:
    nodes = [node for node in graph.nodes if
             (not node_types or node.type in node_types) and
             (not search or search.casefold() in node.name.casefold() or search.casefold() in node.id.casefold())]
    ids = {node.id for node in nodes}
    edges = [edge for edge in graph.relationships if edge.source in ids and edge.target in ids
             and (not relationship_types or edge.type in relationship_types)]
    return GraphView(project_id=graph.project_id, nodes=nodes, relationships=edges)


def adjacency(edges: list[Relationship], types: set[str], reverse: bool = False, both: bool = False):
    result = {}
    for edge in edges:
        if edge.type not in types:
            continue
        source, target = (edge.target, edge.source) if reverse else (edge.source, edge.target)
        result.setdefault(source, []).append((target, edge))
        if both:
            result.setdefault(target, []).append((source, edge))
    return result


def traverse(root: str, adjacent: dict, max_depth: int):
    distances = {root: 0}
    parents = {}
    pending = deque([root])
    while pending:
        current = pending.popleft()
        if distances[current] == max_depth:
            continue
        for target, edge in adjacent.get(current, []):
            if target not in distances:
                distances[target] = distances[current] + 1
                parents[target] = (current, edge)
                pending.append(target)
    limited = any(target not in distances for source in distances for target, _ in adjacent.get(source, []))
    return distances, parents, limited


def dependencies(graph: ArtifactGraph, node_id: str, direction: str, max_depth: int, types: list[str] | None) -> DependencyView:
    find_node(graph, node_id)
    selected = set(types) if types else DEPENDENCY_TYPES
    adjacent = adjacency(graph.relationships, selected, reverse=direction == "upstream")
    distances, _, limited = traverse(node_id, adjacent, max_depth)
    return DependencyView(
        project_id=graph.project_id, root=node_id, direction=direction,
        nodes=[node for node in graph.nodes if node.id in distances],
        relationships=[edge for edge in graph.relationships if edge.type in selected
                       and edge.source in distances and edge.target in distances],
        distances=distances, depth_limited=limited,
    )


def shortest_path(graph: ArtifactGraph, source: str, target: str, max_depth: int, directed: bool, types: list[str] | None) -> PathView:
    find_node(graph, source)
    find_node(graph, target)
    selected = set(types) if types else {edge.type for edge in graph.relationships}
    adjacent = adjacency(graph.relationships, selected, both=not directed)
    distances, parents, _ = traverse(source, adjacent, max_depth)
    node_ids, edges = [], []
    if target in distances:
        node_ids = [target]
        while node_ids[-1] != source:
            previous, edge = parents[node_ids[-1]]
            node_ids.append(previous)
            edges.append(edge)
        node_ids.reverse()
        edges.reverse()
    return PathView(project_id=graph.project_id, found=target in distances, node_ids=node_ids,
                    relationships=edges, max_depth=max_depth, directed=directed)


def requirements(graph: ArtifactGraph) -> list[RequirementSummary]:
    mappings = {}
    for edge in graph.relationships:
        if edge.type == "IMPLEMENTED_BY":
            mappings[edge.source] = mappings.get(edge.source, 0) + 1
    return [RequirementSummary(requirement=node, mapping_status="mapped" if mappings.get(node.id) else "unmapped",
                               implementation_count=mappings.get(node.id, 0))
            for node in graph.nodes if node.type == "REQUIREMENT"]


def traceability(graph: ArtifactGraph, requirement_id: str, max_depth: int) -> TraceabilityView:
    requirement = find_node(graph, requirement_id)
    if requirement.type != "REQUIREMENT":
        raise AppError(422, "not_a_requirement", "Select a REQUIREMENT node.")
    mappings = [edge for edge in graph.relationships if edge.source == requirement_id and edge.type == "IMPLEMENTED_BY"]
    # Only this requirement's explicit mappings are evidence. Subsequent code paths
    # provide context and must never imply that other requirements are implemented.
    context = [edge for edge in graph.relationships if edge.type in DEPENDENCY_TYPES | {"CONTAINS"}]
    adjacent = adjacency(mappings + context, DEPENDENCY_TYPES | {"CONTAINS", "IMPLEMENTED_BY"})
    distances, parents, limited = traverse(requirement_id, adjacent, max_depth)
    paths = []
    for node_id in distances:
        if node_id == requirement_id:
            continue
        path = [node_id]
        while path[-1] != requirement_id:
            path.append(parents[path[-1]][0])
        paths.append(list(reversed(path)))
    return TraceabilityView(
        project_id=graph.project_id, requirement=requirement,
        mapping_status="mapped" if mappings else "unmapped",
        implementation_ids=[edge.target for edge in mappings], evidence_paths=paths,
        nodes=[node for node in graph.nodes if node.id in distances],
        relationships=[edge for edge in mappings + context if edge.source in distances and edge.target in distances],
        depth_limited=limited,
    )


# ─── Phase 4 — Architecture Intelligence Queries ─────────────────────────────

def ensure_architecture(graph: ArtifactGraph) -> ArtifactGraph:
    """
    Guarantees the graph contains architectural entities (SYSTEM, COMPONENT, SERVICE, TECHNOLOGY).
    If missing (such as projects imported before Phase 4 or repositories with arbitrary layout),
    dynamically synthesizes architectural entities and relationships from code files, packages,
    and documentation.
    """
    has_components = any(n.type == "COMPONENT" for n in graph.nodes)
    if has_components:
        return graph

    project_id = graph.project_id
    project_node = next((n for n in graph.nodes if n.id == project_id), None) or next((n for n in graph.nodes if n.type == "PROJECT"), None)
    project_name = project_node.name if project_node else "System"

    readme_node = next((n for n in graph.nodes if n.type == "DOCUMENT" and "readme" in n.name.lower()), None)
    system_desc = (readme_node.properties.get("description") if readme_node else "") or f"Top-level architecture for {project_name}"

    new_nodes = list(graph.nodes)
    new_rels = list(graph.relationships)
    seen_ids = {n.id for n in new_nodes}
    seen_rel_keys = {(r.source, r.type, r.target) for r in new_rels}

    # 1. System entity
    system_id = f"system:{project_id}"
    if system_id not in seen_ids:
        new_nodes.append(Node(id=system_id, type="SYSTEM", name=project_name, properties={"project_id": project_id, "description": system_desc}))
        seen_ids.add(system_id)

    # 2. Gather paths
    file_nodes = [n for n in graph.nodes if n.type == "FILE"]
    pkg_nodes = [n for n in graph.nodes if n.type == "PACKAGE"]
    all_paths = [str(f.properties.get("path") or f.properties.get("file_path") or f.name).replace("\\", "/") for f in file_nodes]
    pkg_paths = [str(p.properties.get("path") or p.name).replace("\\", "/") for p in pkg_nodes]
    combined_paths = all_paths + pkg_paths

    # 3. Detect components
    components_def: list[tuple[str, str, str, str]] = []

    # Frontend UI check
    is_frontend = (
        any(p.startswith(("frontend", "client", "web", "ui")) for p in combined_paths) or
        any("vite.config" in p or "tailwind" in p or "postcss.config" in p for p in combined_paths) or
        any(p.startswith("src") and any(k in p for k in ("components", "hooks", "pages", "views", "ui", "toast")) for p in combined_paths)
    )
    if is_frontend:
        components_def.append(("frontend", "Frontend UI", "presentation", "src" if any(p.startswith("src") for p in combined_paths) else "frontend"))

    # Serverless / Cloud Functions / Supabase
    if any("supabase" in p or "functions" in p for p in combined_paths):
        components_def.append(("supabase", "Supabase Cloud Platform", "infrastructure", "supabase"))

    # Integrations
    if any("integrations" in p or "lovable" in p or "gateway" in p for p in combined_paths):
        components_def.append(("integrations", "Integration Layer", "infrastructure", "src/integrations"))

    # Core library / Security
    if any("lib" in p or "core" in p or "crypto" in p or "vault" in p for p in combined_paths):
        components_def.append(("core", "Security & Core Library", "security", "src/lib"))

    # Backend / API (if present and distinct)
    if any(p.startswith(("backend", "api", "server")) for p in combined_paths):
        components_def.append(("backend", "Backend API Services", "application", "backend"))

    # Quality & Test Suite
    if any("test" in p or "spec" in p for p in combined_paths):
        components_def.append(("test", "Quality & Test Suite", "quality", "src/test"))

    # Fallback if no components detected
    if not components_def:
        components_def.append(("core_app", f"{project_name} Application", "application", "."))

    comp_ids: dict[str, str] = {}
    for c_key, c_name, c_cat, c_folder in components_def:
        comp_id = f"component:{project_id}:{c_key}"
        comp_ids[c_key] = comp_id
        if comp_id not in seen_ids:
            new_nodes.append(Node(id=comp_id, type="COMPONENT", name=c_name, properties={"folder": c_folder, "category": c_cat, "path": c_folder}))
            seen_ids.add(comp_id)
        for r_src, r_type, r_tgt in [(system_id, "CONTAINS", comp_id), (comp_id, "PART_OF", system_id)]:
            if (r_src, r_type, r_tgt) not in seen_rel_keys:
                new_rels.append(Relationship(source=r_src, type=r_type, target=r_tgt))
                seen_rel_keys.add((r_src, r_type, r_tgt))

    # 4. Detect services
    service_ids: dict[str, str] = {}
    for p in all_paths:
        m = re.search(r"supabase/functions/([^/]+)/", p) or re.search(r"functions/([^/]+)/", p)
        if m:
            fn_name = m.group(1)
            svc_key = fn_name.lower().replace("-", "_")
            if svc_key not in service_ids:
                svc_id = f"service:{project_id}:{svc_key}"
                service_ids[svc_key] = svc_id
                svc_clean = fn_name.replace("-", " ").replace("_", " ").title() + " Service"
                if svc_id not in seen_ids:
                    new_nodes.append(Node(id=svc_id, type="SERVICE", name=svc_clean, properties={"service_name": svc_key, "source_file": p}))
                    seen_ids.add(svc_id)
                parent_comp = comp_ids.get("supabase") or comp_ids.get("backend") or list(comp_ids.values())[0]
                for r_src, r_type, r_tgt in [(parent_comp, "CONTAINS", svc_id), (parent_comp, "EXPOSES", svc_id), (svc_id, "PART_OF", system_id)]:
                    if (r_src, r_type, r_tgt) not in seen_rel_keys:
                        new_rels.append(Relationship(source=r_src, type=r_type, target=r_tgt))
                        seen_rel_keys.add((r_src, r_type, r_tgt))
        elif "client.ts" in p or "client.js" in p or "client.py" in p:
            svc_key = "supabase_client" if "supabase" in p else "api_client"
            if svc_key not in service_ids:
                svc_id = f"service:{project_id}:{svc_key}"
                service_ids[svc_key] = svc_id
                svc_clean = "Supabase Client Gateway" if "supabase" in p else "API Client Gateway"
                if svc_id not in seen_ids:
                    new_nodes.append(Node(id=svc_id, type="SERVICE", name=svc_clean, properties={"service_name": svc_key, "source_file": p}))
                    seen_ids.add(svc_id)
                parent_comp = comp_ids.get("integrations") or comp_ids.get("frontend") or list(comp_ids.values())[0]
                for r_src, r_type, r_tgt in [(parent_comp, "CONTAINS", svc_id), (parent_comp, "EXPOSES", svc_id), (svc_id, "PART_OF", system_id)]:
                    if (r_src, r_type, r_tgt) not in seen_rel_keys:
                        new_rels.append(Relationship(source=r_src, type=r_type, target=r_tgt))
                        seen_rel_keys.add((r_src, r_type, r_tgt))

    # Inter-service communications
    for c_k in [k for k in service_ids if "client" in k or "gateway" in k]:
        c_id = service_ids[c_k]
        for s_key, s_id in service_ids.items():
            if s_key != c_k and (c_id, "COMMUNICATES_WITH", s_id) not in seen_rel_keys:
                new_rels.append(Relationship(source=c_id, type="COMMUNICATES_WITH", target=s_id))
                seen_rel_keys.add((c_id, "COMMUNICATES_WITH", s_id))

    if "validate_key" in service_ids and "vault" in service_ids:
        k = (service_ids["validate_key"], "COMMUNICATES_WITH", service_ids["vault"])
        if k not in seen_rel_keys:
            new_rels.append(Relationship(source=k[0], type="COMMUNICATES_WITH", target=k[2]))
            seen_rel_keys.add(k)

    # Inter-component communications
    c_pairs = [
        ("frontend", "supabase"), ("frontend", "integrations"),
        ("integrations", "supabase"), ("integrations", "core"),
        ("frontend", "backend"), ("backend", "core"),
    ]
    for c1, c2 in c_pairs:
        if c1 in comp_ids and c2 in comp_ids:
            k = (comp_ids[c1], "COMMUNICATES_WITH", comp_ids[c2])
            if k not in seen_rel_keys:
                new_rels.append(Relationship(source=k[0], type="COMMUNICATES_WITH", target=k[2]))
                seen_rel_keys.add(k)

    # 5. Detect technologies
    techs: set[str] = set()
    if readme_node:
        techs.update(readme_node.properties.get("technologies", []))
    if any("vite.config" in p for p in combined_paths): techs.add("Vite")
    if any("tailwind" in p for p in combined_paths): techs.add("Tailwind CSS")
    if any("vitest" in p for p in combined_paths): techs.add("Vitest")
    if any(p.endswith((".ts", ".tsx")) for p in all_paths): techs.add("TypeScript")
    if any(p.endswith((".py",)) for p in all_paths): techs.add("Python")
    if any("supabase" in p for p in combined_paths): techs.add("Supabase")

    TECH_MAP = {
        "react": ("ui-framework", ["frontend"]),
        "typescript": ("language", ["frontend", "supabase", "integrations", "core"]),
        "python": ("language", ["backend", "core"]),
        "tailwind css": ("ui-framework", ["frontend"]),
        "vite": ("build-tool", ["frontend"]),
        "vitest": ("testing", ["test"]),
        "supabase": ("backend-service", ["supabase", "integrations"]),
        "postgresql": ("relational-db", ["supabase"]),
        "node.js": ("runtime", ["supabase", "frontend"]),
        "openai": ("llm-api", ["integrations", "supabase"]),
        "go": ("language", ["supabase"]),
    }
    for t in techs:
        t_clean = t.strip()
        t_key = t_clean.lower()
        cat, aff = TECH_MAP.get(t_key, ("tool", []))
        safe_tech_name = re.sub(r"[^a-zA-Z0-9_]", "_", t_key)
        tech_id = f"technology:{project_id}:{safe_tech_name}"
        if tech_id not in seen_ids:
            new_nodes.append(Node(id=tech_id, type="TECHNOLOGY", name=t_clean, properties={"tech_name": t_key, "category": cat}))
            seen_ids.add(tech_id)
        linked = False
        for c_k in aff:
            if c_k in comp_ids:
                k = (comp_ids[c_k], "USES", tech_id)
                if k not in seen_rel_keys:
                    new_rels.append(Relationship(source=k[0], type="USES", target=tech_id))
                    seen_rel_keys.add(k)
                linked = True
        if not linked:
            k = (system_id, "USES", tech_id)
            if k not in seen_rel_keys:
                new_rels.append(Relationship(source=k[0], type="USES", target=tech_id))
                seen_rel_keys.add(k)

    return ArtifactGraph(project_id=project_id, nodes=new_nodes, relationships=new_rels)


def architecture(graph: ArtifactGraph) -> ArchitectureView:
    """
    Extract the architectural subgraph (SYSTEM, COMPONENT, SERVICE, TECHNOLOGY)
    and all interconnecting relationships with architectural aggregate statistics.
    """
    graph = ensure_architecture(graph)
    nodes = [node for node in graph.nodes if node.type in ARCH_TYPES]
    node_ids = {node.id for node in nodes}
    relationships = [
        edge for edge in graph.relationships
        if edge.source in node_ids and edge.target in node_ids
    ]

    stats = ArchitectureStats(
        total_systems=sum(1 for n in nodes if n.type == "SYSTEM"),
        total_components=sum(1 for n in nodes if n.type == "COMPONENT"),
        total_services=sum(1 for n in nodes if n.type == "SERVICE"),
        total_technologies=sum(1 for n in nodes if n.type == "TECHNOLOGY"),
        total_communications=sum(1 for r in relationships if r.type == "COMMUNICATES_WITH"),
    )

    return ArchitectureView(
        project_id=graph.project_id,
        nodes=nodes,
        relationships=relationships,
        stats=stats,
    )


def components(graph: ArtifactGraph) -> list[ComponentSummary]:
    """
    Return all COMPONENT nodes with their categories, folders, used technologies,
    exposed endpoints/services, and contained file/service counts.
    """
    graph = ensure_architecture(graph)
    node_map = {n.id: n for n in graph.nodes}
    comp_nodes = [n for n in graph.nodes if n.type == "COMPONENT"]

    summaries = []
    for comp in comp_nodes:
        # Outgoing USES -> TECHNOLOGY
        techs = [
            node_map[r.target].name for r in graph.relationships
            if r.source == comp.id and r.type == "USES"
            and r.target in node_map and node_map[r.target].type == "TECHNOLOGY"
        ]

        # Outgoing EXPOSES -> SERVICE / COMPONENT
        exposes = [
            node_map[r.target].name for r in graph.relationships
            if r.source == comp.id and r.type == "EXPOSES" and r.target in node_map
        ]

        # Count contained services and code files
        service_count = sum(
            1 for r in graph.relationships
            if (r.source == comp.id and r.type == "CONTAINS" and node_map.get(r.target) and node_map[r.target].type == "SERVICE")
            or (r.target == comp.id and r.type == "PART_OF" and node_map.get(r.source) and node_map[r.source].type == "SERVICE")
        )
        file_count = sum(
            1 for r in graph.relationships
            if (r.source == comp.id and r.type == "CONTAINS" and node_map.get(r.target) and node_map[r.target].type in CODE_TYPES)
            or (r.target == comp.id and r.type == "PART_OF" and node_map.get(r.source) and node_map[r.source].type in CODE_TYPES)
        )

        category = str(comp.properties.get("category", "component"))
        folder = comp.properties.get("folder") or comp.properties.get("path")

        summaries.append(
            ComponentSummary(
                id=comp.id,
                name=comp.name,
                category=category,
                folder=str(folder) if folder else None,
                technologies=sorted(list(set(techs))),
                exposes=sorted(list(set(exposes))),
                service_count=service_count,
                file_count=file_count,
            )
        )

    return sorted(summaries, key=lambda c: (c.category, c.name))


def component_dependencies(graph: ArtifactGraph, component_id: str) -> ComponentDependencyView:
    """
    Return the focused dependency graph for a single component:
      - Calls (outgoing COMMUNICATES_WITH / CALLS)
      - Called by (incoming COMMUNICATES_WITH / CALLS)
      - Uses (outgoing USES -> TECHNOLOGY)
      - Exposes (outgoing EXPOSES)
    """
    graph = ensure_architecture(graph)
    comp = find_node(graph, component_id)
    if comp.type != "COMPONENT":
        raise AppError(422, "not_a_component", "Select a COMPONENT node.")

    node_map = {n.id: n for n in graph.nodes}

    calls = []
    called_by = []
    uses = []
    exposes = []

    for r in graph.relationships:
        if r.source == component_id and r.type in ("COMMUNICATES_WITH", "CALLS"):
            if r.target in node_map and node_map[r.target] not in calls:
                calls.append(node_map[r.target])
        elif r.target == component_id and r.type in ("COMMUNICATES_WITH", "CALLS"):
            if r.source in node_map and node_map[r.source] not in called_by:
                called_by.append(node_map[r.source])
        elif r.source == component_id and r.type == "USES":
            if r.target in node_map and node_map[r.target] not in uses:
                uses.append(node_map[r.target])
        elif r.source == component_id and r.type == "EXPOSES":
            if r.target in node_map and node_map[r.target] not in exposes:
                exposes.append(node_map[r.target])

    return ComponentDependencyView(
        component=comp,
        calls=calls,
        called_by=called_by,
        uses=uses,
        exposes=exposes,
    )


def tech_stack(graph: ArtifactGraph) -> TechStackView:
    """
    Return all TECHNOLOGY nodes grouped by category, with list of components using each.
    """
    graph = ensure_architecture(graph)
    node_map = {n.id: n for n in graph.nodes}
    tech_nodes = [n for n in graph.nodes if n.type == "TECHNOLOGY"]

    all_items: list[TechItem] = []
    by_category: dict[str, list[TechItem]] = {}

    for tech in tech_nodes:
        used_by = [
            node_map[r.source].name for r in graph.relationships
            if r.target == tech.id and r.type == "USES"
            and r.source in node_map and node_map[r.source].type == "COMPONENT"
        ]

        item = TechItem(
            id=tech.id,
            name=tech.name,
            tech_name=str(tech.properties.get("tech_name", tech.name.lower())),
            category=str(tech.properties.get("category", "other")),
            used_by_components=sorted(list(set(used_by))),
        )
        all_items.append(item)
        by_category.setdefault(item.category, []).append(item)

    all_items.sort(key=lambda t: (t.category, t.name))
    for cat in by_category:
        by_category[cat].sort(key=lambda t: t.name)

    return TechStackView(
        project_id=graph.project_id,
        all=all_items,
        by_category=by_category,
    )

