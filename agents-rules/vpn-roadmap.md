# VPN Control Plane: roadmap

Долгосрочное направление описано в [архитектуре VPN](vpn-architecture.md); требования к мониторингу и восстановлению находятся в [эксплуатационной модели](vpn-operations.md).

## Учебный процесс и roadmap

VPN-модуль развивается по [правилам обучения](collaboration.md), [работы с Git и проверками](workflow.md) и [тестирования и deployment](testing-deployment.md): объяснять код и архитектурные решения, двигаться небольшими проверяемыми шагами, тестировать каждый реализуемый слой и проводить изменения через отдельные feature branches. Пользователь должен понимать, что и зачем добавляется. Не генерировать сразу большой объём реализации, не переписывать проект целиком ради модуля и не выполнять за пользователя несогласованные действия.

Примерный порядок будущих этапов:

1. VPN domain models / API design.
2. Read-only VPN status.
3. HomeOps Agent prototype.
4. HomeOps <-> Agent communication.
5. Docker transport monitoring.
6. AWG health monitoring.
7. Routing status.
8. Web dashboard.
9. Controlled transport operations.
10. nftables / ip rule integration.
11. AWG outbound.
12. XRay outbound.
13. Policy routing.
14. Health state machine.
15. Failover.
16. Failback.
17. Auto-heal.
18. Notifications.
19. Additional nodes / transports.

Это ориентир, который можно корректировать по мере обучения, уточнения зависимостей и развития проекта. Он не разрешает автоматически создавать ветки, файлы, задачи реализации или менять инфраструктуру.
