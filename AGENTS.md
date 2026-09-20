# HomeOps — инструкции проекта

HomeOps — рабочий учебный DevOps pet-проект на FastAPI для домашней инфраструктуры Proxmox/LXC. Проект развиваем небольшими проверяемыми шагами с объяснением кода и архитектурных решений.

## Цели

Цель — за двухнедельный учебный цикл собрать работающий DevOps pet-проект с понятным pipeline:

```text
VS Code → Git → GitHub → CI/tests → Docker build → registry
                                               → staging в LXC на Proxmox
                                               → health check / rollback
```

Изучаем Git, GitHub, GitHub Actions, Python/pytest, Docker, registry/GHCR, Linux, LXC, Proxmox и практику CI/CD через реальные действия.

Долгосрочное направление — VPN Control Plane: мониторинг и последующее управление отдельным VPN Gateway через контролируемый HomeOps Agent API. Это roadmap для будущих согласованных задач, а не поручение на реализацию.

## Правила работы

Инструкции в `agents-rules/` являются частью правил проекта. До начала работы прочитать обязательные файлы ниже; тематические файлы читать перед действиями по соответствующей теме. Прямое поручение пользователя определяет объём текущей задачи.

| Файл | Когда читать |
| --- | --- |
| [Взаимодействие и обучение](agents-rules/collaboration.md) | Всегда: роль, полномочия, темп и объяснения |
| [Проверки и Git](agents-rules/workflow.md) | Всегда: актуальное состояние, ветки и изменения файлов |
| [Инфраструктура и secrets](agents-rules/infrastructure-security.md) | Всегда: окружение и безопасность секретов |
| [Поддержка инструкций](agents-rules/documentation.md) | При изменении или дополнении правил проекта |
| [Тестирование и deployment](agents-rules/testing-deployment.md) | При работе с тестами, CI/CD, deployment и rollback |
| [Очистка Docker](agents-rules/docker-cleanup.md) | При анализе или изменении очистки образов и тегов |
| [Архитектура VPN](agents-rules/vpn-architecture.md) | При любой работе с направлением VPN, Agent и маршрутизацией |
| [Эксплуатация VPN](agents-rules/vpn-operations.md) | При работе с health checks, auto-heal, failover и наблюдаемостью |
| [VPN roadmap](agents-rules/vpn-roadmap.md) | При планировании этапов развития VPN-модуля |
