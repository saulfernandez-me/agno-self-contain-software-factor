# 📑 Skill: Spec-Driven Development (RFCs & ADRs)

You are operating under a strict "Spec-Driven Development" methodology. You do not place heavy architectural designs or technical context into task trackers (GitHub Issues). Instead, you write formal documents to the repository.

## 1. Document Types & Definitions

### A. RFC (Request for Comments / Tech Spec)
- **Where:** `docs/rfcs/`
- **When to use:** When designing a new feature, Epic, or complex system.
- **Content:** The "Why" (Business Context) and the "How" (Data models, endpoints, implementation steps).
- **Format:** Use `docs/rfcs/NNN-feature-name.md` (e.g., `001-user-auth.md`).

### B. ADR (Architecture Decision Record)
- **Where:** `docs/adrs/`
- **When to use:** When a decision changes the fundamental architecture of the system or establishes a new invariant (e.g., "Switching from REST to GraphQL").
- **Content:** Context, Decision, and Consequences.
- **Format:** Use `docs/adrs/NNN-decision-name.md` (e.g., `001-use-fastapi.md`).

## 2. Issue Formulation (The Execution Ticket)
GitHub Issues must be "Execution Tickets", not design documents.
An Issue MUST contain:
1. **Pointer:** A direct link to the physical RFC file (e.g., "See `docs/rfcs/005-payment-gateway.md` for context").
2. **Actionable Task:** What specifically needs to be built in this ticket.
3. **Definition of Done (DoD):** Checklists to prove completion.
4. **Verification Command:** The shell command to test the task.
