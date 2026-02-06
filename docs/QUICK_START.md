# 🚀 CONNECTIONS MODULE — Quick Start Guide

## Быстрый запуск изолированного модуля Connections

Этот гайд позволяет развернуть **ТОЛЬКО** модуль Connections без остальной платформы (парсинг Twitter, нейронки, Telegram бот и т.д.).

---

## ⚡ TL;DR (5 минут)

```bash
# 1. MongoDB
docker run -d -p 27017:27017 --name connections-mongo mongo:6.0

# 2. Backend
cd /app/backend
yarn install && yarn build
node dist/server-minimal.js &

# 3. Frontend
cd /app/frontend
yarn install && yarn start &

# 4. Проверка
curl http://localhost:8001/api/connections/health

# 5. Открыть в браузере
# http://localhost:3000/connections
```

---

## 📋 Требования

| Компонент | Версия | Обязательно |
|-----------|--------|-------------|
| Node.js | 20+ | ✅ |
| Python | 3.11+ | ✅ |
| MongoDB | 6.0+ | ✅ |
| yarn | 1.22+ | ✅ |

### ❌ НЕ требуется:
- Twitter API keys
- OpenAI/Claude API keys  
- Telegram Bot Token
- Redis
- ML/Neural сервисы

---

## 🔧 Пошаговая установка

### Шаг 1: База данных MongoDB

**Docker (рекомендуется):**
```bash
docker run -d \
  --name connections-mongo \
  -p 27017:27017 \
  mongo:6.0
```

**Проверка:**
```bash
docker ps | grep mongo
# connections-mongo должен быть RUNNING
```

### Шаг 2: Environment Variables

**Backend** (`/app/backend/.env`):
```env
MONGO_URL=mongodb://localhost:27017
MONGODB_URI=mongodb://localhost:27017/connections_db
DB_NAME=connections_db
NODE_ENV=development
PORT=8003
CORS_ORIGINS=*
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
```

### Шаг 3: Backend Setup

```bash
cd /app/backend

# Установка зависимостей
yarn install

# Сборка TypeScript
yarn build

# Проверка сборки
ls -la dist/server-minimal.js
```

### Шаг 4: Запуск Backend

**Вариант A: Через supervisor**
```bash
sudo supervisorctl restart backend
sudo supervisorctl status backend
# Должно быть: backend RUNNING
```

**Вариант B: Вручную**
```bash
# Terminal 1: Node.js Fastify
cd /app/backend
node dist/server-minimal.js

# Terminal 2: Python FastAPI Proxy
cd /app/backend
python server.py
```

### Шаг 5: Frontend Setup

```bash
cd /app/frontend

# Установка зависимостей
yarn install

# Запуск dev server
yarn start
```

**Или через supervisor:**
```bash
sudo supervisorctl restart frontend
```

---

## ✅ Проверка работоспособности

### API Health Checks

```bash
# Main health
curl -s http://localhost:8001/api/health | jq
# Expected: {"ok":true,"service":"fomo-backend","mode":"minimal"}

# Connections health
curl -s http://localhost:8001/api/connections/health | jq
# Expected: {"ok":true,"module":"connections","status":"healthy",...}

# Mock scoring
curl -s http://localhost:8001/api/connections/score/mock | jq
# Expected: Full scoring response with influence, trends, early_signal
```

### Web Interface

| URL | Описание |
|-----|----------|
| http://localhost:3000/connections | Основная страница |
| http://localhost:3000/connections/radar | Early Signal Radar |
| http://localhost:3000/admin/login | Admin login |
| http://localhost:3000/admin/connections | Admin Control Plane |

### Admin Login

```
Username: admin
Password: admin12345
```

---

## 📊 Seed тестовых данных

```bash
# Добавить тестовые аккаунты
curl -X POST http://localhost:8001/api/connections/test/add-audience \
  -H "Content-Type: application/json" \
  -d '{"author_id":"whale_001","handle":"crypto_whale","engaged_user_ids":["u1","u2","u3","u4","u5","u6","u7","u8","u9","u10"]}'

curl -X POST http://localhost:8001/api/connections/test/add-audience \
  -H "Content-Type: application/json" \
  -d '{"author_id":"alpha_001","handle":"alpha_hunter","engaged_user_ids":["u1","u2","u3","u11","u12","u13","u14","u15"]}'

curl -X POST http://localhost:8001/api/connections/test/add-audience \
  -H "Content-Type: application/json" \
  -d '{"author_id":"defi_001","handle":"defi_expert","engaged_user_ids":["u1","u20","u21","u22","u23","u24"]}'

# Проверить
curl -s "http://localhost:8001/api/connections/accounts?limit=10" | jq '.data.items | length'
# Expected: 3
```

---

## 🔔 Запуск Alerts Engine

```bash
# Получить admin token
TOKEN=$(curl -s -X POST "http://localhost:8001/api/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}' | jq -r '.token')

echo "Token: ${TOKEN:0:30}..."

# Запустить batch алертов
curl -s -X POST "http://localhost:8001/api/admin/connections/alerts/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq

# Expected:
# {
#   "ok": true,
#   "data": {
#     "alerts_generated": 4,
#     "alerts_by_type": {...},
#     "accounts_processed": 6
#   }
# }

# Проверить сгенерированные алерты
curl -s "http://localhost:8001/api/admin/connections/alerts/preview" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.summary'
```

---

## 🌐 Режимы работы

### Mock Mode (default)
- Использует тестовые данные
- Не требует внешних API
- Идеально для разработки

### Sandbox Mode
- Ограниченные реальные данные
- Для интеграционного тестирования

### Twitter Live Mode
- Полные реальные данные
- Требует Twitter API credentials
- **НЕ для текущего развёртывания**

**Переключение:** Admin → Connections → Overview → Change Data Source

---

## 🛠 Troubleshooting

### Backend не запускается

```bash
# Проверить логи
tail -f /var/log/supervisor/backend.err.log

# Проверить порты
lsof -i :8001
lsof -i :8003

# Перезапустить
sudo supervisorctl restart backend
```

### MongoDB connection error

```bash
# Проверить MongoDB
docker ps | grep mongo

# Если не запущен
docker start connections-mongo

# Проверить подключение
mongosh mongodb://localhost:27017
```

### Frontend не грузит данные

```bash
# Проверить CORS
curl -I http://localhost:8001/api/connections/health

# Проверить env
cat /app/frontend/.env | grep BACKEND_URL
```

---

## 📁 Структура файлов

```
/app/
├── backend/
│   ├── .env                        # Environment variables
│   ├── package.json                # Dependencies
│   ├── server.py                   # FastAPI proxy
│   └── src/
│       ├── server-minimal.ts       # Minimal entry point ⭐
│       ├── app-minimal.ts          # Minimal app config ⭐
│       └── modules/
│           └── connections/        # Connections module ⭐
│
├── frontend/
│   ├── .env                        # Environment variables
│   ├── package.json                # Dependencies
│   └── src/
│       ├── pages/
│       │   ├── ConnectionsPage.jsx
│       │   ├── ConnectionsEarlySignalPage.jsx
│       │   └── admin/
│       │       └── AdminConnectionsPage.jsx
│       └── config/
│           └── adminNav.registry.js
│
└── docs/
    ├── CONNECTIONS_MODULE.md       # Полная документация
    └── QUICK_START.md              # Этот файл
```

---

## ⚙️ Supervisor Config (для production)

```ini
[program:backend]
command=node /app/backend/dist/server-minimal.js
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log

[program:frontend]
command=yarn start
directory=/app/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
```

---

## 🎯 Следующие шаги

После успешного запуска:

1. **Изучить Admin Control Plane**
   - http://localhost:3000/admin/connections

2. **Протестировать Alerts Engine**
   - Admin → Connections → Alerts → Run Alerts Batch

3. **Протестировать Twitter Score API (Phase 1)**
   ```bash
   # Twitter Score
   curl -s http://localhost:8001/api/connections/twitter-score/mock | jq
   
   # Audience Quality
   curl -s http://localhost:8001/api/connections/audience-quality/mock | jq
   
   # Hops / Social Distance
   curl -s http://localhost:8001/api/connections/hops/mock | jq
   ```

4. **Настроить параметры**
   - Admin → Connections → Config

5. **Мониторить стабильность**
   - Admin → Connections → Stability

6. **Изучить документацию Phase 1**
   - [TWITTER_SCORE_CORE.md](./TWITTER_SCORE_CORE.md)

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [CONCEPT.md](./CONCEPT.md) | Концепция продукта |
| [CONNECTIONS_MODULE.md](./CONNECTIONS_MODULE.md) | Полная документация |
| [TWITTER_SCORE_CORE.md](./TWITTER_SCORE_CORE.md) | **Phase 1: Twitter Score Core** |
| [TELEGRAM_BOT.md](./TELEGRAM_BOT.md) | Telegram Bot документация |
| [QUICK_START.md](./QUICK_START.md) | Этот файл |

---

*Quick Start Guide v1.1*
*Connections Module — Isolated Deployment*
*Updated: 2026-02-06 (Phase 1 complete)*
