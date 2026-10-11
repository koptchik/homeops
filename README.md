# HomeOps

HomeOps is a long-term learning project for backend development and home infrastructure operations. Codex acts as a mentor; the user gains practical experience through small, explained and verified steps. Learning takes priority over delivery speed and automation.

## Current implementation

- FastAPI backend with `GET /health` and a `/services` router for creating, listing, retrieving and deleting service records.
- Pydantic input validation; records and IDs are held in process memory. There is no persistent database or scheduled service monitoring yet. `check_interval` is currently stored data, not an active scheduler.
- pytest/TestClient tests for health and the implemented service operations, with a fixture resetting in-memory state.
- Application and test Dockerfiles using Python 3.11.
- GitHub Actions configuration for containerized tests, SHA-tagged GHCR image publication, and staging on self-hosted Linux/LXC runners with health checks, conditional rollback and image cleanup.

The deployment chain is connected: tests → GHCR publication → staging pulls and runs the image tagged with the same commit SHA, without rebuilding it. PR tests currently use a self-hosted runner; the target isolation model is not yet implemented in the workflow. See [CI/CD context and rules](agents-rules/testing-deployment.md).

These statements describe repository contents, not a fresh test run or verification of live infrastructure. No Compose configuration is currently tracked in this repository.

## Architectural direction and roadmap

HomeOps remains an independent application. HomeServer is the planned infrastructure/meta repository; it does not replace HomeOps. The goal is a gradually developed infrastructure control plane, with possible Docker, Traefik, Proxmox and VPN integrations, application metrics, alerts, authentication, audit and controlled actions. These integrations are not implemented yet.

The earlier React/TypeScript dashboard and PostgreSQL stack remain possible future choices, not installed components or binding next steps. The VPN design separately considers SQLite for an initial management layer; persistence will be selected when that work is agreed. Prometheus and Grafana remain part of the future observability direction.

The [infrastructure rules](agents-rules/infrastructure-security.md) hold the HomeServer target architecture and roadmap: gradual NPM-to-Traefik migration, Ansible before OpenTofu, GitHub/Forgejo roles, isolated runners, observability, secrets and verified backup/restore. The [VPN architecture](agents-rules/vpn-architecture.md), [operations](agents-rules/vpn-operations.md) and [VPN roadmap](agents-rules/vpn-roadmap.md) preserve that domain's existing design.

The [HomeServer Network target architecture](agents-rules/network-architecture.md) defines private service networks, internal Traefik and split DNS, a provider-independent VPN node inventory, and separate egress, infrastructure backhaul and Public Edge roles. AdGuard Home and DuckDNS remain current/transition context; a custom domain is the target, with Technitium a possible later DNS choice.

HomeOps Core stays private. Future read-only Public HomeOps runs on the Edge using a sanitized Public Projection and a separate Public Store; visitor requests do not call the home administrative API. Public data carries freshness information so the showcase can display last known state when HomeServer is unavailable. Kafka is a possible future private event backbone, not a current dependency. These are architectural plans, not implemented integrations.

The [Network learning roadmap](agents-rules/network-architecture.md#поэтапное-развитие-network) and [decision records with alternatives and trade-offs](agents-rules/network-architecture.md#решения-и-учебные-компромиссы) extend the existing learning path without authorizing migrations.

[HomeMemory / Knowledge Platform](agents-rules/homememory.md) is a separate project within HomeServer, alongside HomeOps. It has its own repository, implementation, roadmap and maintenance lifecycle; HomeOps is a potential client of its read-only interface. HomeMemory preserves project state, architecture, ADRs, plans, history and useful ChatGPT/Codex session summaries beyond a single context window. Markdown + Git is the versioned source of truth; Obsidian or a compatible Markdown vault provides a human interface. The target adds hybrid retrieval (full-text, embeddings and metadata), with PostgreSQL + pgvector as the preferred initial, replaceable search backend, and a shared read-only MCP context interface for Codex and later ChatGPT/HomeOps.

Future import and indexing will prioritize canonical/current-state documents over historical chats and exclude secrets and sensitive configuration data. Optional HomeOps UI features include knowledge search, decision history and “Ask HomeServer”. HomeMemory is a planned independent service, not a HomeOps module or a database decision for the existing application or VPN domain. Its implementation and deployment do not depend on HomeOps releases; any future HomeOps UI integration is a separate client-side task. It does not enable chat synchronization or replace the current infrastructure learning and portfolio goals; see its [staged roadmap](agents-rules/homememory.md#поэтапное-развитие-homememory).

## Project context

Start with [AGENTS.md](AGENTS.md) for the existing thematic rules and their scopes. [Collaboration rules](agents-rules/collaboration.md) define the learning cycle and Codex permissions. [Documentation rules](agents-rules/documentation.md) define how decisions, runbooks and incidents are recorded. Roadmap entries do not authorize implementation or infrastructure changes.
