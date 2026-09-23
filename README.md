# ⚡ Event-Driven Analytics & Webhook Engine

Kelayotgan hodisalarni (events) qabul qiladigan, real-vaqtli tahlil qiladigan va ularni tashqi tizimlarga **xavfsiz, ishonchli webhook'lar** orqali tarqatadigan enterprise-grade Python backend tizimi.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat&logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/tests-13%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 "Enterprise-grade" bu yerda nimani anglatadi?

Bu loyiha shunchaki CRUD emas — Stripe, GitHub, Segment kabi kompaniyalar ishlatadigan real webhook infratuzilmasining asosiy patternlarini o'z ichiga oladi:

| Xususiyat | Nega muhim |
|---|---|
| **Async, non-blocking ingestion** | `POST /events` darhol `202 Accepted` qaytaradi — yuqori RPS'da ham kechikish yo'q |
| **HMAC-SHA256 + timestamp imzolash** | Qabul qiluvchi tomon so'rovning haqiqiyligini tekshira oladi, replay-attack'lardan himoyalangan (Stripe uslubi) |
| **Exponential backoff + jitter bilan retry** | Vaqtinchalik xatolarda aqlli qayta urinish, "thundering herd" muammosisiz |
| **Dead-letter tracking** | `max_retries`dan keyingi muvaffaqiyatsiz yetkazishlar kuzatiladi, yo'qolib ketmaydi |
| **Sliding-window real-time analytics** | Oxirgi N soniyalik statistika O(1) evict bilan, xotira sizmasdan |
| **Repository pattern (Dependency Inversion)** | Storage backend'ni (in-memory → Postgres) kodni o'zgartirmasdan almashtirish mumkin |
| **To'liq async test qamrovi (mock HTTP client)** | Real tarmoqqa chiqmasdan retry/backoff/dead-letter stsenariylarini tekshiradi |

To'liq arxitektura tahlili uchun [ARCHITECTURE.md](ARCHITECTURE.md) ga qarang.

## 📂 Loyiha tuzilishi

```
event-engine/
├── event_engine/
│   ├── api/
│   │   └── app.py            # FastAPI REST endpointlar
│   ├── core/
│   │   ├── schema.py         # Event, Subscription, DeliveryAttempt (Pydantic)
│   │   ├── bus.py             # Async EventBus (producer/consumer)
│   │   ├── security.py        # HMAC signing/verification
│   │   └── analytics.py       # Sliding-window real-time analitika
│   ├── storage/
│   │   └── repository.py      # Repository pattern (in-memory implementatsiya)
│   ├── workers/
│   │   └── dispatcher.py      # Webhook dispatcher — retry + backoff
│   └── cli.py
├── tests/
│   ├── test_security.py
│   ├── test_analytics.py
│   └── test_dispatcher.py
├── Dockerfile
├── ARCHITECTURE.md
├── pyproject.toml
└── requirements.txt
```

## 🚀 O'rnatish va ishga tushirish

```bash
git clone https://github.com/<username>/event-engine.git
cd event-engine
pip install -e ".[dev]"

# Serverni ishga tushirish
event-engine --port 8000
# yoki: uvicorn event_engine.api.app:app --reload
```

### Docker orqali

```bash
docker build -t event-engine .
docker run -p 8000:8000 event-engine
```

## 🧑‍💻 API misollari

**Hodisa yuborish:**
```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -d '{"type": "order.paid", "payload": {"amount": 150}, "source": "shop"}'
```

**Webhook obunasi yaratish:**
```bash
curl -X POST http://localhost:8000/v1/subscriptions \
  -H "Content-Type: application/json" \
  -d '{"target_url": "https://yourapp.com/webhook", "event_types": ["order.paid"], "secret": "whsec_..."}'
```

**Real-vaqtli analitika:**
```bash
curl http://localhost:8000/v1/analytics/window
# {"total_events": 42, "events_by_type": {"order.paid": 30, "user.signed_up": 12}, "events_per_second": 0.14}
```

**Webhook imzosini qabul qiluvchi tomonda tekshirish (Python):**
```python
from event_engine.core.security import verify_signature

is_valid = verify_signature(
    secret="whsec_...",
    body=request.body,
    signature_header=request.headers["X-Webhook-Signature"],
)
```

## 🧪 Testlash

```bash
pip install -r requirements.txt
pytest tests/ -v
```

13 ta test: HMAC imzolash/tekshirish, sliding-window analitika, retry/backoff/dead-letter stsenariylari — barchasi mock HTTP client bilan, tarmoqqa chiqmasdan.

## 🔮 Production uchun kengaytirish yo'nalishlari

- [ ] `Repository`ni Postgres/Redis bilan almashtirish
- [ ] `EventBus`ni Kafka yoki RabbitMQ bilan almashtirish (ko'p instance uchun)
- [ ] Prometheus metrikalari (`/metrics` endpoint)
- [ ] Webhook subscription'lar uchun rate limiting
- [ ] Admin dashboard (dead-letter'larni qayta yuborish uchun)

## 📄 Litsenziya

[MIT](LICENSE)
