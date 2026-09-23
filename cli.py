"""CLI kirish nuqtasi — serverni ishga tushirish uchun."""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(prog="event-engine")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run("event_engine.api.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
