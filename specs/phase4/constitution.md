# Phase IV Constitution — Project-Based UI Expansion (UI-First)

## 1. Purpose of This Constitution

This Constitution defines the immutable laws governing Phase IV of the project.
Phase IV introduces project-based organization while preserving all contracts
established in Phases I, II, and III.

This Constitution has absolute authority over all Phase IV specifications,
plans, tasks, and implementations.

---

## 2. Project-Centric Principle

- All tasks MUST belong to exactly one project.
- A project MUST be the highest-level organizational unit.
- Tasks MUST NOT exist outside a project context.
- Default or implicit projects are forbidden.

---

## 3. UI-First Expansion Principle

- All Phase IV behavior MUST be observable through the UI.
- UI behavior MUST be specified before any internal changes.
- Internal data structures MUST NOT introduce UI-visible behavior
  not explicitly defined in the spec.

---

## 4. Backward Contract Preservation

- Phase I task semantics MUST remain unchanged.
- Phase II UI command structure MUST remain unchanged unless explicitly extended.
- Phase III persistence guarantees MUST remain unchanged.
- Existing tasks MUST remain valid when assigned to a project.

---

## 5. Deterministic Project Interaction

- Project creation, selection, and listing MUST be deterministic.
- UI output for project operations MUST be stable and predictable.
- No implicit project switching is allowed.

---

## 6. Explicit Context Principle

- The active project context MUST be explicit in all UI interactions.
- Hidden or inferred project context is forbidden.
- UI MUST clearly indicate the current project scope.

---

## 7. Isolation & Ownership

- Tasks MUST NOT be shared across projects.
- Operations in one project MUST NOT affect another project.
- Project boundaries MUST be strictly enforced.

---

## 8. AI as Executor Only

- AI agents MUST implement only what is explicitly defined in Phase IV specs.
- AI agents MUST NOT invent project behaviors, defaults, or shortcuts.
- AI agents MUST NOT modify Phase I–III behavior.

---

## 9. Change Control

- Phase IV principles are immutable unless this Constitution is revised.
- No silent overrides, aliases, or compatibility hacks are allowed.

---

## 10. Precedence & Enforcement

- Constitution > Phase IV Specs > Plans > Tasks > Implementation
- Any violation invalidates the Phase IV implementation.