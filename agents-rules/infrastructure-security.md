# Инфраструктура и secrets

## Текущий контекст и статус

HomeOps — существующее самостоятельное FastAPI-приложение; реализация описана в [README](../README.md), staging/deployment — в [правилах CI/CD](testing-deployment.md). Домашний Proxmox и LXC с Docker — инфраструктурный контекст проекта. По сообщённым пользователем сведениям ingress использует Nginx Proxy Manager (NPM), сертификаты — `acme.sh → shared certificates → NPM`; ранее зафиксирован отдельный AdGuard Home. Это контекст окружения, а не результат свежей проверки узлов.

HomeServer и компоненты ниже — согласованные планы или долгосрочные идеи, не уже развёрнутая инфраструктура. Готовность проверяется в отдельной задаче. Особое внимание: SSH, минимальные права, резервное восстановление, rollback, идемпотентность.

Общая [Network target architecture](network-architecture.md) — единый источник сетевых контуров, naming, public/private boundaries, Public Projection и будущего Event Plane. Она дополняет эти правила и учебный план, сохраняя current-state и прежние решения.

## HomeServer и границы проектов

HomeServer — целевой верхнеуровневый infrastructure/meta repository. HomeOps сохраняет собственный код, историю и учебный progression: не удалять его, не переписывать с нуля и не растворять в инфраструктурном репозитории. Крупные проекты могут подключаться по [правилам repositories/submodules](workflow.md).

Целевое логическое дерево, **не поручение создать каталоги**:

```text
HomeServer/
├── README.md
├── AGENTS.md
├── .github/
├── docs/
│   ├── architecture/
│   ├── current-state/
│   ├── diagrams/
│   ├── adr/
│   ├── plans/
│   ├── history/
│   ├── sessions/
│   ├── runbooks/
│   └── incidents/
├── infra/
│   ├── ansible/
│   ├── opentofu/
│   ├── traefik/
│   ├── monitoring/
│   ├── auth/
│   ├── forgejo/
│   ├── runners/
│   └── backup/
├── environments/
│   ├── lab/
│   ├── staging/
│   └── production/
├── HomeOps/
├── HomeMemory/
├── vpn/
└── ...
```

Небольшие инфраструктурные компоненты остаются в `infra/`, без отдельного repository на каждый сервис. Физическая структура появляется по реальной необходимости. ADR, runbooks и incidents оформляются по [правилам документации](documentation.md).

### HomeMemory / Knowledge Platform

[HomeMemory](homememory.md) — самостоятельный проект внутри HomeServer, на одном уровне с HomeOps. Он отвечает за долговременную память человека и AI-агентов и имеет собственные репозиторий, реализацию, roadmap, релизы и сопровождение. Код HomeMemory не размещается в backend HomeOps; связь проектов — отдельно согласованный read-only интерфейс. В логическом дереве выше показаны самостоятельные проекты, а не обычные вложенные Git-репозитории; способ подключения к HomeServer следует [правилам repositories/submodules](workflow.md#репозитории-и-источники-истины). Источником истины остаются Markdown + Git; целевые `docs/current-state/`, `architecture/`, `adr/`, `plans/`, `history/` и `sessions/` разделяют виды знаний внутри существующего `docs/`. Obsidian или совместимый vault работает с этими файлами. До появления HomeServer действуют README и тематические правила; перенос и создание каталогов выполняются только по реальной необходимости.

Будущая цепочка: отобранные и очищенные источники → Markdown + Git → производный hybrid search index (full-text + embeddings + metadata) → read-only MCP → Codex, позднее ChatGPT и HomeOps. PostgreSQL + pgvector — предпочтительный начальный backend индекса, заменяемый независимо от Markdown и интерфейса получения контекста; это не выбор БД для всех компонентов проекта. Импорт и индексирование имеют отдельный контур записи, MCP предоставляет только чтение. Подробности приоритетов источников и исключения чувствительных данных — в [правилах HomeMemory](homememory.md).

HomeMemory остаётся внутренним самостоятельным проектом HomeServer и не становится обязательной зависимостью работы HomeOps или инфраструктуры. Его развёртывание, обновление и восстановление планируются отдельно от HomeOps. Возможные поиск, история решений и «Ask HomeServer» в HomeOps UI развиваются позднее. Публичная витрина не получает доступ к внутреннему vault или индексу; применяются существующие [границы Core/Public](network-architecture.md#homeops-core-public-projection-и-public-store).

## Безопасные миграции и Traefik

Модель миграции: рабочее решение → новое решение параллельно → тестирование → переключение → период наблюдения с доступным rollback → удаление старого решения. Применять к ingress, runners, сертификатам, authentication, storage, networking, Forgejo и monitoring. Сначала документировать исходное состояние и способ возврата.

Согласовано постепенно перейти NPM → Traefik ради declarative configuration, Docker discovery, labels, API, automation, HomeOps integration, ACME, IaC и observability. Это решение о направлении, не выполненная миграция.

Последовательность: NPM работает → Traefik параллельно → тестовый route → HTTPS → DNS challenge → wildcard certificate → WebSocket/headers → перенос сервисов → проверка → 80/443 на Traefik → rollback window → только затем удаление NPM. Не удалять NPM до проверки замены. Discovery не отменяет минимальных прав доступа к Docker.

Прежнее целевое управление TLS, сохраняемое как legacy/transition design: `Traefik ↔ ACME ↔ DNS-01 ↔ DuckDNS ↔ Let's Encrypt`. Совместимость DNS, wildcard и выбранных версий проверять при реализации. Отдельный `acme.sh` и рабочую схему shared certificates сохранять до завершения миграции.

Новый target-state — собственный домен, provider-independent naming и DNS-01 через подходящего DNS provider; DuckDNS остаётся временным решением. Internal Traefik и public Traefik на Edge — разные роли/instances. Discovery, split DNS, wildcard и допустимая эволюция AdGuard → Technitium определены в [Network architecture](network-architecture.md#internal-ingress-dns-и-naming). Эта эволюция не меняет описанный выше порядок безопасной миграции.

## Configuration Management и Infrastructure as Code

Ansible — один из ближайших значимых учебных этапов: переход от понятной ручной повторяемой настройки Linux/LXC к configuration management. Постепенно освоить inventory, playbooks, modules, variables, handlers, templates, roles и idempotency. Реальные задачи: users, SSH, packages, Docker, directories, firewall, agents и service configuration. Не генерировать большую Ansible-инфраструктуру одним шагом.

После базового Ansible — OpenTofu для создания VM/LXC/network/resources. Ansible отвечает за настройку ОС и приложений. Целевая цепочка: `OpenTofu → Proxmox VM/LXC → Ansible → Docker/services`. Каждый уровень понять отдельно до объединения автоматизации.

Для Network target-state эта же цепочка расширяется на VPS и сетевые ресурсы, где применимо: provisioning — OpenTofu, configuration — Ansible, desired state — Git, validation/deployment — CI/CD. Учебный порядок Ansible перед OpenTofu сохраняется. Размещение network configuration в существующем `infra/`, без конкурирующего дерева, описано в [Network IaC](network-architecture.md#iac-gitops-и-secrets).

## Окружения и сеть

Постепенно разделять lab (опасные эксперименты и обучение), staging (проверка будущего production deployment) и production (стабильные используемые сервисы). Наличие staging не доказывает наличие остальных окружений. Не создавать инфраструктуру только ради трёх названий.

Сначала документировать текущую topology. Roadmap security zones: Management, Services, Lab, CI/Runners, VPN, Clients; VLAN возможны позднее, если позволяют сеть и оборудование. Не перестраивать сеть вслепую.

- Не публиковать Proxmox management напрямую.
- Lab не получает ненужный доступ к Management; runners получают минимальный доступ.
- Internet-facing traffic проходит через соответствующий ingress/reverse proxy.
- Административный доступ предпочтительно идёт через защищённую внутреннюю сеть/VPN.

Public CI и internal deployment разделяются по [CI/CD правилам](testing-deployment.md); VPN routing и Agent описаны в [архитектуре VPN](vpn-architecture.md).

Полный состав private control plane и допустимые Home ↔ VPS flows определены в [Network security boundaries](network-architecture.md#private-environment-и-security-boundaries). Backhaul не даёт VPS общего доступа к LAN. Локальная работа Core не зависит от Edge, а public showcase читает отдельный sanitized read model; [модель независимости](network-architecture.md#независимость-private-и-public) задаёт поведение при отказах.

## Secrets и границы публикации

Пароли, API keys, SSH private keys и токены не записывать в репозиторий. Использовать GitHub Secrets/environment secrets и `.env` по назначению. `.env` с секретами должен исключаться через `.gitignore`; `.env.example` содержит только примеры без реальных секретов.

Планируется SOPS + age для Git-managed secrets. Не хранить открыто passwords, tokens, API keys, private keys, DuckDNS/Forgejo tokens, HomeOps secrets и production credentials; публичные examples используют placeholders. Ключи расшифрования не размещать в Git вместе с зашифрованными данными.

Полная внутренняя конфигурация HomeServer может храниться в private Forgejo. Private addresses, hostnames, VLAN, inventory, domains, topology, firewall information и deployment targets требуют осознанной границы доступа. Публичное представление на GitHub очищать от чувствительных инфраструктурных данных. Можно показывать architecture, example inventory, roles, generic IaC, documentation, sanitized configurations и CI/CD design. Ранее записанные внутренние сведения не считать автоматически разрешёнными к новой публикации.

## Observability и учебные аварии

Roadmap: Prometheus, Grafana, Loki, Alertmanager; постепенно наблюдать Proxmox, LXC, Docker, Traefik, HomeOps, VPN, AdGuard и system resources. HomeOps в будущем экспортирует application metrics. Учебные цели — metrics, logs, alerts, troubleshooting, incident response, SLI и SLO, а не только установка dashboard.

Network-specific signals, events, topology и агрегированное представление HomeOps описаны в [Network observability](network-architecture.md#observability-network-events-и-ui). Event Plane развивается от application events/workers к Kafka только при обоснованной потребности; Kafka остаётся private и не обязательна для basic HomeOps functionality.

Контролируемые аварии допустимы в отдельно согласованном LAB-упражнении: остановка контейнера, DNS/route/certificate/VPN/database failure, CPU load, заполнение тестового disk. Проверять изоляцию и способ восстановления. Цикл: failure → detection → alert → diagnosis → runbook → recovery. В production не проводить такие эксперименты без прямого решения пользователя. VPN-специфичные проверки остаются в [эксплуатационных правилах VPN](vpn-operations.md).

## Authentication, backup и дальнейшие этапы

После базовой стабильности приложений возможен Authentik или аналогичный Identity Provider: Traefik → Authentication/OIDC → internal services. Для HomeOps позднее рассматриваются OIDC, JWT, RBAC, MFA concepts и audit log; это не текущая функциональность.

Backup полноценен только с проверенным restore. Roadmap: Proxmox Backup Server или эквивалент, retention, verification, restore tests, RPO и RTO. Учебный сценарий только в безопасной LAB-среде по отдельному поручению: удалить test LXC → restore → Ansible → services available → verification.

Forgejo mirror сохраняет Git repository data, но не является полноценным backup Forgejo. Нужен отдельный backup/restore базы, конфигурации, users, Issues, PR, Actions, Releases, Packages, attachments и metadata.

Renovate — будущие контролируемые обновления: PR → CI → review → staging → production. Не включать бесконтрольные production updates.

Kubernetes/K3s не является ближайшей задачей. Сначала уверенно освоить Linux, networking, Git, Docker/Compose, Traefik, CI/CD, Ansible, monitoring, secrets и backups. Затем возможен отдельный K3s LAB для сравнения эксплуатационных свойств Docker Compose и Kubernetes. Рабочую Compose-инфраструктуру сохранять.

## Поэтапный учебный план HomeServer/HomeOps

Отправная точка — существующий HomeOps и реализованная в workflow цепочка tests → publish в GHCR → pull на staging → health checks/условный rollback. Не повторять реализацию Docker pull как новую задачу. Наличие кода не заменяет проверку запуска и освоение механизма. План задаёт учебные зависимости и критерии освоения без сроков; каждый этап делится на маленькие задачи по [учебному циклу](collaboration.md), а не выполняется Codex автоматически.

| Этап | Практический результат | Условие перехода дальше |
| --- | --- | --- |
| 1. Завершить текущий CI/CD | Разобрать существующие изменения rollback, проверить восстановление, изолировать public PR tests от домашней сети; постепенно добавить нужные проверки | Пользователь объясняет путь образа и сценарии ошибок; есть фактическая проверка восстановления. Подробный порядок — в [CI/CD плане](testing-deployment.md#ближайшие-учебные-шаги) |
| 2. Описать инфраструктуру и оформить HomeServer | Зафиксировать текущие узлы, сервисы, ingress, DNS/TLS, runners, данные и границы доступа; выбрать authoritative repositories и минимальную структуру HomeServer | Схема соответствует реальности, public/private разделены, самостоятельность HomeOps сохранена; нужны только реально используемые каталоги |
| 3. Освоить Ansible на LAB | Воспроизвести небольшой понятный ручной процесс: inventory, безопасное подключение, один playbook, затем variables/handlers/templates/roles | Повторный запуск не делает ненужных изменений; пользователь понимает idempotency и диагностику |
| 4. Подготовить повторяемый запуск сервисов | Освоить Docker Compose на одном LAB-сервисе; постепенно описывать конфигурацию через Ansible | Понятны ports, networks, volumes, configuration и способ восстановления; существующий staging не мигрирует автоматически |
| 5. Перейти к Traefik | Выполнить описанную выше постепенную миграцию ingress и TLS с ADR | Проверены HTTPS, DNS-01, wildcard, headers/WebSocket, наблюдение и rollback; только затем убрать NPM/acme.sh |
| 6. Укрепить внутреннюю платформу | GitHub/Forgejo, односторонние mirrors, изолированный internal runner, SOPS/age и минимальные права | Проверены границы доступа и восстановление Forgejo; публичные PR не исполняются в домашней сети |
| 7. Добавить OpenTofu | Создать один тестовый ресурс Proxmox, затем настроить его Ansible | Пользователь понимает plan/apply, state, границу provisioning/configuration и безопасное удаление LAB-ресурса |
| 8. Развивать прикладной HomeOps | Небольшими шагами добавить проверки сервисов, обоснованное хранение данных, затем read-only интеграции Docker/Traefik/Proxmox | Каждая функция имеет понятный API, тесты ошибок и наблюдаемое поведение; существующий пользовательский код сохраняется |
| 9. Освоить observability и восстановление | Metrics/logs/alerts, application metrics HomeOps, SLI/SLO; один контролируемый отказ, runbook, incident и restore test | Пользователь обнаруживает, объясняет и устраняет отказ; известны проверенные RPO/RTO для выбранного сценария |
| 10. Развивать VPN-домен | Read-only состояние → authenticated Agent → allowlisted operations → routing/health/failover по [VPN roadmap](vpn-roadmap.md) | Каждый слой проверяется отдельно в LAB; нет произвольного remote shell и неконтролируемого fallback |
| 11. Укреплять эксплуатацию | По реальной потребности добавить OIDC/RBAC/audit, security zones/VLAN, production promotion и Renovate | Контролируемые действия защищены до их включения; обновление, откат и restore понятны и проверены |
| 12. Сравнить с K3s | Отдельный необязательный LAB после уверенного освоения предыдущей базы | Сравниваются реальные свойства эксплуатации; Compose-инфраструктура сохраняется |

Это ориентир зависимостей, а не жёсткий waterfall: backend можно развивать между инфраструктурными занятиями. Прежний акцент на завершении CI/CD сохраняется как план этого направления, но не задаёт обязательную тему следующей сессии. Допускается чередовать направления для разнообразия практики по [правилам переключения](collaboration.md#чередование-тем-и-точки-продолжения). Актуальную точку продолжения восстанавливать по последним обсуждениям и относящимся к задаче проверкам; номер этапа сам по себе не является приоритетом.

Подробный [Network roadmap](network-architecture.md#поэтапное-развитие-network) связывает этапы 2/5/8/9/10/11: current-state → internal discovery → Gateway/один node → multi-node health → policies/failover → own domain/split DNS → Edge/backhaul → Public Projection/Store → observability integration → event-driven расширение при необходимости. Это детализация, не новая обязательная нумерация; базовая диагностика и безопасность нужны с первых шагов.

Самостоятельный [HomeMemory roadmap](homememory.md#поэтапное-развитие-homememory) соотносится с общим учебным планом: документирование на этапе 2, backend и интеграции на этапе 8, эксплуатацию и защиту на этапах 9/11: Markdown/vault → ручной отбор итогов → базовый поиск → hybrid RAG + read-only MCP → автоматический импорт → возможный HomeOps UI. Эта связь описывает учебные зависимости, а не включение реализации HomeMemory в backlog HomeOps. Разработка и сопровождение HomeMemory планируются отдельно; работа над сервисом начинается только отдельным согласованным учебным шагом.

Уточнение приоритета HomeMemory: его минимальная документальная основа — ближайшая параллельная работа рядом с текущим выбранным направлением. Прежняя привязка к этапу 1 (CI/CD) уточнена: сохранение знаний нужно и при работе с хранилищем, сетью, backend или другими частями HomeServer. Не откладывать сохранение знаний до оформления HomeServer или этапа 8. Связи с этапами 2/8/9/11 описывают учебные темы, а не обязательное ожидание этих номеров. Сначала небольшой полезный корпус и итоги сессий, затем поиск и read-only MCP/RAG по готовности; подробный [ближайший приоритет](homememory.md#ближайший-параллельный-приоритет) не меняет границ поручений.

Базовые backup, secrets, минимальные права и диагностика нужны с первого затрагивающего их шага, а не откладываются до номера этапа. До любой миграции проверять восстановление; до controlled actions — authentication, validation и audit. Production не является обязательным результатом ближайшей сессии.

С рабочего ПК без подтверждённого доступа к домашней инфраструктуре выбирать анализ репозитория, проектирование, локальные учебные изменения и доступные GitHub-проверки. Подключения, deployments и аварийные упражнения проводить только при подтверждённом доступе и отдельной согласованной задаче. Перед новой реализацией проверить незавершённые ветки/PR в рамках поручения, чтобы не повторять уже написанную работу.

## Направление интеграций HomeOps

Ориентир, а не поручение реализовать всё: REST API + tests → service monitoring → Docker integration → Traefik integration → Proxmox integration → VPN integration → observability → OIDC/RBAC → audit → controlled actions. Alerts и authentication добавляются постепенно. Реализованную основу отличать от будущих интеграций; Docker/Traefik/Proxmox API сейчас не считать подключёнными.

VPN/control-plane сохраняет [собственную архитектуру](vpn-architecture.md) и [roadmap](vpn-roadmap.md). HomeOps связывает знания, а не заменяет изучение каждого слоя готовой автоматизацией.

Network-направление HomeOps: infrastructure control plane + observability view + network policy interface + отдельный public portfolio showcase. HomeOps интегрирует специализированные инструменты, не заменяя Proxmox, Prometheus/Grafana, Traefik, DNS, Kafka, Ansible и OpenTofu. Public/Core и их данные разделяются по [Network architecture](network-architecture.md#homeops-core-public-projection-и-public-store).

Не скрывать обнаруженные проблемы. Предупреждения должны относиться к конкретному действию и его последствиям, а не заменять практическую работу общей памяткой.
