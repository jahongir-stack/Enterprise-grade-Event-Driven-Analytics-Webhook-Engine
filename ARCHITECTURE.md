# Arxitektura

## Umumiy oqim

```
                 POST /v1/events (202 Accepted)
                          │
                          ▼
                   ┌─────────────┐
                   │  EventBus   │  asyncio.Queue — backpressure bilan
                   │ (producer/  │
                   │  consumer)  │
                   └──────┬──────┘
                          │ fan-out (3 ta mustaqil subscriber)
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
    ┌─────────────┐ ┌───────────┐ ┌──────────────┐
    │ Repository  │ │ Analytics │ │  Dispatcher   │
    │ (persist)   │ │  Engine   │ │  (webhooks)   │
    └─────────────┘ └───────────┘ └──────┬────────┘
                                          │ HMAC-imzolangan HTTP POST
                                          ▼
                                 Tashqi webhook manzillari
                                 (retry + exponential backoff)
```

## Nega bunday qaror qilindi

| Qaror | Sabab |
|---|---|
| `asyncio.Queue` asosidagi EventBus | Ingestion endpoint darhol javob qaytarishi kerak (202), og'ir ish (webhook yetkazish) orqa fonda bo'lishi kerak |
| Repository Protocol (interfeys) | Storage backend'ni (in-memory → Postgres/Redis) almashtirish qolgan kodga tegmasdan bo'lishi uchun (Dependency Inversion) |
| HMAC + timestamp imzo | Webhook qabul qiluvchi tomon so'rovning haqiqiyligini va yangiligini (replay attack'siz) tekshira olishi uchun |
| Exponential backoff + jitter | Vaqtinchalik tarmoq xatolarida qayta urinish, lekin ko'p webhook bir vaqtda qayta urinib qabul qiluvchini "thundering herd" bilan qulatmasligi uchun |
| Sliding window analytics | To'liq tarixni saqlamasdan, oxirgi N soniyalik statistikani O(1) evict bilan hisoblash |
| Dead letter (max_retries) | Cheksiz urinish o'rniga, muvaffaqiyatsiz yetkazishlarni kuzatish va keyinchalik qo'lda ko'rib chiqish imkoniyati |

## Kengaytirish nuqtalari

- `Repository` interfeysini Postgres yoki Redis bilan almashtirish — boshqa hech narsa o'zgarmaydi
- `EventBus`ni Kafka/RabbitMQ bilan almashtirish — ko'p instance (horizontal scaling) uchun
- `AnalyticsEngine`ga persistent time-series backend (masalan ClickHouse) qo'shish
