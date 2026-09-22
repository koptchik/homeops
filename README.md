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

## Project context

Start with [AGENTS.md](AGENTS.md) for the existing thematic rules and their scopes. [Collaboration rules](agents-rules/collaboration.md) define the learning cycle and Codex permissions. [Documentation rules](agents-rules/documentation.md) define how decisions, runbooks and incidents are recorded. Roadmap entries do not authorize implementation or infrastructure changes.
