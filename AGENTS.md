# AGENTS.md

## Purpose

<Concise statement of what this project does and who it serves.>
<Why this repository exists and what outcome it enables.>

<This repository uses AI assistance to help analyze changes and perform>
<explicitly requested actions in a controlled and human-readable way.>

Help me to develment faster

---

## Project Summary (Human & Agent Context)

<!-- Add a concise project summary here -->

<This section provides high-level context for both humans and agents.>
<It should be updated occasionally by humans or via a reporting workflow.>

### Overview

- Project type: <!-- describe the project type -->
- Primary stack:
  - Backend: <!-- backend tech -->
  - Frontend: <!-- frontend tech -->
  - Environment: <!-- environment/tooling -->

- Intended users: <!-- who uses this system -->

### Key Areas

<Areas>
- <Area 1:> <!-- area focus -->
- <Area 2:> <!-- area focus -->
- <Area 3:> <!-- area focus -->

### Operational Notes

- How the project is typically run or built
- Important constraints or assumptions
- Links to key docs (README, architecture notes, etc.)

### Current State

<!-- Known risks or limitations (high level) -->
<!-- Open questions -->

- Maturity: <!-- prototype | active | stable | legacy -->

---

## Global Rules (Apply to ALL agents)

- Do NOT assume intent
- Run a Workflow ONLY when explicitly requested
- Workflow execution ALWAYS requires explicit user confirmation
- If no Workflow is invoked: analysis and discussion only
- Avoid side effects unless confirmed
- Prefer analysis before modification
- No large refactors unless explicitly approved
- If context is missing, stop and ask
- Separate facts from recommendations clearly

---

## Agent Modes (REQUIRED — choose exactly ONE)

The agent MUST always be operating in a declared mode.
If this section is missing OR none/multiple modes are `enabled`, the agent MUST stop and ask which mode to use.

Mode declaration (MUST be present; set exactly one to `enabled`):

- Analyze Mode: disabled
- Action Plan Mode: disabled
- Agent Mode: disabled

### Analyze Mode (Docs-only; create-only)

- Allowed: read/search repository files; create NEW documentation files (summaries/reports) only (no edits, no deletes); propose Action Plans.
- Allowed: Read All git Commits.
- If any edit/deletion is needed (even for docs), stop and ask to switch to Action Plan Mode.
- Not allowed: modify or delete any file (including documentation); touch code/config; run commands with side effects; run any Git operations.

### Action Plan Mode (Plan-driven; ask before each file change)

- Requires: an explicit Action Plan reviewed + approved by the user.
- The Action Plan MUST list every file operation (create/modify/delete) with exact paths.
- Before execution, ask deliverables: Documentation | Code | Both.
  - If Documentation is requested: ask location (e.g. `docs/`) and depth (overview vs function/API-level).
- BEFORE each file operation (create/modify/delete): state the path + operation + intent and ask for explicit confirmation (no batch confirmations).
- For new files: ask content level per file: Template/Skeleton | Full Code.
- No undeclared/collateral changes.

### Agent Mode (More autonomous; ask before Git)

- Only active when explicitly enabled by the user.
- Allowed: implement quickly (scaffolding, helper files, small refactors) to keep coherence.
- MUST ask for explicit confirmation before any Git operation (`git add`, `git commit`, `git push`, `git reset`, `git rebase`, branch/tag ops, etc.).
- Must list all created/modified/deleted files and intent.

---

## Workflows

Workflows are **optional, on-demand tasks**.
They never run automatically.
Workflow execution is mode-agnostic; when explicitly requested and confirmed, the workflow's own scope and limitations apply regardless of the enabled Agent Mode.

Before executing ANY Workflow, the agent MUST:

1. Restate the workflow name
2. Summarize what will happen (side effects)
3. Ask for explicit confirmation

Execution MUST NOT proceed without clear confirmation
(e.g. "Proceed", "Yes, run it", "Approved").

---

### Workflow Annexes

Workflow definitions live in `AGENTS.d/workflows/` and inherit the rules in this file.

- [CreateCommit](AGENTS.d/workflows/CreateCommit.md)
- [GenerateProjectReport](AGENTS.d/workflows/GenerateProjectReport.md)

---

### Scope Limits

- Agents must NOT invent new workflows
- Agents must NOT run workflows implicitly
- Agents must NOT generate commit messages outside the canonical format

---
