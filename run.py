"""Start the four phone servers (ports 3001-3004) sharing one orchestrator and database."""

import argparse
import asyncio

import uvicorn

from server.app import create_app
from server.db import PEOPLE, init_db, reset_db
from server.orchestrator import Orchestrator

BASE_PORT = 3000


async def serve(db_path, host):
    orch = Orchestrator()
    servers = []
    for person_id in PEOPLE:
        config = uvicorn.Config(
            create_app(person_id, orch, db_path),
            host=host,
            port=BASE_PORT + person_id,
            log_level="warning",
        )
        servers.append(uvicorn.Server(config))
    for person_id, name in PEOPLE.items():
        print(f"{name}: http://localhost:{BASE_PORT + person_id}", flush=True)
    await asyncio.gather(*(s.serve() for s in servers))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="bank.db", help="SQLite file (default: bank.db)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--reset", action="store_true", help="restore starting balances and exit")
    args = parser.parse_args()

    if args.reset:
        reset_db(args.db)
        print("Database reset: every person has 10 000 CZK, no payments.")
        return
    init_db(args.db)
    asyncio.run(serve(args.db, args.host))


if __name__ == "__main__":
    main()
