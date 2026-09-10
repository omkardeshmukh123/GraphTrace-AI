"""Contract tests for the read adapter. These do not require a live Neo4j server."""
import json

import pytest

from backend.app.config import Settings
from backend.app.errors import AppError
from backend.app.graph.store import Neo4jGraphStore
from scripts.make_demo import demo_graph


class FakeTransaction:
    def __init__(self, graph):
        self.graph = graph
        self.calls = []

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        assert parameters == {"project_id": "demo"}
        if "-[r]->" in query:
            assert "(a:Entity {project_id: $project_id})" in query
            assert "(b:Entity {project_id: $project_id})" in query
            values = self.graph.relationships
        else:
            values = self.graph.nodes
        records = []
        for value in values:
            record = value.model_dump()
            record["properties_json"] = json.dumps(record.pop("properties"))
            records.append(record)
        return records


class FakeSession:
    def __init__(self, tx):
        self.tx = tx

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute_read(self, operation):
        return operation(self.tx)


class FakeDriver:
    def __init__(self, tx):
        self.tx = tx

    def session(self, *, database):
        assert database == "neo4j"
        return FakeSession(self.tx)


def test_read_adapter_preserves_contract_and_scopes_endpoints():
    graph = demo_graph()
    tx = FakeTransaction(graph)
    store = object.__new__(Neo4jGraphStore)
    store.settings = Settings(_env_file=None)
    store.driver = FakeDriver(tx)
    assert store.get("demo") == graph
    assert len(tx.calls) == 2


def test_neo4j_write_handoff(monkeypatch):
    received = {}
    def writer(**kwargs):
        received.update(kwargs)
    monkeypatch.setattr("backend.app.graph.store.load_plugin", lambda *args: writer)
    store = object.__new__(Neo4jGraphStore)
    store.settings = Settings(_env_file=None)
    store.driver = object()
    graph = demo_graph()
    store.save(graph)
    assert received == {"graph": graph, "driver": store.driver, "database": "neo4j"}


def test_missing_writer_is_explicit():
    store = object.__new__(Neo4jGraphStore)
    store.settings = Settings(_env_file=None, graph_writer="")
    with pytest.raises(AppError) as error:
        store.check_writable()
    assert error.value.status == 503
