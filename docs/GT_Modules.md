# **Member 1 — Artifact Intelligence**

**Main responsibility:** Make GraphTrace AI understand the different software artifacts.

### **Modules / Work**

1. **Requirement Intelligence**
   - SRS/PDF parsing
   - Requirement extraction
   - Functional/non-functional requirements
   - Actors and use cases
   - Requirement metadata
   - Requirement identification
2. **Architecture Intelligence**
   - README analysis
   - Folder/project structure analysis
   - Configuration-file analysis
   - Identify components/services
   - Identify technologies
   - Identify component relationships
   - Generate structured architecture information
3. **Code Intelligence**
   - Tree-sitter integration
   - AST generation
   - File/package extraction
   - Class/interface extraction
   - Method/function extraction
   - Import relationships
   - Function-call relationships
   - Inheritance relationships
   - Code dependencies
4. **Test Intelligence**
   - Test-file detection
   - Test-case extraction
   - Test-method extraction
   - Test → class/method mapping
   - Test metadata extraction
5. **Documentation Intelligence**
   - README/Markdown parsing
   - API documentation parsing
   - Documentation section extraction
   - Documentation → code identification
6. **Common Artifact Output**
   - Define common JSON/data format
   - Normalize extracted information
   - Send structured artifact information to Member 2

**Final responsibility:**

**Raw Project → Structured Software Knowledge**

# **Member 2 — Knowledge Graph Engine**

**Main responsibility:** Turn Member 1's extracted information into the **Software Knowledge Graph**.

### **Modules / Work**

1. **Graph Schema Design**
   - Define node types
   - Define node properties
   - Define relationship types
   - Define graph rules
2. **Neo4j Integration**
   - Neo4j setup
   - Database configuration
   - Graph database APIs
   - CRUD operations
3. **Node Creation**
   - Requirement nodes
   - Architecture/component nodes
   - Module nodes
   - Class nodes
   - Method nodes
   - API nodes
   - Test nodes
   - Documentation nodes
   - Technology nodes
4. **Relationship Creation**

```
IMPLEMENTS
CALLS
IMPORTS
DEPENDS_ON
CONTAINS
TESTED_BY
DOCUMENTED_BY
USES
PART_OF
```

- - etc.

1. **Entity Resolution**
   - Identify when two extracted entities refer to the same thing
   - Avoid duplicate nodes
   - Resolve relationships between different artifact types
2. **Graph Updating**
   - Detect changed artifacts
   - Update affected nodes
   - Add/remove relationships
   - Keep graph synchronized with project changes
3. **Graph Query API**
   - Find dependencies
   - Find relationships
   - Find paths
   - Find connected artifacts
   - Provide graph data to Member 3

**Final responsibility:**

**Structured Software Knowledge → Connected Software Knowledge Graph**

# **Member 3 — Intelligence & Reasoning Engine**

**Main responsibility:** Make the Knowledge Graph intelligent and useful for developers.

### **Modules / Work**

1. **Graph Query Engine**
   - Convert user requests into graph queries
   - Cypher queries
   - Graph traversal
   - Path finding
2. **Semantic Search**
   - Embedding generation
   - Vector database
   - Semantic retrieval
   - Combine semantic results with graph results
3. **GraphRAG**
   - Graph-based retrieval
   - Relevant-node retrieval
   - Relevant-document/code retrieval
   - Context construction
4. **Requirement Traceability**
   - Requirement → Architecture
   - Requirement → Module
   - Requirement → Code
   - Requirement → Test
   - Requirement → Documentation
5. **Dependency Analysis**
   - Component dependencies
   - Class dependencies
   - Method dependencies
   - Dependency chains
   - Upstream/downstream analysis
6. **Change Impact Analysis**
   - Identify changed entity
   - Traverse dependent nodes
   - Identify potentially affected components
   - Identify affected APIs
   - Identify affected tests
   - Identify affected documentation
   - Impact/risk calculation
7. **LLM Integration**
   - Send retrieved graph context to LLM
   - Generate natural-language explanations
   - Explain graph traversal/reasoning
   - Keep responses grounded in retrieved project information
8. **Intelligence APIs**
   - Search API
   - Traceability API
   - Dependency API
   - Impact-analysis API
   - Explanation API

**Final responsibility:**

**Knowledge Graph → Analysis, Reasoning & Explainable Intelligence**

# **Member 4 — Frontend & Visualization**

**Main responsibility:** Turn everything into an actual usable GraphTrace AI product.

### **Modules / Work**

1. **Application/UI Foundation**
   - React/Next.js setup
   - Routing
   - Component system
   - Application layout
   - API integration
2. **Project Management UI**
   - Create project
   - Upload ZIP
   - Repository connection
   - Project selection
   - Analysis status/progress
3. **Dashboard**
   - Project overview
   - Requirements count
   - Classes/modules
   - Tests
   - APIs
   - Documentation
   - Graph statistics
4. **Knowledge Graph Visualization**
   - Interactive graph
   - Node/relationship visualization
   - Node selection
   - Relationship exploration
   - Filtering/searching
5. **Architecture Visualization**
   - Component view
   - Service relationships
   - Architecture diagram
   - Component details
6. **Requirement Traceability UI**
   - Select requirement
   - Show implementation path
   - Requirement → Code → Test → Documentation
7. **Dependency Explorer**
   - Select component/class
   - Show upstream/downstream dependencies
   - Interactive dependency graph
8. **Test Intelligence UI**
   - Test-to-code mapping
   - Related tests
   - Test impact visualization
9. **Documentation View**
   - Related documentation
   - API documentation
   - Code ↔ documentation relationships
10. **Chat Interface**

- Developer question interface
- Display GraphTrace responses
- Show supporting graph path/context

1. **Change Impact Dashboard**

- Changed component/requirement
- Affected components
- Affected APIs
- Affected tests
- Affected documentation
- Impact visualization
- Risk/impact summary

1. **Explainability UI**

- Show _why_ something was identified
- Display graph traversal/path
- Link answer → actual project entities

1. **Final Product Integration**

- Connect all backend APIs
- Error handling
- Loading states
- Performance optimization
- Final UI polish

**Final responsibility:**

**GraphTrace Intelligence → Usable Developer Product**

# **The Phase Structure**

## **Phase 1 — Basic Software Understanding**

### **Goal**

Take a small repository and turn it into a basic graph that can be explored.

This is your example.

| **Member** | **Work**                                       |
| ---------- | ---------------------------------------------- |
| **M1**     | Basic README + source-code parser              |
| ---        | ---                                            |
| **M2**     | Basic Neo4j schema + graph builder             |
| ---        | ---                                            |
| **M3**     | Basic Cypher queries + dependency/path queries |
| ---        | ---                                            |
| **M4**     | Basic dashboard + graph visualization          |
| ---        | ---                                            |

### **Pipeline**

Repository

↓

M1: Parse README + Code

↓

Structured JSON

↓

M2: Create Neo4j Nodes + Relationships

↓

Knowledge Graph

↓

M3: Query Graph

↓

M4: Display Graph

### **End result**

You upload:

project.zip

and get:

Project

├── src

│ ├── UserService

│ ├── AuthService

│ └── UserRepository

│

├── README

└── dependencies

with actual relationships visible in Neo4j/UI.

### **Phase gate**

**"Can we upload a project and visually explore its software structure?"**

If yes → Phase 2.

# **Phase 2 — Real Code Intelligence**

Now don't jump to requirements yet.

Make the **code side actually useful**.

### **M1 — Code Intelligence v2**

Expand the parser:

Files

Packages

Classes

Interfaces

Methods

Functions

Imports

Function Calls

Inheritance

Dependencies

Use Tree-sitter/static analysis.

### **M2 — Graph v2**

Expand the graph schema:

FILE

PACKAGE

CLASS

INTERFACE

METHOD

FUNCTION

Relationships:

CONTAINS

IMPORTS

CALLS

EXTENDS

IMPLEMENTS

DEPENDS_ON

M2 also handles entity IDs and duplicate entities.

### **M3 — Dependency Intelligence**

Now M3 can actually reason over the graph:

What depends on UserService?

UserController

↓

UserService

↓

UserRepository

Queries:

- What calls this class?
- What does this method call?
- What depends on this module?
- What is upstream?
- What is downstream?
- Find path between A and B.

### **M4 — Dependency Explorer**

UI becomes:

Select Class

↓

Dependencies

↓

Interactive Graph

Add:

- search
- node selection
- relationship filters
- class/method details
- dependency view

### **Phase gate**

**"Can GraphTrace explain the dependency structure of an unfamiliar codebase?"**

# **Phase 3 — Requirement Intelligence**

Now introduce the **SRS**.

This is where GraphTrace starts becoming different from a normal code-analysis tool.

Your project specifically targets end-to-end traceability from requirements through implementation, tests and documentation.

### **M1**

Build SRS parser:

SRS

↓

Requirements

↓

Functional Requirements

Non-functional Requirements

Actors

Use Cases

Requirement IDs

Descriptions

Output:

{

"id": "REQ-001",

"type": "functional",

"description": "User shall be able to login"

}

### **M2**

Add:

Requirement

nodes.

Then establish:

Requirement

↓

?

↓

Code

Initially this mapping can be manually/semi-automatically established.

Later you automate it.

### **M3**

Build:

# **Requirement Traceability Engine**

Example:

REQ-001 Login

↓

AuthController

↓

AuthService

↓

JWTService

↓

UserRepository

Queries:

- Which code implements this requirement?
- Which requirements are implemented by this class?
- Is this requirement implemented?
- Show the complete requirement → code path.

### **M4**

Build:

# **Requirement Traceability UI**

User clicks:

**REQ-001 — User Login**

and sees:

Requirement

↓

Architecture

↓

Component

↓

Class

↓

Method

### **Phase gate**

**"Can we trace a requirement into the actual implementation?"**

# **Phase 4 — Architecture Intelligence**

Now you have:

Requirements

↓

Code

↓

Dependencies

Next you add the architectural layer between them.

### **M1**

Architecture extraction:

README

Folder Structure

Config Files

Package Structure

Frameworks

Services

Components

APIs

Identify:

Frontend

Backend

Database

Authentication Service

API Layer

Business Layer

etc.

### **M2**

Add architecture nodes:

SYSTEM

COMPONENT

SERVICE

MODULE

API

DATABASE

TECHNOLOGY

Relationships:

PART_OF

USES

DEPENDS_ON

COMMUNICATES_WITH

EXPOSES

Now you can connect:

Requirement

↓

Component

↓

Module

↓

Class

↓

Method

### **M3**

Architecture reasoning:

What components does Authentication depend on?

Which APIs belong to Payment Service?

What modules communicate with Database?

What happens if AuthService fails?

### **M4**

Architecture visualization:

┌──────────────┐

│ Frontend │

└──────┬───────┘

↓

┌──────────────┐

│ API Gateway │

└──────┬───────┘

↓

┌──────────────┐

│ Auth Service │

└──────┬───────┘

↓

┌──────────────┐

│ Database │

└──────────────┘

And importantly, architecture components should be clickable → revealing the underlying graph.

### **Phase gate**

**"Can GraphTrace understand the architecture and connect it to the actual code?"**

# **Phase 5 — Test Intelligence**

Now you have enough graph structure to add tests.

### **M1**

Parse:

JUnit

PyTest

Jest

etc.

depending on languages/frameworks you support.

Extract:

Test File

Test Class

Test Method

Assertions

Referenced Class/Method

### **M2**

Add:

TEST

TEST_CASE

and relationships:

TESTS

TESTED_BY

Example:

AuthService

↑

│ TESTED_BY

│

LoginTest

### **M3**

Build test reasoning:

Which tests cover AuthService?

Which tests are affected if UserService changes?

Which requirements have tests?

Which code has no mapped tests?

### **M4**

Build:

# **Test Intelligence UI**

For every requirement:

Requirement

↓

Code

↓

Tests

So:

REQ-001

↓

AuthService

↓

LoginTest

↓

PASSED

### **Phase gate**

**"Can GraphTrace connect requirements → implementation → tests?"**

# **Phase 6 — Documentation Intelligence**

Now add documentation.

This is where the graph becomes a proper **software lifecycle knowledge graph** rather than just a code graph.

### **M1**

Parse:

README

Markdown

API Documentation

Comments

Configuration Documentation

Extract:

Document

Section

API

Usage

Configuration

Description

### **M2**

Add:

DOCUMENT

SECTION

API_DOCUMENTATION

Relationships:

DOCUMENTED_BY

DESCRIBES

REFERENCES

Example:

AuthService

↓

DOCUMENTED_BY

↓

Authentication.md

### **M3**

Documentation intelligence:

Which documentation describes this API?

What documentation is related to this class?

Which APIs are undocumented?

Which documentation references changed components?

### **M4**

Documentation UI:

Class → Documentation

API → Documentation

Requirement → Documentation

Plus document search.

### **Phase gate**

**"Can GraphTrace trace software knowledge across requirements, architecture, code, tests and documentation?"**

At this point your graph is becoming the central product.

# **Phase 7 — GraphRAG + LLM**

**Only now** I'd introduce the serious LLM layer.

This is important because your own project definition says the **Knowledge Graph is the primary project knowledge base**, while the LLM mainly explains retrieved graph information.

## **M1 — Improve Artifact Context**

M1 helps prepare:

Requirement chunks

Code metadata

Documentation chunks

Architecture descriptions

Test descriptions

and metadata.

## **M2 — Retrieval Infrastructure**

M2 handles:

Neo4j retrieval

Graph traversal

Vector storage

Embeddings

Entity linking

## **M3 — GraphRAG Engine**

This is the major M3 milestone.

Pipeline:

User Question

↓

Intent

↓

Graph Query

↓

Relevant Nodes

↓

Graph Traversal

↓

Relevant Documents/Code

↓

Context

↓

LLM

↓

Explanation

## **M4 — Chat + Explainability**

User asks:

Where is authentication implemented?

GraphTrace shows:

Answer

Authentication is implemented through:

AuthController

↓

AuthService

↓

JWTService

↓

UserRepository

And alongside the answer:

**\[View Graph Path\]**

This is the important distinction from a generic chatbot.

### **Phase gate**

**"Can a user ask a natural-language question and receive an answer grounded in the project's graph?"**

# **Phase 8 — Change Impact Analysis**

This should be the **final major intelligence module**.

Because now you have:

Requirements

↓

Architecture

↓

Components

↓

Code

↓

Tests

↓

Documentation

So change impact becomes a graph traversal problem.

## **M1 — Change Detection**

Detect:

Changed file

Changed class

Changed method

Changed API

Changed requirement

Input could initially be:

User selects:

AuthService.login()

or later:

Git commit

## **M2 — Impact Graph**

Traverse:

Changed Method

↓

CALLS

↓

Dependent Methods

↓

Classes

↓

Components

↓

APIs

↓

Tests

↓

Documentation

## **M3 — Impact Reasoning**

Produce:

CHANGE

↓

DIRECT IMPACT

↓

INDIRECT IMPACT

↓

AFFECTED TESTS

↓

AFFECTED DOCUMENTATION

↓

AFFECTED REQUIREMENTS

And eventually:

Impact Score

Risk Level

Reason

Affected Artifacts

## **M4 — Impact Dashboard**

This becomes one of your biggest demo features.

User selects:

Change AuthService.login()

GraphTrace:

AuthService.login()

│

┌────────────────┼────────────────┐

↓ ↓ ↓

AuthController LoginTest Authentication.md

│

↓

Login API

│

↓

Frontend Login

Dashboard:

CHANGE IMPACT

Direct Impact 3

Indirect Impact 7

Affected Tests 4

Affected APIs 2

Affected Docs 3

Risk: HIGH

And then:

Why?

The graph path explains it.

# **So the Overall Development Looks Like This**

This is the structure I'd actually give your team:

PHASE 1

Basic Repository Understanding

│

├── M1 → Basic Parser

├── M2 → Basic Graph

├── M3 → Basic Queries

└── M4 → Basic Dashboard

↓

PHASE 2

Code Intelligence

│

├── M1 → AST / Code Analysis

├── M2 → Code Graph

├── M3 → Dependency Analysis

└── M4 → Dependency Explorer

↓

PHASE 3

Requirement Intelligence

│

├── M1 → SRS Parser

├── M2 → Requirement Graph

├── M3 → Traceability Engine

└── M4 → Traceability UI

↓

PHASE 4

Architecture Intelligence

│

├── M1 → Architecture Extraction

├── M2 → Architecture Graph

├── M3 → Architecture Reasoning

└── M4 → Architecture Visualization

↓

PHASE 5

Test Intelligence

│

├── M1 → Test Parser

├── M2 → Test Graph

├── M3 → Test Analysis

└── M4 → Test UI

↓

PHASE 6

Documentation Intelligence

│

├── M1 → Documentation Parser

├── M2 → Documentation Graph

├── M3 → Documentation Analysis

└── M4 → Documentation UI

↓

PHASE 7

GraphRAG + LLM

│

├── M1 → Context Preparation

├── M2 → Retrieval Infrastructure

├── M3 → GraphRAG + LLM

└── M4 → Chat + Explainability

↓

PHASE 8

Change Impact Analysis

│

├── M1 → Change Detection

├── M2 → Impact Traversal

├── M3 → Impact Reasoning

└── M4 → Impact Dashboard

↓

GRAPH TRACE AI

**Tech Stack**

| **Layer**                         | **Technology**                                | **Purpose**                                      |
| --------------------------------- | --------------------------------------------- | ------------------------------------------------ |
| **Frontend**                      | React / Next.js                               | Web application and dashboard                    |
| ---                               | ---                                           | ---                                              |
| **UI**                            | Tailwind CSS                                  | Interface styling                                |
| ---                               | ---                                           | ---                                              |
| **Graph Visualization**           | React Flow / Cytoscape.js                     | Interactive software knowledge graph             |
| ---                               | ---                                           | ---                                              |
| **Backend**                       | Python + FastAPI                              | REST APIs and backend services                   |
| ---                               | ---                                           | ---                                              |
| **Programming Language Analysis** | Tree-sitter                                   | AST parsing and source-code analysis             |
| ---                               | ---                                           | ---                                              |
| **Document Parsing**              | PyMuPDF / PDF parser                          | SRS and PDF extraction                           |
| ---                               | ---                                           | ---                                              |
| **Code Analysis**                 | Tree-sitter + custom static analysis          | Classes, methods, imports, calls, dependencies   |
| ---                               | ---                                           | ---                                              |
| **Knowledge Graph**               | Neo4j                                         | Central Software Knowledge Graph                 |
| ---                               | ---                                           | ---                                              |
| **Graph Query**                   | Cypher                                        | Graph traversal and relationship queries         |
| ---                               | ---                                           | ---                                              |
| **Vector Search**                 | FAISS / Chroma                                | Semantic retrieval and embeddings                |
| ---                               | ---                                           | ---                                              |
| **Embeddings**                    | Sentence Transformers                         | Convert requirements/code/docs into vectors      |
| ---                               | ---                                           | ---                                              |
| **GraphRAG**                      | Custom GraphRAG pipeline                      | Combine graph relationships + semantic retrieval |
| ---                               | ---                                           | ---                                              |
| **LLM**                           | Llama 3 / compatible LLM<br><br>Open ai api ( | Natural-language interpretation and explanation  |
| ---                               | ---                                           | ---                                              |
| **LLM Framework**                 | LangChain / LlamaIndex                        | LLM, retrieval and agent orchestration           |
| ---                               | ---                                           | ---                                              |
| **Version Control**               | Git / GitHub                                  | Repository ingestion and change detection        |
| ---                               | ---                                           | ---                                              |
| **Data Format**                   | JSON                                          | Communication between artifact modules           |
| ---                               | ---                                           | ---                                              |
| **Database/API Layer**            | FastAPI + Neo4j driver                        | Backend ↔ graph communication                    |
| ---                               | ---                                           | ---                                              |
| **Containerization**              | Docker                                        | Reproducible deployment                          |
| ---                               | ---                                           | ---                                              |
| **Testing**                       | PyTest + appropriate language test frameworks | Backend and parser testing                       |
| ---                               | ---                                           | ---                                              |