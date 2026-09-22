# Инфраструктура и secrets

## Текущий контекст и статус

HomeOps — существующее самостоятельное FastAPI-приложение; реализация описана в [README](../README.md), staging/deployment — в [правилах CI/CD](testing-deployment.md). Домашний Proxmox и LXC с Docker — инфраструктурный контекст проекта. По сообщённым пользователем сведениям ingress использует Nginx Proxy Manager (NPM), сертификаты — `acme.sh → shared certificates → NPM`; ранее зафиксирован отдельный AdGuard Home. Это контекст окружения, а не результат свежей проверки узлов.

HomeServer и компоненты ниже — согласованные планы или долгосрочные идеи, не уже развёрнутая инфраструктура. Готовность проверяется в отдельной задаче. Особое внимание: SSH, минимальные права, резервное восстановление, rollback, идемпотентность.

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
│   ├── diagrams/
│   ├── adr/
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
├── vpn/
└── ...
```

Небольшие инфраструктурные компоненты остаются в `infra/`, без отдельного repository на каждый сервис. Физическая структура появляется по реальной необходимости. ADR, runbooks и incidents оформляются по [правилам документации](documentation.md).

## Безопасные миграции и Traefik

Модель миграции: рабочее решение → новое решение параллельно → тестирование → переключение → период наблюдения с доступным rollback → удаление старого решения. Применять к ingress, runners, сертификатам, authentication, storage, networking, Forgejo и monitoring. Сначала документировать исходное состояние и способ возврата.

Согласовано постепенно перейти NPM → Traefik ради declarative configuration, Docker discovery, labels, API, automation, HomeOps integration, ACME, IaC и observability. Это решение о направлении, не выполненная миграция.

Последовательность: NPM работает → Traefik параллельно → тестовый route → HTTPS → DNS challenge → wildcard certificate → WebSocket/headers → перенос сервисов → проверка → 80/443 на Traefik → rollback window → только затем удаление NPM. Не удалять NPM до проверки замены. Discovery не отменяет минимальных прав доступа к Docker.

Целевое управление TLS: `Traefik ↔ ACME ↔ DNS-01 ↔ DuckDNS ↔ Let's Encrypt`. Совместимость DNS, wildcard и выбранных версий проверять при реализации. Отдельный `acme.sh` и рабочую схему shared certificates сохранять до завершения миграции.

## Configuration Management и Infrastructure as Code

Ansible — один из ближайших значимых учебных этапов: переход от понятной ручной повторяемой настройки Linux/LXC к configuration management. Постепенно освоить inventory, playbooks, modules, variables, handlers, templates, roles и idempotency. Реальные задачи: users, SSH, packages, Docker, directories, firewall, agents и service configuration. Не генерировать большую Ansible-инфраструктуру одним шагом.

После базового Ansible — OpenTofu для создания VM/LXC/network/resources. Ansible отвечает за настройку ОС и приложений. Целевая цепочка: `OpenTofu → Proxmox VM/LXC → Ansible → Docker/services`. Каждый уровень понять отдельно до объединения автоматизации.

## Окружения и сеть

Постепенно разделять lab (опасные эксперименты и обучение), staging (проверка будущего production deployment) и production (стабильные используемые сервисы). Наличие staging не доказывает наличие остальных окружений. Не создавать инфраструктуру только ради трёх названий.

Сначала документировать текущую topology. Roadmap security zones: Management, Services, Lab, CI/Runners, VPN, Clients; VLAN возможны позднее, если позволяют сеть и оборудование. Не перестраивать сеть вслепую.

- Не публиковать Proxmox management напрямую.
- Lab не получает ненужный доступ к Management; runners получают минимальный доступ.
- Internet-facing traffic проходит через соответствующий ingress/reverse proxy.
- Административный доступ предпочтительно идёт через защищённую внутреннюю сеть/VPN.

Public CI и internal deployment разделяются по [CI/CD правилам](testing-deployment.md); VPN routing и Agent описаны в [архитектуре VPN](vpn-architecture.md).

## Secrets и границы публикации

Пароли, API keys, SSH private keys и токены не записывать в репозиторий. Использовать GitHub Secrets/environment secrets и `.env` по назначению. `.env` с секретами должен исключаться через `.gitignore`; `.env.example` содержит только примеры без реальных секретов.

Планируется SOPS + age для Git-managed secrets. Не хранить открыто passwords, tokens, API keys, private keys, DuckDNS/Forgejo tokens, HomeOps secrets и production credentials; публичные examples используют placeholders. Ключи расшифрования не размещать в Git вместе с зашифрованными данными.

Полная внутренняя конфигурация HomeServer может храниться в private Forgejo. Private addresses, hostnames, VLAN, inventory, domains, topology, firewall information и deployment targets требуют осознанной границы доступа. Публичное представление на GitHub очищать от чувствительных инфраструктурных данных. Можно показывать architecture, example inventory, roles, generic IaC, documentation, sanitized configurations и CI/CD design. Ранее записанные внутренние сведения не считать автоматически разрешёнными к новой публикации.

## Observability и учебные аварии

Roadmap: Prometheus, Grafana, Loki, Alertmanager; постепенно наблюдать Proxmox, LXC, Docker, Traefik, HomeOps, VPN, AdGuard и system resources. HomeOps в будущем экспортирует application metrics. Учебные цели — metrics, logs, alerts, troubleshooting, incident response, SLI и SLO, а не только установка dashboard.

Контролируемые аварии допустимы в отдельно согласованном LAB-упражнении: остановка контейнера, DNS/route/certificate/VPN/database failure, CPU load, заполнение тестового disk. Проверять изоляцию и способ восстановления. Цикл: failure → detection → alert → diagnosis → runbook → recovery. В production не проводить такие эксперименты без прямого решения пользователя. VPN-специфичные проверки остаются в [эксплуатационных правилах VPN](vpn-operations.md).

## Authentication, backup и дальнейшие этапы

После базовой стабильности приложений возможен Authentik или аналогичный Identity Provider: Traefik → Authentication/OIDC → internal services. Для HomeOps позднее рассматриваются OIDC, JWT, RBAC, MFA concepts и audit log; это не текущая функциональность.

Backup полноценен только с проверенным restore. Roadmap: Proxmox Backup Server или эквивалент, retention, verification, restore tests, RPO и RTO. Учебный сценарий только в безопасной LAB-среде по отдельному поручению: удалить test LXC → restore → Ansible → services available → verification.

Forgejo mirror сохраняет Git repository data, но не является полноценным backup Forgejo. Нужен отдельный backup/restore базы, конфигурации, users, Issues, PR, Actions, Releases, Packages, attachments и metadata.

Renovate — будущие контролируемые обновления: PR → CI → review → staging → production. Не включать бесконтрольные production updates.

Kubernetes/K3s не является ближайшей задачей. Сначала уверенно освоить Linux, networking, Git, Docker/Compose, Traefik, CI/CD, Ansible, monitoring, secrets и backups. Затем возможен отдельный K3s LAB для сравнения эксплуатационных свойств Docker Compose и Kubernetes. Рабочую Compose-инфраструктуру сохранять.

## Поэтапный учебный план HomeServer/HomeOps

Отправная точка — существующий HomeOps и реализованная в workflow цепочка tests → publish в GHCR → pull на staging → health checks/условный rollback. Не повторять реализацию Docker pull как новую задачу. Наличие кода не заменяет проверку запуска и освоение механизма. План задаёт порядок обучения без сроков; каждый этап делится на маленькие задачи по [учебному циклу](collaboration.md), а не выполняется Codex автоматически.

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

Это ориентир зависимостей, а не жёсткий waterfall: backend можно развивать между инфраструктурными занятиями. Базовые backup, secrets, минимальные права и диагностика нужны с первого затрагивающего их шага, а не откладываются до номера этапа. До любой миграции проверять восстановление; до controlled actions — authentication, validation и audit. Production не является обязательным результатом ближайшей сессии.

С рабочего ПК без подтверждённого доступа к домашней инфраструктуре выбирать анализ репозитория, проектирование, локальные учебные изменения и доступные GitHub-проверки. Подключения, deployments и аварийные упражнения проводить только при подтверждённом доступе и отдельной согласованной задаче. Перед новой реализацией проверить незавершённые ветки/PR в рамках поручения, чтобы не повторять уже написанную работу.

## Направление интеграций HomeOps

Ориентир, а не поручение реализовать всё: REST API + tests → service monitoring → Docker integration → Traefik integration → Proxmox integration → VPN integration → observability → OIDC/RBAC → audit → controlled actions. Alerts и authentication добавляются постепенно. Реализованную основу отличать от будущих интеграций; Docker/Traefik/Proxmox API сейчас не считать подключёнными.

VPN/control-plane сохраняет [собственную архитектуру](vpn-architecture.md) и [roadmap](vpn-roadmap.md). HomeOps связывает знания, а не заменяет изучение каждого слоя готовой автоматизацией.

Не скрывать обнаруженные проблемы. Предупреждения должны относиться к конкретному действию и его последствиям, а не заменять практическую работу общей памяткой.
