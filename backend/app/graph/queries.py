"""Bounded graph traversals shared by the local and Neo4j adapters."""

from collections import deque

from backend.app.errors import AppError
from backend.app.models import (
    ArtifactGraph, DEPENDENCY_TYPES, DependencyView, GraphView, Node,
    PathView, Relationship, RequirementSummary, TraceabilityView,
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
