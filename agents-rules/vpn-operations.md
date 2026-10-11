# VPN Control Plane: эксплуатация и восстановление

Долгосрочные требования к будущей подсистеме; реализация выполняется только по отдельному поручению. Перед работой читать [архитектуру и границы безопасности](vpn-architecture.md).

Multi-node health и failover дополняют прежнюю модель transports. Public/private контуры, network events и независимость egress/backhaul определены в [Network architecture](network-architecture.md); эти требования не разрешают запуск аварийных проверок сейчас.

## Health checks и классификация отказов

Проверка здоровья должна быть многоуровневой, с учётом применимости проверок к конкретному transport:

```text
process/container
        -> interface
        -> VPN handshake
        -> routing
        -> connectivity
        -> HTTPS test
        -> external IP validation
```

Состояние `container running` или `process running` само по себе не доказывает работоспособность transport. Если интернет через него недоступен, он не должен считаться healthy только из-за запущенного контейнера.

Нужно различать как минимум: падение процесса, падение контейнера, отсутствие интерфейса, отсутствие VPN handshake, неработающий маршрут, отсутствие интернета через transport, блокировку отдельных проверок при работающем transport, высокую потерю пакетов и чрезмерную задержку.

Не классифицировать любую ошибку как «блокировку провайдером». Причину определять настолько точно, насколько позволяют наблюдаемые данные; неопределённость сохранять явно.

## Auto-heal, failover и failback

Будущий auto-heal может следовать последовательности: неудачная проверка -> ограниченные повторные проверки -> разрешённый перезапуск transport -> повторная проверка -> failover при сохраняющемся отказе.

Предусмотреть failure threshold, restart attempt limit, cooldown, состояния degraded/blocked, допустимый fallback и recovery probing. Бесконечные циклы перезапуска недопустимы.

Предварительная цепочка failover: использовать AWG, пока он healthy; при отказе переходить на XRay; при отказе обоих применять политику клиента. Например:

Это сохранённый ранний transport-centric вариант. В multi-node target-state policy выбирает node и transport раздельно; отказ одного AWG node не доказывает отказ всех AWG nodes.

- TV: `AWG -> XRay -> DIRECT`.
- Private device: `AWG -> XRay -> BLOCK`.

DIRECT не является универсальным fallback: для клиентов с запретом прямого выхода отказ VPN должен приводить к BLOCK.

После переключения на резервный transport периодически проверять primary. Failback разрешать после recovery threshold, например `N` последовательных успешных probes. Один случайный успешный запрос не должен вызывать возврат на primary.

Health/failover engine должен работать независимо от браузерного UI: недоступность Web UI не должна останавливать мониторинг, auto-heal и переключение маршрутов. Возможная организация: system service / daemon с monitoring, auto-heal, failover и API для UI.

Agent/control daemon на VPN Gateway в перспективе запускается как отдельный systemd service, например с `Restart=on-failure` или иной обоснованной политикой. Перезапуск daemon средствами systemd не заменяет собственный transport failover и ограничения перезапусков.

## Multi-node health и объяснимый failover

Оценивать отдельно node availability, service/process health, применимый VPN handshake, latency, packet loss, external connectivity, ожидаемый public IP и фактическую работоспособность маршрута. Один ping не доказывает node health. Probes должны проходить через проверяемые node/transport, а не случайно через default DIRECT route; иметь bounded timeouts и контекст измерения. Load — дополнительный сигнал выбора, не единственное доказательство здоровья.

Нужны timestamp/last_seen, причина и давность результатов. `healthy`, `degraded`, `unhealthy` и `unknown/stale` — примеры будущего health vocabulary; согласовать его с transport state machine, не смешивая lifecycle, health и routing mode. Например, PL healthy / DE degraded / NL healthy — состояния inventory, не фактическая проверка этих nodes. Пропавшая telemetry не должна оставлять бессрочный healthy.

Сценарий target-state:

1. DE признан unhealthy после настроенных probes/thresholds; сохранить причины и исключить его из eligible routing candidates.
2. Policy evaluation находит разрешённый NL; если candidates отсутствуют, применяется только явно допустимый fallback или BLOCK.
3. Создать событие начала, применить изменение через allowlisted Agent operation, проверить реальный egress route; recorded decision связывает rule/version, old/new node и transport.
4. Записать completion либо failure с причиной; после успешного перехода сохранить route-changed event и отправить уведомление, когда notification layer будет реализован. Отказ уведомления не отменяет работающее переключение.
5. Продолжать recovery probes DE. После recovery threshold вернуть его в available pool; возврат активного трафика на DE — отдельное решение policy/failback с hysteresis/cooldown, не реакция на один успешный ping.

Failover наблюдаем, логируем, объясним и отменяем: предусмотреть отключение automation/manual override, отмену ещё не применённого решения и контролируемый возврат к последнему безопасному маршруту после проверки. Не откатываться слепо на unhealthy node и не ослаблять BLOCK. При провале post-change check сохранять разрешённый безопасный путь или блокировку и явное failure-состояние. Thresholds, recovery/cooldown и restart limits задаются по политике, не бесконечным циклом переключений.

Gateway должен сохранять последнюю валидную конфигурацию и локальную обработку отказов при недоступном браузере, Public Edge или central UI/API; точные degraded behaviours проектируются до включения automation. Это уточняет прежнюю независимость daemon от Web UI. Public Store и Kafka не участвуют в обязательном пути принятия локального routing decision.

## Events, audit и наблюдаемость

Предусмотреть сохранение событий для UI, диагностики, истории проблем, выявления нестабильных transport и будущих уведомлений. Примеры: AWG перешёл в DEGRADED, три проверки завершились неуспешно, AWG перезапущен, недоступность сохранилась, маршрут изменён `AWG -> XRay`, AWG восстановился, маршрут изменён `XRay -> AWG`.

Наблюдаемость развивать итеративно: current state, transport uptime, latency, packet loss, last successful probe, last handshake, restart count, current external IP и failover history. Не добавлять весь набор сразу.

Уведомления, например через Telegram или другие каналы, относятся к поздним этапам. Полезное сообщение содержит отказ, переключение и причину: AWG unavailable; switched AWG -> XRay; connectivity checks failed. Уведомления не входят в первую реализацию.

Общий словарь [Network events и observability](network-architecture.md#observability-network-events-и-ui) связывает node health, route changes и failover с audit, metrics/logs, UI и будущими notifications. Private diagnostics не отправляются в Public HomeOps без transformation/sanitization; выбор Kafka не требуется для первого event log.
