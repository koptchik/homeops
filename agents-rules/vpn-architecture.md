# VPN Control Plane / VPN Gateway: архитектура

## Статус направления и границы

HomeOps планируется постепенно расширять как центральный control plane для части домашней инфраструктуры. Одна из будущих подсистем, **VPN Control Plane**, предназначена для наблюдения и последующего управления отдельным домашним VPN Gateway.

В общем направлении [HomeServer](infrastructure-security.md) HomeOps остаётся самостоятельным приложением, а VPN/control-plane компоненты могут оставаться отдельными repositories. Этот документ регулирует VPN-домен, а не общую инфраструктуру HomeServer.

Общие контуры, Edge, backhaul, DNS и public/private boundaries задаёт [Network architecture](network-architecture.md). Все управление, inventory и диагностические данные этого VPN-документа относятся к private HomeOps Core; наружу может выходить только разрешённая Public Projection.

**Документы о VPN фиксируют долгосрочную идею и roadmap, а не поручение реализовать их сейчас.** Примеры структуры, API, сетевых таблиц и параметров описывают возможный дизайн; они не являются командами к выполнению или окончательными контрактами.

Существующие архитектура, каталоги, API, модели, тесты, Docker-настройки, CI/CD и staging/deploy workflow сохраняются. Новое направление дополняет [общие правила проекта](../AGENTS.md) и не отменяет их. Каждая будущая реализация требует отдельной согласованной задачи; наличие roadmap само по себе не разрешает менять код или инфраструктуру.

В целевой архитектуре HomeOps выполняет роли control plane, интерфейса управления, мониторинга, хранения конфигурации и состояния, отображения здоровья инфраструктуры, а позднее автоматизации и failover. Эти VPN-роли ещё не реализованы. HomeOps не становится VPN-движком: низкоуровневое управление сетью остаётся на VPN Gateway.

## VPN Gateway и HomeOps Agent

Предполагается отдельный LXC-контейнер Proxmox с ролью VPN Gateway. Конкретный внутренний адрес хранится в приватном inventory владельца. Наличие справочной информации не является разрешением на подключение или изменение узла.

Для шлюза предполагаются или предварительно подготовлены `/dev/net/tun`, Linux IP forwarding, Docker, `NET_ADMIN`, userspace VPN implementations, AmneziaWG, XRay, `nftables` и `iproute2`. Их фактическая готовность должна проверяться при отдельно согласованной работе с инфраструктурой.

Предпочтительная схема:

```text
HomeOps
   |
   | authenticated API
   v
homeops-agent (на VPN Gateway LXC)
   |
   +-- Docker
   +-- routing / routes / ip rule
   +-- nftables
   +-- AmneziaWG
   +-- XRay
   +-- health checks
```

`homeops-agent` планируется как отдельный лёгкий компонент непосредственно на управляемом узле. Он собирает локальное состояние, возвращает его HomeOps и выполняет только заранее определённые разрешённые операции. Он изолирует центральный backend от прямого root-доступа к инфраструктуре.

Принцип взаимодействия: `HomeOps -> controlled Agent API -> whitelisted operations`. Агент использует allowlist операций и допустимых целей. Например, `restart_transport("awg-out")` означает конкретную разрешённую операцию над известным transport, а не выполнение переданной пользователем shell-команды.

Для controlled operations обязательны validation параметров, least privilege, audit, health checks и предусмотренный rollback. Эксплуатационные подробности находятся в [правилах VPN](vpn-operations.md).

Схемы `HomeOps -> SSH root -> arbitrary commands` и `HomeOps -> exposed Docker socket` не являются целевой архитектурой. Не предоставлять HomeOps неограниченный удалённый shell ради управления шлюзом.

## Transports, inbound и outbound

Проектировать поддержку нескольких транспортов с возможностью дальнейшего расширения:

| Логическое имя | Назначение |
| --- | --- |
| `DIRECT` | Прямой выход в интернет |
| `AWG_OUT` | AmneziaWG через внешний VPN/VPS |
| `XRAY_OUT` | XRay / REALITY через внешний VPS |

Каждый transport имеет состояние. Предварительная модель: `DISABLED`, `STARTING`, `UP`, `DEGRADED`, `BLOCKED`, `DOWN`, `RECOVERING`. Точные enum, смысл состояний и переходы проектируются при реализации; состояние transport и режим маршрутизации клиента являются отдельными понятиями.

VPN Gateway должен в перспективе совмещать две роли:

- **Inbound:** принимать VPN-соединения доверенных устройств, например телефона через AmneziaWG.
- **Outbound:** выбирать дальнейший выход трафика через `DIRECT`, `AWG_OUT` или `XRAY_OUT` по политикам шлюза. Inbound-подключение не предопределяет outbound transport.

```text
Remote device
      |
      | stable inbound VPN
      v
Home VPN Gateway
      |
      +-- DIRECT ----------> Internet
      +-- AWG OUT ---------> VPS -> Internet
      +-- XRay OUT --------> VPS -> Internet
```

Предпочтительная модель: стабильный inbound для мобильных и других клиентов, динамическая outbound-маршрутизация на шлюзе. Переключение между DIRECT, AWG OUT и XRay OUT не должно требовать изменения VPN-конфигурации телефона.

## VPN nodes и Network Policy

Прежняя схема DIRECT/AWG/XRay описывает выбор transport и сохраняется как исходный дизайн. Multi-VPS target-state добавляет независимый выбор egress node: `Client → Home VPN Gateway → Policy Engine → DIRECT или (VpnNode + transport) → Internet`. Несколько nodes могут поддерживать один transport, а один node — несколько transports. Стабильный inbound доверенных клиентов остаётся отдельной ролью и не смешивается с egress или infrastructure backhaul.

Gateway отвечает за routing/policy routing, direct/VPN paths, выбор node, client/device/group и domain/network policies, health-based selection, failover, rules, telemetry и интеграцию с HomeOps через Agent. Он не отправляет весь Home LAN через VPN по умолчанию. Количество nodes и набор стран динамические; `vpn-pl`, `vpn-de`, `vpn-nl`, `vpn-fi`, `vpn-ch` — примеры, не enum и не обязательный inventory.

### VpnNode как инфраструктурная сущность

Проектировать модель в рамках актуальной архитектуры приложения, не копировать список полей в таблицу БД автоматически:

| Группа | Возможные поля | Смысл и границы |
| --- | --- | --- |
| Identity / placement | `id`, `name`, `region`, `country`, `provider` | Стабильная identity и metadata; provider/region не определяют класс приложения |
| Connectivity | `endpoint`, `public_ip`, `capabilities` | Endpoint и поддерживаемые transports/features; public IP может быть наблюдаемым значением, отличным от configured endpoint |
| Desired configuration | `enabled`, `priority` | Намерение оператора; выключенный node не становится доступным для выбора из-за успешного ping |
| Observed state | `status`, `health_state`, `latency`, `packet_loss`, `load`, `last_seen` | Состояние, качество пути и давность; неизвестное значение не равно нулю или healthy |

При реализации уточнить границу operational status / computed health и не хранить два противоречащих источника истины. Измерения имеют timestamp, units и контекст path/transport; telemetry не обязана лежать в одной записи с desired configuration. Credentials хранятся отдельно от inventory по secrets rules.

Модель: `VpnNode + Provider + Region + Capabilities`, не `H1CloudNode`. H1Cloud — текущий план, но одновременно должны быть возможны Hetzner, другой VPS provider и self-hosted node. Provider adapters появляются только при реальной интеграции; ядро policies не зависит от конкретного provider SDK.

### Network Policy

Форма правила: `device/group + destination/domain/network (+ service при известной идентичности) + action`. Target примеры:

| Match | Action |
| --- | --- |
| Client A | DIRECT |
| Client B | Предпочитать разрешённые VPN nodes региона EU |
| Domain X | Выбранный VPN-DE node |
| Network Y | DIRECT |
| Service Z | VPN-NL, если Gateway может достоверно сопоставить трафик сервису |

Предусмотреть priorities, deterministic ordering, явный default policy, допустимый fallback, audit и read-only dry-run/evaluation mode. При равных priorities нужен стабильный tie-breaker (например, rule ID); направление сортировки, first-match/иная семантика и разрешение конфликтов фиксируются и проверяются до применения. Никакого случайного выбора по порядку выдачи inventory.

Решение должно объяснять matched rule, версию policies, eligible candidates, исключённые nodes с причиной, выбранные node/transport и fallback. Сначала фильтровать `enabled`, capabilities, policy constraints и health/freshness; затем применять предпочтения и детерминированный выбор. Метрика latency сама по себе не отменяет запрет выхода DIRECT или требование определённого региона.

Default policy и исчерпание candidates задаются явно для класса клиентов. DIRECT допустим только по политике; для запрета прямого выхода используется BLOCK. Смена node/transport выполняется контролируемо через Agent с validation, audit, post-change route check и безопасным rollback. Dry-run возвращает объяснение без изменения маршрутов.

Доменные policies опираются на DNS/IP mapping, рассматриваемый ниже. При реализации учитывать TTL, shared/CDN addresses, IPv4/IPv6 и clients с альтернативным DNS: один домен не всегда равен одному уникальному IP. Возможные ограничения точности объяснять пользователю; не обещать корректность domain policy одним сопоставлением имени.

## Policy routing

Будущее управление политиками выполняется через Agent API на VPN Gateway. Предполагаемая Linux-механика: `nftables`, packet marks, `ip rule` и отдельные routing tables.

Концептуальные соответствия, не готовая конфигурация и не инструкция выполнять команды:

Следующая таблица — сохранённый пример прежней transport-centric модели. В multi-node target-state конкретные tables/marks проектируются под пары node/transport и обратный трафик; числа 200/300 не ограничивают количество nodes. Egress и backhaul не используют одну общую routing table как неявный канал доступа домой.

| Направление | Routing table | Packet mark |
| --- | --- | --- |
| DIRECT | `main` | `0x10` |
| AWG | `200` | `0x20` |
| XRay | `300` | `0x30` |

Предполагаемые логические режимы маршрутизации:

- `DIRECT`: обычный прямой выход в интернет.
- `VPN`: принудительный выход через выбранный VPN transport.
- `AUTO`: маршрут определяется политиками.
- `BLOCK`: блокировать трафик вместо fallback в DIRECT, чтобы исключить прямые утечки для соответствующих клиентов.

Политики должны учитывать отдельные устройства. Примеры: `Android -> AUTO`, `Laptop -> VPN`, `TV -> AUTO`, `Server -> DIRECT`. Возможные идентификаторы: IP, VPN client ID, внутренний VPN-адрес или другая безопасная идентичность. Точная модель идентификации пока не зафиксирована.

Возможны политики назначения: локальные сети напрямую, определённые назначения через VPN, остальное напрямую; либо одни назначения через AWG, другие через XRay.

Linux routing работает с IP, а не непосредственно с доменными именами. Доменные правила могут потребовать отдельного механизма:

```text
DNS -> resolved IP sets -> nftables sets -> routing marks
```

В домашней инфраструктуре уже есть отдельный AdGuard Home. Возможная интеграция DNS и policy routing рассматривается позднее и не входит в текущее изменение документации.

Это ранее зафиксированный infrastructure context, не свежая проверка. Эволюция DNS и её границы теперь описаны в [Network architecture](network-architecture.md#internal-ingress-dns-и-naming): AdGuard сохраняется на начальном этапе, Technitium остаётся кандидатом; DNS integration не означает миграцию сейчас.

## Backend, данные и API

Основной backend продолжает использовать FastAPI. VPN-функциональность добавляется модульно, согласуется с архитектурой проекта на момент реализации и не ломает существующий backend.

Пример возможной будущей структуры, без требования создавать эти файлы сейчас:

```text
backend/app/
  routers/
    vpn.py
  services/
    vpn/
      health.py
      transports.py
      routing.py
      agent.py
  models/
    vpn.py
```

Для первого этапа системы управления предпочтительно рассматривать SQLite. Потенциальные сущности: `devices`, `transports`, `routing_policies`, `health_checks`, `events`, `failover_events`, `settings`. Таблицы, связи и миграции проектировать только на соответствующем этапе реализации.

Для multi-node этапа добавить концепцию `vpn_nodes` и связи node/transport/policy; это расширение предыдущего списка, не готовая DB schema. SQLite остаётся прежним кандидатом первого management layer; будущий PostgreSQL относится к private environment. Public Store имеет отдельную роль и не является репликой administrative database.

Примеры будущего API, не утверждённые контракты и не задача на создание endpoints:

```text
GET  /api/vpn/status
GET  /api/vpn/transports
GET  /api/vpn/routes
GET  /api/vpn/devices
POST /api/vpn/transports/{name}/restart
POST /api/vpn/mode/{mode}
```

## Web UI

В перспективе HomeOps получает разделы VPN Dashboard, Transports, Devices, Routing Rules, Health, Events, Failover и Settings.

В общем target-state эти страницы входят в [Network UI](network-architecture.md#observability-network-events-и-ui), где добавляются Nodes, DNS, Edge, Traffic и topology из нормализованных данных. VPN dashboard должен показывать выбранные node и transport раздельно; существующий transport dashboard остаётся полезным первым шагом.

Dashboard должен показывать состояние DIRECT, AWG и XRay, активный маршрут в соответствующем контексте политики, latency, packet loss, последнее успешное соединение, последнее состояние transport, причину ошибки, время последнего переключения и failover state.

Пример логической панели: `DIRECT: UP`, `AWG: UP`, `XRAY: DEGRADED`, активный маршрут `AWG`, цепочка failover `AWG -> XRay -> DIRECT` для политики, допускающей прямой выход.

UI отображает состояние и вызывает backend; непосредственная логика управления сетью в UI не размещается:

```text
Web UI -> FastAPI -> service layer -> agent/API -> VPN Gateway
```

## Изменение параметров обходных транспортов

В долгосрочной перспективе возможна автоматизация смены порта, некоторых AWG-параметров, отдельных XRay-настроек и выбора transport. Такие изменения допустимы только при возможности согласованно настроить обе стороны соединения, например Home Gateway и управляемый VPS.

Нельзя автоматически менять inbound-конфигурацию сервера, если удалённые мобильные клиенты не получили соответствующую конфигурацию. Стабильный inbound и изменяемый outbound остаются предпочтительным разделением ответственности.

## Безопасность и окружения

VPN Control Plane потенциально управляет Docker, firewall, маршрутизацией, VPN, сетевыми namespace и привилегированными системными операциями. При проектировании обязательны следующие границы:

- Запрет произвольного shell через HTTP. API вида `POST /run-command` с пользовательским полем `command` недопустим; использовать только заранее определённые операции с проверенными параметрами и целями.
- Docker socket не выставлять наружу по сети.
- Применять least privilege и практически разумное разделение HomeOps frontend, HomeOps backend, Agent и privileged system operations.
- Agent API должен требовать надёжную аутентификацию. Возможные варианты: API token, mTLS, signed requests или private network с credentials. Окончательную модель выбрать отдельным проектированием; наличие частной сети само по себе не заменяет аутентификацию.
- Хранение secrets подчиняется [правилам инфраструктуры и secrets](infrastructure-security.md); реальные ключи и конфигурации с секретами не помещать в репозиторий.

Разделять локальную разработку, lab, staging и production по [назначению окружений](infrastructure-security.md). Существующий staging не должен автоматически получать права управления реальным VPN Gateway. По возможности использовать mock agent, test agent, безопасное тестовое окружение либо ограниченный read-only доступ. Не передавать staging root/control доступ к реальной сетевой инфраструктуре просто для проверки новой функции.

## Будущее расширение HomeOps

При проектировании Agent учитывать возможность дальнейших управляемых узлов: VPN Gateway Agent, Net Services Agent, Proxmox Agent и Backup Agent. Не создавать универсальную платформу заранее: сначала решать текущую реальную задачу, сохраняя возможность дальнейшего расширения без архитектурных тупиков.

Смежные документы: [эксплуатация и восстановление](vpn-operations.md), [этапы развития](vpn-roadmap.md).
