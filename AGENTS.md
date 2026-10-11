# HomeOps — инструкции проекта

HomeOps — рабочий учебный DevOps pet-проект на FastAPI для домашней инфраструктуры Proxmox/LXC. Проект развиваем небольшими проверяемыми шагами с объяснением кода и архитектурных решений.

## Цели

**HomeServer/HomeOps — прежде всего долгосрочная учебная площадка для последовательного освоения backend-разработки, Linux, сетей, Docker, CI/CD, DevOps, observability, security, Infrastructure as Code и эксплуатации инфраструктуры.** Понимание и самостоятельная практика пользователя важнее скорости, автоматизации и полноты реализации. Codex — наставник, а не автономный разработчик проекта; полномочия и учебный цикл определены в [правилах взаимодействия](agents-rules/collaboration.md).

Практическая цель — собрать работающий проект с понятным pipeline без фиксированного срока завершения. Целевая цепочка:

```text
VS Code → Git → GitHub → CI/tests → Docker build → registry
                                               → staging в LXC на Proxmox
                                               → health check / rollback
```

Изучаем Git, GitHub, GitHub Actions, Python/pytest, Docker, registry/GHCR, Linux, LXC, Proxmox и практику CI/CD через реальные действия.

HomeOps остаётся самостоятельным приложением и постепенно развивается в control plane домашней инфраструктуры. HomeServer — целевой верхнеуровневый infrastructure/meta repository, а не новое имя или замена HomeOps. Его архитектура и общий roadmap находятся в [инфраструктурных правилах](agents-rules/infrastructure-security.md). VPN Control Plane остаётся отдельным направлением: мониторинг и последующее управление VPN Gateway через контролируемый Agent API. Roadmap не является поручением на реализацию.

Целевая [Network-архитектура HomeServer](agents-rules/network-architecture.md) связывает private network, internal ingress/DNS, multi-VPS VPN, отдельные backhaul и Public Edge, а также HomeOps Core и read-only Public HomeOps через sanitized Public Projection. Это направление последовательного изучения DevOps/SRE, сетей и event-driven систем, а не поручение внедрять компоненты. Private control plane остаётся private; детали, эволюция решений и Network roadmap находятся в этом тематическом документе.

Самостоятельный проект [HomeMemory / Knowledge Platform](agents-rules/homememory.md) внутри HomeServer — долговременная память для человека и AI-агентов: Markdown + Git, совместимый с Obsidian vault, поиск по знаниям и read-only MCP. HomeMemory сохраняет архитектуру, решения, планы и полезные итоги сессий между контекстными окнами. Его реализация и сопровождение ведутся отдельно от HomeOps, в собственном репозитории и по собственному roadmap; HomeOps — возможный клиент его read-only интерфейса. Это будущая часть архитектуры и roadmap; основная цель остаётся прежней — обучение через реально используемую домашнюю инфраструктуру и портфолио.

Подтверждаемое по файлам состояние HomeOps описано в [README](README.md); детали существующего pipeline и его отличия от целевого — в [правилах CI/CD](agents-rules/testing-deployment.md). Наличие конфигурации не доказывает текущее здоровье инфраструктуры.

Порядок зависимостей и критерии освоения находятся в [поэтапном плане](agents-rules/infrastructure-security.md#поэтапный-учебный-план-homeserverhomeops). Ближайшую тему выбирать по последним релевантным обсуждениям, фактическому состоянию, интересу пользователя и [правилам чередования тем](agents-rules/collaboration.md#чередование-тем-и-точки-продолжения). [Учебные шаги CI/CD](agents-rules/testing-deployment.md#ближайшие-учебные-шаги) сохраняются для продолжения этого направления; они не являются обязательной следующей задачей каждой сессии. Минимальная документальная основа HomeMemory имеет высокий ближайший приоритет как [параллельное направление](agents-rules/homememory.md#ближайший-параллельный-приоритет) рядом с выбранной практической темой. Roadmap не разрешает автоматическую реализацию.

## Правила работы

Инструкции в `agents-rules/` являются частью правил проекта. До начала работы прочитать обязательные файлы ниже; тематические файлы читать перед действиями по соответствующей теме. Прямое поручение пользователя определяет объём текущей задачи.

| Файл | Когда читать |
| --- | --- |
| [Взаимодействие и обучение](agents-rules/collaboration.md) | Всегда: роль, полномочия, темп и объяснения |
| [Проверки и Git](agents-rules/workflow.md) | Всегда: актуальное состояние, ветки и изменения файлов |
| [Инфраструктура и secrets](agents-rules/infrastructure-security.md) | Всегда: границы HomeServer/HomeOps, инфраструктурная архитектура, roadmap и безопасность |
| [Network-архитектура](agents-rules/network-architecture.md) | При работе с сетью, ingress, DNS, VPN, Edge, Public HomeOps, network events и их roadmap |
| [Поддержка инструкций](agents-rules/documentation.md) | При изменении или дополнении правил проекта |
| [HomeMemory / Knowledge Platform](agents-rules/homememory.md) | При работе с памятью проекта, Markdown-vault, итогами сессий, импортом знаний, RAG, MCP и roadmap этого направления |
| [Тестирование и deployment](agents-rules/testing-deployment.md) | При работе с тестами, CI/CD, deployment и rollback |
| [Очистка Docker](agents-rules/docker-cleanup.md) | При анализе или изменении очистки образов и тегов |
| [Архитектура VPN](agents-rules/vpn-architecture.md) | При любой работе с направлением VPN, Agent и маршрутизацией |
| [Эксплуатация VPN](agents-rules/vpn-operations.md) | При работе с health checks, auto-heal, failover и наблюдаемостью |
| [VPN roadmap](agents-rules/vpn-roadmap.md) | При планировании этапов развития VPN-модуля |
