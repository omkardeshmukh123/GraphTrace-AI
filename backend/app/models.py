"""The versioned contract shared with artifact extraction and the frontend."""

from typing import Annotated, Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")]
NodeType = Literal[
    "PROJECT", "FILE", "PACKAGE", "MODULE", "CLASS", "INTERFACE",
    "METHOD", "FUNCTION", "REQUIREMENT", "DOCUMENT", "TECHNOLOGY",
]
RelationshipType = Literal[
    "CONTAINS", "IMPORTS", "CALLS", "EXTENDS", "IMPLEMENTS",
    "DEPENDS_ON", "IMPLEMENTED_BY", "DOCUMENTED_BY", "USES", "PART_OF",
]
DEPENDENCY_TYPES = {"IMPORTS", "CALLS", "EXTENDS", "IMPLEMENTS", "DEPENDS_ON", "USES"}
CODE_TYPES = {"FILE", "PACKAGE", "MODULE", "CLASS", "INTERFACE", "METHOD", "FUNCTION"}


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Node(Contract):
    id: Identifier
    type: NodeType
    name: str = Field(min_length=1, max_length=500)
    properties: dict[str, JsonValue] = Field(default_factory=dict)


class Relationship(Contract):
    source: Identifier
    target: Identifier
    type: RelationshipType
    properties: dict[str, JsonValue] = Field(default_factory=dict)


class ArtifactGraph(Contract):
    schema_version: Literal["1.0"] = "1.0"
    project_id: Identifier
    nodes: list[Node] = Field(min_length=1, max_length=5000)
    relationships: list[Relationship] = Field(default_factory=list, max_length=20000)

    @model_validator(mode="after")
    def validate_graph(self):
        nodes = {node.id: node for node in self.nodes}
        if len(nodes) != len(self.nodes):
            raise ValueError("Node IDs must be unique within a project")
        projects = [node for node in self.nodes if node.type == "PROJECT"]
        if len(projects) != 1 or projects[0].id != self.project_id:
            raise ValueError("Exactly one PROJECT node must have id equal to project_id")
        seen = set()
        for edge in self.relationships:
            if edge.source not in nodes or edge.target not in nodes:
                raise ValueError("All relationship endpoints must exist in the same graph")
            key = (edge.source, edge.type, edge.target)
            if key in seen:
                raise ValueError("Duplicate relationships are not allowed")
            seen.add(key)
            if edge.type == "IMPLEMENTED_BY" and (
                nodes[edge.source].type != "REQUIREMENT" or nodes[edge.target].type not in CODE_TYPES
            ):
                raise ValueError("IMPLEMENTED_BY must point from a REQUIREMENT to code")
        return self


class ManualMapping(Contract):
    requirement: str = Field(min_length=1, max_length=1000)
    implementation: str = Field(min_length=1, max_length=1000)


class ProjectSummary(Contract):
    id: Identifier
    name: str
    node_count: int
    relationship_count: int
    counts: dict[str, int]
    status: Literal["ready"] = "ready"
    source: str


class GraphView(Contract):
    project_id: Identifier
    nodes: list[Node]
    relationships: list[Relationship]


class DependencyView(GraphView):
    root: Identifier
    direction: Literal["upstream", "downstream"]
    distances: dict[str, int]
    depth_limited: bool


class PathView(Contract):
    project_id: Identifier
    found: bool
    node_ids: list[str]
    relationships: list[Relationship]
    max_depth: int
    directed: bool


class RequirementSummary(Contract):
    requirement: Node
    mapping_status: Literal["mapped", "unmapped"]
    implementation_count: int


class TraceabilityView(GraphView):
    requirement: Node
    mapping_status: Literal["mapped", "unmapped"]
    implementation_ids: list[str]
    evidence_paths: list[list[str]]
    depth_limited: bool
    note: str = "Mappings identify linked code; they do not verify requirement correctness."


def make_node_id(project_id: str, node_type: str, reference: str) -> str:
    """reference: POSIX-relative path plus qualified symbol, e.g. auth.py::Auth.login."""
    return uuid5(NAMESPACE_URL, f"graphtrace:{project_id}:{node_type}:{reference}").hex
