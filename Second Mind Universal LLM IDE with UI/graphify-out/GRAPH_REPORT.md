# Graph Report - wiki  (2026-04-16)

## Corpus Check
- Corpus is ~25,268 words - fits in a single context window. You may not need a graph.

## Summary
- 83 nodes · 159 edges · 8 communities detected
- Extraction: 49% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Vocera Product Ecosystem|Vocera Product Ecosystem]]
- [[_COMMUNITY_Wiki Structure & Stryker Core|Wiki Structure & Stryker Core]]
- [[_COMMUNITY_Condensed Intent NLP Pipeline|Condensed Intent NLP Pipeline]]
- [[_COMMUNITY_Smart Hospital Pillars & Spaces|Smart Hospital Pillars & Spaces]]
- [[_COMMUNITY_Product Image Entities|Product Image Entities]]
- [[_COMMUNITY_Platform Pillars & Virtual Care|Platform Pillars & Virtual Care]]
- [[_COMMUNITY_ProCuity & Engage Products|ProCuity & Engage Products]]
- [[_COMMUNITY_Operation Log|Operation Log]]

## God Nodes (most connected - your core abstractions)
1. `SmartHospital Platform (Concept)` - 19 edges
2. `Hands-Free Hospital Communication (Concept)` - 14 edges
3. `Wiki Overview` - 11 edges
4. `Condensed Intent & NER System — Vocera Voice Platform` - 11 edges
5. `Stryker SmartHospital Platform — US Marketing Hub` - 10 edges
6. `Sync Badge` - 10 edges
7. `Stryker Sync Badge — Hands-Free Clinical Communication Device` - 9 edges
8. `Vocera` - 9 edges
9. `Wiki Index` - 8 edges
10. `Stryker Medical-Surgical Equipment — US Portfolio Overview` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Clinical Communication (SmartHospital Pillar)` --encompasses--> `Hands-Free Hospital Communication (Concept)`  [INFERRED]
  wiki/notes/stryker-smart-hospital-platform.md → wiki/concepts/HandsfreeHospitalCommunication.md
- `EMDAN (Medical Device Alarm Notification)` --supports--> `Ambient Intelligence (SmartHospital Pillar)`  [INFERRED]
  wiki/notes/stryker-sync-badge.md → wiki/notes/stryker-smart-hospital-platform.md
- `Sync Badge` --semantically_similar_to--> `Smartbadge`  [INFERRED] [semantically similar]
  wiki/notes/stryker-sync-badge.md → wiki/notes/stryker-smart-hospital-platform.md
- `Wiki Overview` --references--> `Condensed Intent & NER System — Vocera Voice Platform`  [EXTRACTED]
  wiki/overview.md → wiki/notes/vocera-condensed-intent-ner-system.md
- `Wiki Overview` --references--> `Condensed Intent Classification (Concept)`  [EXTRACTED]
  wiki/overview.md → wiki/concepts/CondensedIntentClassification.md

## Hyperedges (group relationships)
- **Vocera Voice Processing Pipeline** — wake_word_detection, stt_pipeline, nlu_intent_routing, condensedintentclassification_concept, intent_reconstruction_engine, vocera_voice_server [EXTRACTED 0.95]
- **SmartHospital Platform Five Pillars** — clinical_communication_pillar, workflow_engine_pillar, virtual_care_pillar, ambient_intelligence_pillar, connected_infrastructure_pillar [EXTRACTED 1.00]
- **Condensed Intent Model Evaluation Candidates** — gpt_4o, gpt_4o_mini, gpt_41_nano, condensedintentclassification_concept [EXTRACTED 0.90]

## Communities

### Community 0 - "Vocera Product Ecosystem"
Cohesion: 0.25
Nodes (15): Connected Infrastructure Pillar, Smart Hospital Platform, Stryker, Virtual Care Pillar, Vocera Smartbadge, Sync Badge, Vocera Accessories, Clinical Communication (+7 more)

### Community 1 - "Wiki Structure & Stryker Core"
Cohesion: 0.54
Nodes (13): EMDAN (Medical Device Alarm Notification), Hands-Free Hospital Communication (Concept), Wiki Index, Wiki Overview, Interoperability-First Platform Strategy, Smartbadge, Stryker, Stryker Medical-Surgical Equipment — US Portfolio Overview (+5 more)

### Community 2 - "Condensed Intent NLP Pipeline"
Cohesion: 0.18
Nodes (12): Condensed Intent Classification (Concept), GPT-4.1-nano, GPT-4o, GPT-4o-mini, Intent Reconstruction Engine, NLU Intent Routing, Why Condensed Intent over Vanilla LLM, Model-Agnostic Design for Enterprise Healthcare (+4 more)

### Community 3 - "Smart Hospital Pillars & Spaces"
Cohesion: 0.2
Nodes (11): Ambient Intelligence (SmartHospital Pillar), Clinical Communication (SmartHospital Pillar), Connected Infrastructure (SmartHospital Pillar), Prime Series Transport, ProCuity Beds, SmartED (Care Space), SmartOR (Care Space), SmartRoom (Care Space) (+3 more)

### Community 4 - "Product Image Entities"
Cohesion: 0.36
Nodes (11): Ambient Monitoring, Patient Safety, Prime Series, Stryker Smart Hospital Platform, Stryker, Sync Badge, Clinical Workflow, Hands-Free Communication (+3 more)

### Community 5 - "Platform Pillars & Virtual Care"
Cohesion: 0.29
Nodes (11): Ambient Intelligence, Clinical Communication, Connected Infrastructure, Virtual Care, Workflow Engine, Virtual Monitoring, Virtual Nursing, Vocera Ease (+3 more)

### Community 6 - "ProCuity & Engage Products"
Cohesion: 0.36
Nodes (9): ProCuity, SmartHospital Platform, Stryker, Vocera, Ambient Intelligence, Clinical Communication, ProCuity LEX / ZX, ProCuity ZMX (+1 more)

### Community 7 - "Operation Log"
Cohesion: 1.0
Nodes (1): Wiki Log

## Knowledge Gaps
- **14 isolated node(s):** `Wiki Log`, `Intent Reconstruction Engine`, `Prime Series Transport`, `Workflow Engine (SmartHospital Pillar)`, `Virtual Care (SmartHospital Pillar)` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Operation Log`** (1 nodes): `Wiki Log`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SmartHospital Platform (Concept)` connect `Smart Hospital Pillars & Spaces` to `Wiki Structure & Stryker Core`, `Condensed Intent NLP Pipeline`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `Condensed Intent & NER System — Vocera Voice Platform` connect `Condensed Intent NLP Pipeline` to `Wiki Structure & Stryker Core`, `Smart Hospital Pillars & Spaces`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `Condensed Intent Classification (Concept)` connect `Condensed Intent NLP Pipeline` to `Wiki Structure & Stryker Core`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Hands-Free Hospital Communication (Concept)` (e.g. with `Sync Badge` and `Clinical Communication (SmartHospital Pillar)`) actually correct?**
  _`Hands-Free Hospital Communication (Concept)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Wiki Log`, `Intent Reconstruction Engine`, `Prime Series Transport` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._