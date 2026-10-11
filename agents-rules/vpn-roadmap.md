# VPN Control Plane: roadmap

Долгосрочное направление описано в [архитектуре VPN](vpn-architecture.md); требования к мониторингу и восстановлению находятся в [эксплуатационной модели](vpn-operations.md).

Это доменная детализация [Network roadmap HomeServer](network-architecture.md#поэтапное-развитие-network), где отдельно развиваются internal ingress/DNS, Edge/backhaul и Public Projection. VPN control остаётся private; public showcase получает только очищенные данные.

## Учебный процесс и roadmap

VPN-модуль развивается по [правилам обучения](collaboration.md), [работы с Git и проверками](workflow.md) и [тестирования и deployment](testing-deployment.md): объяснять код и архитектурные решения, двигаться небольшими проверяемыми шагами, тестировать каждый реализуемый слой и проводить изменения через отдельные feature branches. Пользователь должен понимать, что и зачем добавляется. Не генерировать сразу большой объём реализации, не переписывать проект целиком ради модуля и не выполнять за пользователя несогласованные действия.

Первоначальный transport-centric порядок будущих этапов (сохранён как история проектирования; актуальные уточнения для multi-node — ниже):

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

## Эволюция к multi-node target-state

Прежний пункт 19 откладывал дополнительные nodes до конца transport roadmap. Теперь несколько nodes и их health нужны до автоматического выбора/failover. Это изменение порядка обучения, не утверждение, что прежние этапы выполнены. AWG/XRay остаются вариантами transports; расширение их набора не является обязательной предпосылкой нескольких VPS.

| Область прежнего плана | Уточнённый учебный шаг | Проверяемый результат |
| --- | --- | --- |
| Domain models, read-only status, Agent, communication | Учесть VpnNode, Provider, Region, Capabilities и разделение desired/observed state; начать с одного node и одного transport | Inventory/status объясняют данные; authenticated read-only Agent не даёт произвольный shell |
| Routing status, outbound, controlled operations | Отдельный Gateway, один egress, ручные policies; сохранять inbound/backhaul раздельно | Пользователь проверяет DIRECT/VPN/BLOCK и маршрут, затем малую allowlisted operation с audit/rollback |
| Additional nodes, monitoring, health state | Ввести динамический multi-node inventory и probes до automatic selection | Узлы и transports различаются; availability/handshake/connectivity/public IP/latency/loss показывают фактический путь |
| Policy routing, failover/failback/auto-heal | Deterministic rule ordering, dry-run, default/fallback, затем health-based selection и bounded recovery | Объяснимый выбор, отмена, отсутствие запрещённого DIRECT, проверенные thresholds и recovery |
| Dashboard, events, notifications, расширение | Встроить VPN в Network UI/observability; добавлять новые nodes/transports по потребности | UI показывает node/transport отдельно, audit объясняет переходы; notifications и public data используют свои границы |

Базовые health/events появляются вместе с соответствующим routing шагом, а не откладываются до полного observability stack. Edge/backhaul не реализуются как ещё один VPN outbound; их этапы находятся в общем Network roadmap. Kafka не является prerequisite для VPN-модуля.
