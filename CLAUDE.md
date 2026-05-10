# CLAUDE.md — cloud-security-intelligence

This file defines how Claude Code should assist on this project.
Read it fully before writing any code, suggesting any changes, or running any commands.

---

## Project Overview

A multi-agent system that scans GCP environments for security misconfigurations using
Security Command Center, enriches findings with threat intelligence, and generates
prioritized remediation reports. Deployed on GCP Cloud Run with full observability
via Cloud Logging, Cloud Monitoring, and Cloud Trace.

---

## My Learning Goals

This project exists to build real understanding, not just working code.
The following rules exist to protect that goal.

**Claude's role is to assist and explain — not to drive.**
I make the architectural decisions. I write the first version of everything that matters.
Claude helps me improve what I've written, explains things I don't understand,
and handles boilerplate that doesn't teach me anything.

---

## What Claude Can Do Without Being Asked

- Fix syntax errors in code I've written
- Suggest improvements to code I've already written and understand
- Write boilerplate: Dockerfiles, Cloud Build YAML, .gitignore
- Write or improve tests once I've defined what needs to be tested
- Explain GCP services, CrewAI concepts, or Python patterns when I ask
- Catch security issues (hardcoded secrets, overly permissive IAM, missing input validation)
- Use the CrewAI CLI to scaffold project structure — this is expected and encouraged

---

## What Claude Must NOT Do

- Write the first version of any agent (role, goal, backstory, or task) — I write those
- Design the Pydantic models between agents — I define the data contracts
- Make GCP architecture decisions (which services to use, how they connect)
- Design the observability schema (what gets logged, what metrics matter)
- Write the agent loop or orchestration logic from scratch
- Refactor working code into patterns I haven't learned yet without explaining why
- Use frameworks or libraries not already in this project without flagging it first

---

## Stack

- **Language:** Python 3.13
- **Package manager:** uv (managed by CrewAI CLI)
- **Agent framework:** CrewAI
- **LLM:** Anthropic Claude (claude-sonnet-4-20250514 unless otherwise specified)
- **Cloud:** GCP — Cloud Run, Cloud Tasks, Cloud Storage, Secret Manager,
  Security Command Center, Cloud Logging, Cloud Monitoring, Cloud Trace,
  Artifact Registry, Cloud Build, Workload Identity Federation
- **Observability:** Structured JSON logging, custom Cloud Monitoring metrics, Cloud Trace
- **CI/CD:** Cloud Build triggered on push to main

---

## Project Structure

```
gcp-security-intelligence/
├── src/gcp_security_intelligence/
│   ├── config/
│   │   ├── agents.yaml       # Agent definitions (role, goal, backstory)
│   │   └── tasks.yaml        # Task definitions and expected outputs
│   ├── tools/                # CrewAI tools (SCC API wrapper, enrichment, etc.)
│   ├── schemas/              # Pydantic models for inter-agent data contracts
│   ├── observability/        # Logging, metrics, and tracing setup
│   ├── crew.py               # Crew assembly and orchestration
│   └── main.py               # Application entry point / Cloud Run handler
├── tests/                    # Unit and integration tests
├── cloudbuild.yaml           # Cloud Build CI/CD pipeline
├── Dockerfile                # Container definition
├── pyproject.toml            # Dependencies managed by uv
└── CLAUDE.md                 # This file
```

---

## Code Style Rules

- All functions must have type hints and a one-line docstring
- Structured JSON logging only — no print() statements in production code
- Every log entry must include: trace_id, agent_name, event_type, and timestamp
- No secrets in code or environment variables — Secret Manager only
- All GCP authentication via Workload Identity Federation — no service account key files
- Pydantic models for all inter-agent data — no passing raw dicts between agents
- Maximum function length: 40 lines. If longer, it needs to be broken up

---

## Observability Requirements

Every agent run must produce:
- A structured log entry at the start and end of each agent's execution
- A log entry for every tool call (input and output)
- Token usage logged after every LLM call
- A unique trace_id that follows the entire crew run end to end
- Custom metric increments for: runs_started, runs_completed, runs_failed, tool_calls_total

These are non-negotiable. Do not skip observability for "just testing" purposes.

---

## Security Requirements (non-negotiable)

- No hardcoded credentials anywhere in the codebase
- No service account key files — Workload Identity Federation only
- All API keys stored in and retrieved from Secret Manager
- Input validation on all external inputs (project IDs, API responses)
- Principle of least privilege on all IAM bindings — no Editor or Owner roles
- VPC Service Controls perimeter around SCC and Secret Manager APIs

---

## How to Run Locally

```bash
# CrewAI CLI scaffolds the project and manages dependencies via uv
crewai create crew cloud-security-intelligence

# Install dependencies
uv sync

# Set environment variables for local dev only
export ANTHROPIC_API_KEY="your-key-here"
export GCP_PROJECT_ID="your-project-id"

# Run the crew
crewai run
```

---

## When I Ask Claude to Explain Something

Give a clear explanation first, then show code if relevant.
Do not give me code without an explanation. I need to understand what I'm building.

---

## When I'm Stuck

Ask me what I've already tried and what I think the problem is before suggesting a fix.
I learn more from being guided to the answer than from being given it.