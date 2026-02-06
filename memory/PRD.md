# Connections Module - PRD

## Оригинальное требование
Развернуть проект Connections Module с GitHub (https://github.com/svetlanaslinko057/555768), следуя инструкциям репозитория. Изолированный модуль для справедливого рейтинга инфлюенсеров.

## Архитектура

### Технологический стек
- **Backend**: Node.js 20+ (Fastify/TypeScript) + Python FastAPI proxy
- **Frontend**: React 19 + Tailwind CSS
- **Database**: MongoDB 6.0+
- **Порты**: FastAPI (8001), Fastify (8003), Frontend (3000)

### Структура
```
/app/
├── backend/
│   ├── src/
│   │   ├── server-minimal.ts      # Entry point
│   │   ├── app-minimal.ts         # App config
│   │   └── modules/connections/   # Connections Module
│   └── server.py                  # FastAPI proxy
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── ConnectionsPage.jsx
│       │   ├── ConnectionsEarlySignalPage.jsx
│       │   └── admin/AdminConnectionsPage.jsx
│       └── components/connections/
└── docs/
    ├── CONCEPT.md
    ├── CONNECTIONS_MODULE.md
    └── QUICK_START.md
```

## Персоны пользователей
1. **Трейдеры/Инвесторы** — поиск "восходящих звёзд" до массового внимания
2. **Маркетологи** — выбор инфлюенсеров с реальной аудиторией
3. **Аналитики** — мониторинг динамики влияния

## Основные функции

### ✅ Реализовано
- **Influence Scoring** — качество влияния (Base + Adjusted)
- **Trend Analysis** — Velocity + Acceleration метрики
- **Early Signal Detection** — Breakout/Rising детекция
- **Risk Detection** — Уровни риска (low/medium/high)
- **Alerts Engine** — Генерация алертов (preview режим)
- **Admin Control Plane** — Управление модулем
- **Mock Mode** — Работа без Twitter API

### Режимы работы
- **Mock** (текущий) — тестовые данные
- **Sandbox** — ограниченные реальные данные
- **Twitter Live** — полные данные (требует API keys)

## Что реализовано (2026-02-06)

### P0 - Backend Core (ЗАВЕРШЁН ✅)
- [x] FastAPI proxy → Node.js Fastify
- [x] Connections Module API endpoints
- [x] Admin authentication (JWT)
- [x] MongoDB подключение
- [x] Mock data generation

### P1 - Graph как Продукт (ЗАВЕРШЁН ✅)
- [x] **Filter Modal** (schema-driven) — фильтрация по profile, early signal, risk level
- [x] **Suggestions Panel** ("Explore Suggestions") — 5 рекомендаций с причинами
- [x] **Node Details Panel** — клик по ноде → влияние, сигнал, связи
- [x] **Compare из графа** — кнопка "Compare with..." → выбор второго аккаунта → сравнение
- [x] **Ranking Table** — Top 10 инфлюенсеров, синхронизация с графом
- [x] **Навигация** — Influencers | Graph | Radar табы

### Frontend Pages
- [x] `/connections` — список инфлюенсеров
- [x] `/connections/graph` — Force Graph визуализация с фильтрами
- [x] `/connections/radar` — Early Signal визуализация
- [x] `/admin/connections` — Admin Control Plane

### API Endpoints
- `GET /api/connections/health`
- `GET /api/connections/accounts`
- `POST /api/connections/score`
- `POST /api/connections/early-signal`
- `GET /api/admin/connections/overview`

## Приоритеты (Backlog)

### P0 - Backend Core — ✅ ЗАВЕРШЁН

### P1 - Graph как Продукт — ✅ ЗАВЕРШЁН

### P2.1 - Telegram Delivery (ЗАВЕРШЁН ✅)
- [x] Telegram Bot (@t_fomo_bot) подключен
- [x] Admin UI для управления доставкой
- [x] Типы алертов: Early Breakout, Strong Acceleration, Trend Reversal
- [x] Cooldown настройки (24h/12h)
- [x] Test Message / Dispatch Pending функции
- [x] History и Stats API

### P2.2 - Share / Persist Graph State (ЗАВЕРШЁН ✅)
- [x] Backend API: encode/decode state (base64-url-safe)
- [x] Frontend: state restore from URL (?state=...)
- [x] Share Button с копированием URL
- [x] Telegram → Open in Graph ссылки
- [x] Version control (GraphState v1.0)

### P2 - Интеграции
- [ ] Twitter API интеграция (переключение Mock → Twitter Live)
- [ ] Telegram Delivery для алертов
- [ ] Discord Webhooks

### P3 - Аналитика
- [ ] Historical Data Storage
- [ ] ML-enhanced Scoring
- [ ] Prediction Models

### P4 - Расширение
- [ ] Cross-platform (Reddit, Telegram channels)
- [ ] Export/Share функциональность

## Credentials
- **Admin**: admin / admin12345

## Ссылки
- Документация: /app/docs/
- GitHub: https://github.com/svetlanaslinko057/555768
