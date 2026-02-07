<!-- SYNC IMPACT REPORT:
Version change: N/A → 1.0.0
Added sections: All sections (new constitution)
Removed sections: None
Templates requiring updates: N/A (new file)
Follow-up TODOs: None
-->

# In-Memory Python Console Todo App Constitution

## Core Principles

### Spec-Driven Development Principle
No code may be generated before the spec is complete. Claude Code or AI agents MUST implement only what is in the approved spec. Manual coding is strictly forbidden.

### Determinism and Traceability
All outputs MUST be deterministic. All AI agent actions MUST be traceable back to the spec. No improvisation or hallucinated behaviors are allowed.

### Progressive Evolution Principle
Phase I is the foundation; principles MUST enable future growth without violating Phase I contracts. Changes to core Phase I behaviors MUST be explicitly authorized via Constitution revision.

### Separation of Responsibility
Input, processing, and output MUST be clearly separated. AI agents MAY execute tasks but MUST NOT redefine responsibilities. Users, AI agents, and in-memory storage MUST operate within defined boundaries.

### Statelessness as Default
Even though Phase I is in-memory, all state logic MUST be explicit and clearly recoverable. Hidden or implicit state is forbidden.

### User Ownership & Isolation
Each user's tasks MUST be isolated. No cross-user data access is allowed.

### AI as Executor, Not Designer
AI MUST follow specs for task creation, update, deletion, listing, and completion. AI MUST NOT invent features or behaviors outside the approved Phase I spec.

### Change Control Principle
Phase I principles are immutable unless explicitly revised in `/sp.constitution.md`. Silent modifications or workarounds are strictly prohibited.

### Precedence & Enforcement
Constitution > Phase I Specs > Tasks > Implementation. Any violation invalidates the Phase I implementation.

## Purpose of the Constitution
This Constitution defines the immutable laws and non-negotiable principles that govern the design, evolution, and AI interaction for Phase I of the In-Memory Python Console Todo App. This document establishes the authority of principles over all specifications and code for this phase.

## Governance
This Constitution serves as the ultimate authority governing all aspects of Phase I development. All implementations, specifications, and AI agent actions MUST comply with these principles. Any amendments to this Constitution require explicit revision and must be documented in the version control system. All development activities must verify compliance with constitutional principles.

**Version**: 1.0.0 | **Ratified**: 2026-01-31 | **Last Amended**: 2026-01-31