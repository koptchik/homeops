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

Подтверждаемое по файлам состояние HomeOps описано в [README](README.md); детали существующего pipeline и его отличия от целевого — в [правилах CI/CD](agents-rules/testing-deployment.md). Наличие конфигурации не доказывает текущее здоровье инфраструктуры.

Порядок дальнейшего обучения и критерии перехода между этапами находятся в [поэтапном плане](agents-rules/infrastructure-security.md#поэтапный-учебный-план-homeserverhomeops); ближайшая работа — в [учебных шагах CI/CD](agents-rules/testing-deployment.md#ближайшие-учебные-шаги). Это ориентир совместной работы, а не разрешение на автоматическую реализацию.

## Правила работы

Инструкции в `agents-rules/` являются частью правил проекта. До начала работы прочитать обязательные файлы ниже; тематические файлы читать перед действиями по соответствующей теме. Прямое поручение пользователя определяет объём текущей задачи.

| Файл | Когда читать |
| --- | --- |
| [Взаимодействие и обучение](agents-rules/collaboration.md) | Всегда: роль, полномочия, темп и объяснения |
| [Проверки и Git](agents-rules/workflow.md) | Всегда: актуальное состояние, ветки и изменения файлов |
| [Инфраструктура и secrets](agents-rules/infrastructure-security.md) | Всегда: границы HomeServer/HomeOps, инфраструктурная архитектура, roadmap и безопасность |
| [Поддержка инструкций](agents-rules/documentation.md) | При изменении или дополнении правил проекта |
| [Тестирование и deployment](agents-rules/testing-deployment.md) | При работе с тестами, CI/CD, deployment и rollback |
| [Очистка Docker](agents-rules/docker-cleanup.md) | При анализе или изменении очистки образов и тегов |
| [Архитектура VPN](agents-rules/vpn-architecture.md) | При любой работе с направлением VPN, Agent и маршрутизацией |
| [Эксплуатация VPN](agents-rules/vpn-operations.md) | При работе с health checks, auto-heal, failover и наблюдаемостью |
| [VPN roadmap](agents-rules/vpn-roadmap.md) | При планировании этапов развития VPN-модуля |
