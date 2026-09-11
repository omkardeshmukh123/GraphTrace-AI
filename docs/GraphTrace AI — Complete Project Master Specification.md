# **GraphTrace AI — Complete Project Master Specification**

## **1\. Project Identity**

### **Project Name**

**GraphTrace AI**

### **Full Concept**

**An Explainable Software Engineering Intelligence Platform based on a Software Knowledge Graph.**

### **Primary Objective**

GraphTrace AI is designed to understand a software project as a **connected system**, rather than treating source code, requirements, architecture, tests, and documentation as isolated artifacts.

The system extracts information from these artifacts, converts the information into structured entities and relationships, and stores them in a unified **Software Knowledge Graph**.

The graph then becomes the persistent project knowledge layer used for:

- software understanding
- dependency analysis
- requirement traceability
- architecture understanding
- test mapping
- documentation analysis
- semantic search
- GraphRAG
- change-impact analysis
- explainable responses

The project document explicitly defines this multi-artifact approach rather than a source-code-only analyzer.

# **2\. The Core Problem**

Traditional software projects contain many different artifacts:

Requirements

│

├── SRS

│

Architecture

│

├── diagrams

├── components

└── services

│

Source Code

│

├── classes

├── methods

├── APIs

└── dependencies

│

Tests

│

Documentation

The problem is that these artifacts are generally disconnected.

For example:

Requirement R-12

?

↓

Which component implements it?

?

↓

Which classes implement that component?

?

↓

Which tests verify it?

?

↓

Which documentation describes it?

A developer often has to manually discover those relationships.

GraphTrace's fundamental idea is:

Instead of searching individual artifacts,

build relationships between them.

# **3\. Central Idea**

The central data structure is:

# **Software Knowledge Graph**

Conceptually:

Requirement

│

IMPLEMENTED_BY

↓

Component

│

CONTAINS

↓

Module

│

CONTAINS

↓

Class

↙ ↘

CALLS DEPENDS_ON

↓ ↓

Method Service

│

TESTED_BY

↓

Test

│

DOCUMENTED_BY

↓

Documentation

This graph is the **core of GraphTrace AI**.

The project source explicitly establishes that the Knowledge Graph, rather than the LLM, is the primary source of project knowledge.

# **4\. The Most Important Architectural Principle**

## **Knowledge Graph First**

This distinction is extremely important for your project presentation.

GraphTrace is **not**:

User

↓

LLM

↓

Answer

It is:

User

↓

Intent / Query

↓

Knowledge Graph

↓

Relevant project information

↓

Reasoning / Retrieval

↓

LLM

↓

Explanation

The LLM does not contain the project's authoritative knowledge.

The project knowledge exists in:

Software Knowledge Graph

The LLM can therefore be replaced by another compatible model without destroying the core knowledge system.

The source specifically states that the graph stores requirements, architecture, source code, tests, documentation, dependencies and workflows, while the LLM primarily explains retrieved information.

# **5\. High-Level Architecture**

GraphTrace consists of **four major layers**.

┌─────────────────────────────────────────────────────┐

│ GRAPH TRACE AI │

└─────────────────────────┬───────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ 1. ARTIFACT INTELLIGENCE LAYER │

│ │

│ Requirements │ Architecture │ Code │ Tests │ Docs │

└─────────────────────────┬───────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ 2. KNOWLEDGE GRAPH ENGINE │

│ │

│ Schema + Entity Resolution + Neo4j │

└─────────────────────────┬───────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ 3. INTELLIGENCE & REASONING ENGINE │

│ │

│ Graph Query │ GraphRAG │ Search │ Traceability │

│ Dependency Analysis │ Change Impact │ Explanation │

└─────────────────────────┬───────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ 4. EXPLAINABILITY & VISUALIZATION │

│ │

│ Dashboard │ Graph │ Architecture │ Chat │ Reports │

└─────────────────────────────────────────────────────┘

The four-layer architecture and responsibilities are directly established by the project source.

# **6\. Layer 1 — Artifact Intelligence**

This is where GraphTrace **understands raw software artifacts**.

It should not immediately throw everything into an LLM.

Instead:

Raw Artifact

↓

Parser / Analyzer

↓

Structured Information

↓

Normalized Entity + Relationship Data

↓

Knowledge Graph

There are five major artifact-intelligence modules.

# **7\. Requirement Intelligence**

## **Input**

Primarily:

- SRS
- requirement documents
- requirement descriptions
- use-case information

## **Extract**

Potential entities:

Requirement

Functional Requirement

Non-functional Requirement

Actor

Use Case

Business Rule

Constraint

Example:

REQ-001

"The system shall allow users to log in."

becomes:

{

"id": "REQ-001",

"type": "FUNCTIONAL_REQUIREMENT",

"description": "The system shall allow users to log in."

}

Then eventually:

REQ-001

↓

Authentication Component

↓

AuthController

↓

AuthService

↓

JWTService

### **Purpose**

Turn natural-language requirements into graph entities that can later be connected to implementation.

# **8\. Architecture Intelligence**

Architecture Intelligence determines the **high-level organization of the software**.

Potential inputs:

- README
- project structure
- folder hierarchy
- configuration
- dependency files
- source structure
- architecture documents

It identifies things such as:

System

Component

Service

Module

API

Database

Technology

Layer

Example:

E-commerce System

Frontend

Backend

├── Authentication Service

├── Payment Service

└── Order Service

Database

Graph:

Frontend

↓ COMMUNICATES_WITH

Backend

↓ CONTAINS

Authentication Service

↓ USES

Database

The project specifically includes automatic architecture understanding as a key feature.

# **9\. Code Intelligence**

This is one of the most technically important modules.

## **Technology**

**Tree-sitter** is the planned core parsing technology.

The code analyzer should extract things such as:

### **Structural entities**

Repository

File

Package

Folder

Class

Interface

Method

Function

Variable

API

### **Relationships**

IMPORTS

CALLS

EXTENDS

IMPLEMENTS

CONTAINS

DEPENDS_ON

Example:

AuthController

│

│ CALLS

↓

AuthService

│

│ CALLS

↓

JWTService

│

│ USES

↓

UserRepository

This produces the underlying code dependency graph.

# **10\. Test Intelligence**

Test Intelligence understands the testing side of the project.

Potential entities:

Test File

Test Class

Test Case

Assertion

Test Suite

Relationships:

TESTS

TESTED_BY

VALIDATES

Example:

LoginTest

↓ TESTS

AuthService.login()

This later allows GraphTrace to answer:

Which tests are affected if AuthService changes?

or:

Which requirements have corresponding tests?

The project explicitly identifies test coverage mapping as one of its core features.

# **11\. Documentation Intelligence**

Documentation Intelligence analyzes:

- README
- Markdown
- API documentation
- configuration documentation
- usage instructions
- technical documentation

Entities could include:

Document

Section

API Documentation

Configuration

Usage

Example

Relationships:

DOCUMENTED_BY

DESCRIBES

REFERENCES

Example:

AuthService

↓ DOCUMENTED_BY

Authentication.md

This becomes extremely important during change-impact analysis.

# **12\. Standard Output of Layer 1**

One of the most important architectural decisions should be a **common intermediate format**.

Every artifact parser should produce standardized information.

Conceptually:

{

"entities": \[

{

"id": "class:AuthService",

"type": "CLASS",

"name": "AuthService"

}

\],

"relationships": \[

{

"source": "class:AuthController",

"type": "CALLS",

"target": "class:AuthService"

}

\],

"metadata": {}

}

This creates a clean boundary:

M1's parser implementation

↓

Standard JSON

↓

M2 Graph

M2 should not care how M1 extracted the information.

# **13\. Layer 2 — Knowledge Graph Engine**

This is the **central storage and relationship layer**.

## **Database**

### **Neo4j**

Neo4j is the central Knowledge Graph database identified by the project.

# **14\. Graph Schema**

The exact final schema is still something your team should formally freeze during implementation.

A proposed conceptual schema is:

### **Artifact nodes**

Requirement

Architecture

Component

Module

Repository

Folder

File

Class

Interface

Method

Function

API

Test

Document

Technology

### **Relationships**

CONTAINS

PART_OF

IMPLEMENTS

CALLS

IMPORTS

DEPENDS_ON

EXTENDS

IMPLEMENTS

USES

TESTS

TESTED_BY

DOCUMENTED_BY

DESCRIBES

REFERENCES

COMMUNICATES_WITH

EXPOSES

Not every relationship needs to be implemented in the first prototype.

# **15\. Why Neo4j?**

A relational database might represent:

Classes table

Methods table

Requirements table

Tests table

but then relationship queries become increasingly dependent on joins.

The GraphTrace problem is inherently relational:

Requirement

→ Component

→ Module

→ Class

→ Method

→ Test

→ Documentation

Graph databases are naturally suited to traversing such relationships.

The graph allows queries such as:

Find all nodes connected to AuthService within depth 3.

or:

Requirement → Implementation → Test

# **16\. Entity Resolution**

This is an important M2 responsibility.

The same software entity can appear in multiple artifacts.

For example:

AuthService

may appear in:

- source code
- README
- architecture documentation
- tests
- API documentation

GraphTrace must avoid creating:

AuthService_1

AuthService_2

AuthService_3

AuthService_4

when they all refer to the same entity.

Instead:

AuthService

/ | \\

Code Test Docs

This is why entity IDs, canonical names and resolution rules matter.

# **17\. Graph Updating**

The graph should not necessarily be rebuilt from scratch every time.

Eventually:

Old Project

↓

Changed Files

↓

Re-analyze affected artifacts

↓

Update graph

This becomes particularly important for future change-impact functionality.

# **18\. Layer 3 — Intelligence & Reasoning Engine**

This is where GraphTrace starts doing more than storing data.

The intelligence layer consumes the graph and performs analysis.

Major components:

Graph Query Engine

Semantic Search

GraphRAG

Traceability

Dependency Analysis

Change Impact Analysis

LLM Explanation

# **19\. Graph Query Engine**

M3's first major responsibility.

User request:

What depends on AuthService?

becomes something conceptually equivalent to:

AuthService

↓

incoming DEPENDS_ON / CALLS relationships

↓

dependent entities

Possible operations:

find_entity()

find_dependencies()

find_dependents()

find_path()

find_related_nodes()

trace_requirement()

find_tests()

find_documentation()

# **20\. Dependency Analysis**

This operates primarily on the code/architecture graph.

Example:

OrderController

↓

OrderService

↓

PaymentService

↓

PaymentRepository

GraphTrace can determine:

### **Direct dependencies**

OrderService → PaymentService

### **Indirect dependencies**

OrderController

→ OrderService

→ PaymentService

→ PaymentRepository

This allows developers to understand unfamiliar systems.

# **21\. Requirement Traceability**

This is one of the flagship features.

The desired path is:

Requirement

↓

Architecture

↓

Component

↓

Module

↓

Class

↓

Method

↓

Test

↓

Documentation

Example:

REQ-001

User Login

↓

Authentication Component

↓

AuthController

↓

AuthService

↓

JWTService

↓

LoginTest

↓

Authentication.md

The project explicitly identifies **requirement-to-code traceability** as a core feature.

# **22\. Semantic Search**

Keyword search:

authentication

might only find exact occurrences.

Semantic search attempts to find conceptually relevant information.

For example:

How does the application verify users?

could retrieve:

AuthService

JWTService

TokenValidator

Authentication.md

Login requirement

This is where embeddings/vector retrieval can complement graph traversal.

Important distinction:

Vector Search

\= semantic similarity

Graph Search

\= relationship structure

GraphTrace can combine them.

# **23\. GraphRAG**

GraphRAG combines:

Knowledge Graph

-

Retrieval

-

LLM

Conceptually:

User Question

↓

Question Understanding

↓

Graph Retrieval

↓

Graph Traversal

↓

Relevant Project Context

↓

LLM

↓

Natural Language Explanation

The graph determines **what project information is relevant**.

The LLM turns that information into a readable answer.

# **24\. LLM's Role**

This needs to remain very clear during your viva.

### **The LLM is NOT:**

- the project database
- the authoritative source of project relationships
- the primary knowledge store

### **The LLM IS:**

- a natural-language interface
- an explanation layer
- an interpretation component
- potentially an intent-understanding component

For example:

User:

"If I change the authentication logic, what breaks?"

GraphTrace:

Authentication logic

↓

Graph traversal

↓

AuthService

↓

AuthController

↓

Login API

↓

LoginTest

↓

Authentication documentation

Then the LLM explains those results.

This architecture is explicitly supported by the project's source material.

# **25\. Layer 4 — Explainability & Visualization**

The fourth layer turns backend intelligence into an actual product.

Major UI components:

Dashboard

Project Upload

Knowledge Graph Viewer

Dependency Explorer

Architecture View

Requirement Traceability

Test Mapping

Documentation View

Chat

Impact Dashboard

# **26\. Dashboard**

The dashboard could display:

Project Overview

Requirements 42

Components 12

Classes 187

Methods 923

APIs 31

Tests 246

Documents 18

Graph Relationships 1,500+

These numbers are illustrative UI fields, not current project measurements.

# **27\. Knowledge Graph Viewer**

Interactive graph:

Requirement

│

↓

Component

│

↓

Class

↙ ↘

Method Test

│

↓

Documentation

Features:

- zoom
- pan
- search
- filtering
- node selection
- relationship inspection
- path highlighting

# **28\. Architecture View**

Instead of showing hundreds of classes:

Frontend

Backend

Database

Auth Service

Payment Service

Order Service

The architecture view provides a higher abstraction level.

Clicking:

Payment Service

could reveal:

PaymentService

PaymentController

PaymentRepository

Payment API

PaymentTest

Payment documentation

This creates drill-down:

System

↓

Architecture

↓

Component

↓

Module

↓

Class

↓

Method

# **29\. Chat Interface**

The chat interface is not simply a generic ChatGPT clone.

It should answer questions using project-grounded retrieval.

Example:

Where is authentication implemented?

Answer:

Authentication is implemented primarily through:

AuthController

↓

AuthService

↓

JWTService

↓

UserRepository

Then provide:

**View graph path**

This is the explainability aspect.

# **30\. Explainability**

A major differentiator.

Instead of:

"AuthService is important."

GraphTrace should show **why**.

Example:

AuthService

↑

called by AuthController

↑

used by Login API

↑

implements REQ-001

↑

tested by LoginTest

The user can inspect the actual graph path supporting the conclusion.

# **31\. Change Impact Analysis**

This is probably the most technically interesting final feature.

The concept:

Change

↓

Find changed entity

↓

Traverse graph

↓

Find affected entities

↓

Classify impact

↓

Calculate risk

↓

Explain

↓

Visualize

Example:

Change:

AuthService.login()

Graph:

AuthService.login()

│

┌────────────┼────────────┐

↓ ↓ ↓

AuthController LoginTest Auth Docs

│

↓

Login API

│

↓

Frontend

GraphTrace could report:

Direct Impact

Indirect Impact

Affected APIs

Affected Components

Affected Tests

Affected Documentation

Affected Requirements

Risk

The source identifies change-impact analysis as a major project feature.

# **32\. Complete Data Flow**

The entire system can be understood as this:

USER

│

↓

Upload Repository

│

↓

┌─────────────────────┐

│ Artifact Detection │

└──────────┬──────────┘

↓

┌───────────────┼────────────────┐

↓ ↓ ↓

SRS Source Docs

↓ ↓ ↓

Requirement Code Document

Parser Parser Parser

↓ ↓ ↓

└───────────────┼────────────────┘

↓

Structured Data

↓

Entity Resolution

↓

Knowledge Graph

(Neo4j)

↓

┌────────────┼────────────┐

↓ ↓ ↓

Query Traversal Semantic

Engine Search

└────────────┼────────────┘

↓

GraphRAG

↓

LLM

↓

Explanation

↓

Frontend / UI

# **33\. Technology Stack**

Based on the project direction we've established, the stack is:

## **Backend**

**Python**

Primary backend/analysis language.

**FastAPI**

Backend REST/API layer.

## **Code Analysis**

**Tree-sitter**

For source-code parsing and AST-level analysis.

## **Knowledge Graph**

**Neo4j**

Central Software Knowledge Graph.

**Cypher**

Graph querying language.

## **AI / Retrieval**

**GraphRAG**

Graph-grounded retrieval.

**Sentence Transformers**

Potential embedding technology for semantic search.

**FAISS / Chroma**

Potential vector retrieval layer.

**Llama 3 / compatible LLM**

Natural-language explanation.

**LangChain / LlamaIndex**

Potential orchestration/retrieval framework.

These latter choices should be treated as **implementation choices rather than irrevocably frozen architecture**, unless your team formally locks them.

## **Frontend**

**React / Next.js**

Web application.

**Tailwind CSS**

UI styling.

**React Flow / Cytoscape.js**

Graph visualization.

Again, the exact visualization library is an implementation decision that should be finalized before development.

## **Development**

Git

GitHub

Docker

PyTest

JSON

# **34\. Four-Team-Member Architecture**

Your four-person division fits the architecture extremely well.

## **Member 1 — Artifact Intelligence**

### **Responsibility**

**Understand the software artifacts.**

Modules:

Requirement Intelligence

Architecture Intelligence

Code Intelligence

Test Intelligence

Documentation Intelligence

Output:

Raw Project

↓

Structured Software Knowledge

## **Member 2 — Knowledge Graph**

### **Responsibility**

**Connect the extracted knowledge.**

Work:

Graph Schema

Neo4j

Nodes

Relationships

Entity Resolution

Graph Updates

Graph Query APIs

Output:

Structured Knowledge

↓

Software Knowledge Graph

## **Member 3 — Intelligence & Reasoning**

### **Responsibility**

**Reason over the graph.**

Work:

Graph Queries

Dependency Analysis

Traceability

Semantic Search

GraphRAG

LLM Integration

Change Impact

Output:

Knowledge Graph

↓

Intelligence

## **Member 4 — Frontend & Visualization**

### **Responsibility**

**Present the intelligence.**

Work:

Dashboard

Graph Viewer

Architecture View

Dependency Explorer

Traceability UI

Test UI

Documentation UI

Chat

Impact Dashboard

Explainability

Output:

Intelligence

↓

Developer Product

# **35\. Team Interaction**

This should be the fundamental development model:

M1

UNDERSTAND

↓

M2

CONNECT

↓

M3

REASON

↓

M4

PRESENT

Or:

M1 → JSON → M2 → Graph → M3 → API → M4 → UI

This gives you very clean interfaces between teammates.

# **36\. Phase-Based Development**

Since you've now decided **not to organize the project around months**, I recommend organizing it around functional phases.

## **Phase 1 — Basic Vertical Slice**

M1 → Basic parser

M2 → Basic graph

M3 → Basic querying

M4 → Basic dashboard + graph

Outcome:

Repository

↓

Code Analysis

↓

Neo4j

↓

Graph

↓

Basic UI

## **Phase 2 — Code Intelligence**

M1 → Tree-sitter / AST analysis

M2 → Code graph expansion

M3 → Dependency analysis

M4 → Dependency explorer

Outcome:

**Understand an unfamiliar codebase.**

## **Phase 3 — Requirements**

M1 → SRS parser

M2 → Requirement nodes + links

M3 → Traceability engine

M4 → Traceability UI

Outcome:

**Requirement → Code traceability.**

## **Phase 4 — Architecture**

M1 → Architecture extraction

M2 → Architecture graph

M3 → Architecture reasoning

M4 → Architecture visualization

Outcome:

**Requirement → Architecture → Code.**

## **Phase 5 — Tests**

M1 → Test parser

M2 → Test graph

M3 → Test analysis

M4 → Test visualization

Outcome:

**Requirement → Code → Test.**

## **Phase 6 — Documentation**

M1 → Documentation parser

M2 → Documentation graph

M3 → Documentation reasoning

M4 → Documentation UI

Outcome:

**Requirement → Code → Test → Documentation.**

## **Phase 7 — GraphRAG**

M1 → Context preparation

M2 → Retrieval infrastructure

M3 → GraphRAG + LLM

M4 → Chat + explainability

Outcome:

Natural-language questions grounded in project knowledge.

## **Phase 8 — Change Impact**

M1 → Change detection

M2 → Graph traversal

M3 → Impact reasoning

M4 → Impact dashboard

Outcome:

"What happens if I change this?"

becomes an actual GraphTrace capability.

# **37\. The Evolution of the Graph**

This is perhaps the best way to explain your entire project to a professor.

### **Initially:**

Code

↓

Code Graph

### **Then:**

Requirement

↘

Code Graph

↗

Architecture

### **Then:**

Requirement

↓

Architecture

↓

Code

↓

Tests

↓

Documentation

### **Finally:**

Requirement

│

Architecture

│

Code

↙ ↓ ↘

Tests APIs Docs

\\ │ /

Dependencies

│

↓

Change Impact

The graph becomes progressively richer.

# **38\. Main Features**

The project's documented feature set includes:

### **1\. Knowledge Graph Generation**

Convert project artifacts into connected graph entities.

### **2\. Requirement-to-Code Traceability**

Connect requirements to implementation.

### **3\. Architecture Understanding**

Automatically infer software architecture.

### **4\. Static Code Analysis**

Analyze source code structure and dependencies.

### **5\. Dependency Analysis**

Identify direct and indirect relationships.

### **6\. Test Coverage Mapping**

Connect implementation to tests.

### **7\. Documentation Analysis**

Connect software entities to documentation.

### **8\. Semantic Search**

Find conceptually relevant project information.

### **9\. GraphRAG**

Use graph structure for retrieval and grounded AI interaction.

### **10\. Change Impact Analysis**

Predict potentially affected artifacts.

### **11\. Explainable AI**

Show the graph evidence/path behind answers.

### **12\. Interactive Graph Visualization**

Allow developers to explore project relationships.

### **13\. Architecture Visualization**

Display higher-level system structure.

### **14\. Developer Chat**

Natural-language interaction with project knowledge.

These features are explicitly listed or implied in the project overview.

# **39\. Example: E-Commerce Project**

Suppose the analyzed project is:

E-Commerce Application

Requirement:

REQ-002:

User must be able to authenticate.

Architecture:

Frontend

↓

API

↓

Authentication Service

↓

User Database

Code:

LoginController

↓

AuthService

↓

JWTService

↓

UserRepository

Test:

LoginTest

Documentation:

Authentication.md

GraphTrace creates:

REQ-002

│

│ IMPLEMENTED_BY

↓

Authentication Service

│

↓

AuthService

│

├── CALLS → JWTService

│

├── TESTED_BY → LoginTest

│

└── DOCUMENTED_BY → Authentication.md

Now the graph isn't simply storing files.

It stores **software relationships**.

# **40\. Example Query**

User:

Where is authentication implemented?

GraphTrace:

REQ-002

↓

Authentication Service

↓

AuthService

↓

JWTService

↓

UserRepository

Then the LLM explains:

Authentication is handled primarily by AuthService, which invokes JWTService for token handling and interacts with UserRepository for user data.

The explanation is generated from retrieved graph/project context rather than relying solely on the model's generic knowledge.

# **41\. Example Change Impact**

User changes:

AuthService.login()

Graph traversal:

AuthService.login()

│

├── AuthController

│ ↓

│ Login API

│

├── LoginTest

│

├── Authentication.md

│

└── REQ-002

Potential report:

Changed Entity

AuthService.login()

Affected:

├── AuthController

├── Login API

├── LoginTest

├── Authentication.md

└── REQ-002

Risk:

High

The actual scoring methodology is **not yet formally defined** in the uploaded source and should therefore be treated as future implementation work rather than an already-established algorithm.

# **42\. Important Technical Algorithms**

The project will ultimately require several algorithmic components.

## **A. AST Extraction**

Source Code

↓

Tree-sitter

↓

AST

↓

Classes / Methods / Imports / Calls

## **B. Entity Resolution**

Extracted Entity

↓

Normalize name/path/identifier

↓

Search existing graph

↓

Match existing entity?

├── Yes → update

└── No → create

## **C. Graph Traversal**

Given:

Node A

find:

A → B → C → D

according to relationship types and traversal depth.

## **D. Requirement Traceability**

Requirement

↓

Candidate Component

↓

Candidate Module

↓

Candidate Code Entity

↓

Evidence / relationship

↓

Traceability path

The exact automated matching algorithm still needs to be formally specified.

## **E. Change Impact**

Conceptually:

Changed Node

↓

Reverse dependency traversal

↓

Direct dependents

↓

Indirect dependents

↓

Artifact classification

↓

Impact report

## **F. Semantic Retrieval**

Query

↓

Embedding

↓

Vector similarity

↓

Candidate project artifacts

↓

Graph expansion

↓

Context

# **43\. What Makes GraphTrace Different**

The strongest conceptual distinction is:

### **Generic AI assistant**

Question

↓

LLM

↓

Answer

### **GraphTrace**

Question

↓

Project Knowledge

↓

Graph Retrieval

↓

Graph Relationships

↓

Relevant Context

↓

LLM

↓

Explainable Answer

The project source explicitly frames GraphTrace as a persistent project knowledge base and says that any compatible LLM can be connected to it.

So your strongest claim should be:

**GraphTrace AI separates project knowledge from language generation.**

That's much stronger and more technically defensible than saying:

"Our AI knows the project."

# **44\. What GraphTrace Is NOT**

This is useful for your project scope.

GraphTrace is not primarily:

- a code generator
- an IDE replacement
- a generic chatbot
- a GitHub clone
- a project-management tool
- a simple static analyzer
- merely a visualization tool
- merely a RAG chatbot

Its central product is:

**A persistent, connected representation of software knowledge that enables traceability, analysis and explainable reasoning.**

# **45\. What Is Actually "AI" in GraphTrace?**

You should not present every component as AI.

### **Traditional / deterministic intelligence**

AST parsing

Dependency extraction

Graph construction

Graph traversal

Static analysis

Relationship detection

### **AI/ML components**

Semantic embeddings

Semantic retrieval

Natural-language intent interpretation

GraphRAG

LLM explanation

Potential intelligent requirement-code mapping

This makes your architecture more credible.

# **46\. What Should Be Deterministic?**

Where possible:

Class exists?

Method calls another method?

File imports package?

Test references class?

These should preferably be derived through static analysis rather than asking an LLM.

For example:

AuthController → CALLS → AuthService

should ideally come from code analysis.

Not:

LLM thinks AuthController probably calls AuthService.

This is a major design principle for reliability.

# **47\. What Can the LLM Handle?**

Good uses:

"What does this dependency chain mean?"

"Explain this architecture."

"Summarize this requirement."

"Why is this component affected?"

"Explain the impact report."

The graph provides the evidence.

The LLM explains it.

# **48\. Project Folder Architecture**

The exact folder structure is **not formally established in the uploaded handoff document**, so this should be treated as a recommended implementation structure rather than historical project fact.

A clean architecture would be:

graphtrace-ai/

│

├── backend/

│ │

│ ├── api/

│ │

│ ├── artifact_intelligence/

│ │ ├── requirements/

│ │ ├── architecture/

│ │ ├── code/

│ │ ├── tests/

│ │ └── documentation/

│ │

│ ├── knowledge_graph/

│ │ ├── schema/

│ │ ├── models/

│ │ ├── builders/

│ │ ├── resolver/

│ │ └── queries/

│ │

│ ├── intelligence/

│ │ ├── search/

│ │ ├── graph_rag/

│ │ ├── traceability/

│ │ ├── dependencies/

│ │ └── impact/

│ │

│ ├── llm/

│ │

│ └── main.py

│

├── frontend/

│ ├── components/

│ ├── pages/

│ ├── graph/

│ ├── dashboard/

│ ├── traceability/

│ ├── architecture/

│ ├── impact/

│ └── chat/

│

├── parsers/

│

├── tests/

│

├── docs/

│

├── docker/

│

└── README.md

Again: **this is a recommended structure, not something I would claim the uploaded source already finalized.**

# **49\. API Architecture**

The uploaded project material does not establish a finalized endpoint specification, so don't present the following as existing APIs.

A sensible eventual API design would be:

POST /projects

POST /projects/{id}/analyze

GET /projects/{id}

GET /projects/{id}/graph

GET /entities/{id}

GET /entities/{id}/dependencies

GET /entities/{id}/dependents

GET /requirements/{id}/trace

GET /requirements/{id}/tests

POST /search

POST /chat

POST /impact-analysis

GET /impact-analysis/{id}

These should be designed around **capabilities**, not individual database queries.

# **50\. Important Interface Contracts**

This is especially important for your four-member team.

## **M1 → M2**

Structured Artifact Data

Prefer:

{

"entities": \[\],

"relationships": \[\],

"metadata": {}

}

## **M2 → M3**

Expose graph operations rather than making M3 directly depend on Neo4j internals.

find_entity()

find_path()

get_dependencies()

get_dependents()

get_related_entities()

## **M3 → M4**

Expose clean APIs:

/search

/traceability

/dependencies

/impact

/explain

M4 shouldn't need to know whether M3 used:

Cypher

GraphRAG

embeddings

LLM

custom algorithms

# **51\. Current Development State**

Based strictly on the uploaded project materials plus the project decisions already established:

### **Conceptual architecture**

**Well defined.**

Artifact Intelligence

↓

Knowledge Graph

↓

Intelligence

↓

Visualization

### **Core product concept**

**Well defined.**

### **Knowledge Graph-first principle**

**Well defined.**

### **Major features**

**Defined.**

### **Team division**

**Defined conceptually.**

### **Phase-based roadmap**

**Defined conceptually.**

### **Exact graph schema**

**Needs implementation/finalization.**

### **Exact APIs**

**Needs implementation/finalization.**

### **Exact folder structure**

**Needs implementation/finalization.**

### **Exact impact scoring algorithm**

**Not formally defined yet.**

### **Production-grade parser coverage**

**Not established yet.**

### **Full GraphRAG implementation**

**Not established yet.**

### **Complete UI**

**Not established yet.**

# **52\. Biggest Technical Risks**

These aren't necessarily "bugs"; they're engineering risks you should actively design around.

## **1\. Parser accuracy**

Real repositories are messy.

Different languages/frameworks have different syntax and semantics.

## **2\. Cross-artifact linking**

This is probably one of the hardest parts.

How do you know:

REQ-12

corresponds to:

AuthService.login()

?

This requires evidence-based matching rather than blindly asking an LLM.

## **3\. Entity resolution**

The same concept can appear under slightly different names.

## **4\. Graph explosion**

Large projects could produce:

100k+ nodes

millions of relationships

So visualization and traversal need filtering and limits.

## **5\. False relationships**

A wrong graph edge can be more dangerous than a missing edge.

You need relationship provenance/confidence where appropriate.

## **6\. LLM hallucination**

Graph grounding can **reduce** hallucinations, but it doesn't mathematically guarantee zero hallucinations.

Your project's own material frames the benefit as improved consistency and reduced hallucination through graph grounding.

# **53\. Strongest Demonstration Flow**

For a final demonstration, I'd eventually make the whole product follow this sequence:

1\. Upload Project

↓

2\. Analyze Repository

↓

3\. Show Architecture

↓

4\. Show Knowledge Graph

↓

5\. Select Requirement

↓

6\. Show Requirement → Code

↓

7\. Show Code Dependencies

↓

8\. Show Related Tests

↓

9\. Show Documentation

↓

10\. Ask Chat Question

↓

11\. Show Graph-Grounded Answer

↓

12\. Change a Method

↓

13\. Run Impact Analysis

↓

14\. Show Affected Components

↓

15\. Show Affected Tests

↓

16\. Show Affected Documentation

↓

17\. Explain Why

That demonstrates virtually the entire architecture in one continuous story.

# **54\. The Project in One Sentence**

If your professor asks:

**"What exactly are you building?"**

Say:

**GraphTrace AI is a software engineering intelligence platform that converts requirements, architecture, source code, tests and documentation into a unified Software Knowledge Graph and uses graph-based analysis, retrieval and LLM-assisted explanation to provide traceability, dependency analysis, software understanding and change-impact analysis.**

# **55\. The Project in 30 Seconds**

If they ask for a shorter explanation:

**Existing AI coding assistants primarily operate around the code and the context supplied to them. GraphTrace AI builds a persistent knowledge representation of the entire software project. It extracts requirements, architecture, code, tests and documentation, connects them in a Neo4j Software Knowledge Graph, and then performs graph-based traceability, dependency analysis, semantic retrieval and change-impact analysis. An LLM sits on top of this system primarily to interpret and explain the graph-grounded results.**

# **56\. The Fundamental Mental Model**

The entire project can be remembered as:

GRAPH TRACE AI

RAW SOFTWARE

│

▼

┌───────────────┐

│ UNDERSTAND │ ← M1

│ artifacts │

└───────┬───────┘

│

▼

┌───────────────┐

│ CONNECT │ ← M2

│ knowledge │

└───────┬───────┘

│

▼

┌───────────────┐

│ REASON │ ← M3

│ over graph │

└───────┬───────┘

│

▼

┌───────────────┐

│ PRESENT │ ← M4

│ intelligence │

└───────────────┘

And the **software knowledge itself** evolves:

Requirements

│

▼

Architecture

│

▼

Code

↙ ↓ ↘

Tests APIs Docs

\\ │ /

Dependencies

│

▼

Change Impact

That is the actual backbone of GraphTrace.