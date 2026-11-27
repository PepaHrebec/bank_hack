"""Start the four phone servers (ports 3001-3004 by default) sharing one orchestrator and database."""

import argparse
import asyncio
import socket

import uvicorn

from server.app import create_app
from server.db import PEOPLE, init_db, reset_db
from server.orchestrator import Orchestrator

BASE_PORT = 3000


def lan_ip():
    # Connecting a UDP socket sends nothing; it just reveals which local address routes out.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def display_host(ip):
    # YouTube refuses to play embeds on pages served from a bare IP address, so show a
    # nip.io name instead: 146-102-217-199.nip.io resolves to 146.102.217.199.
    if ip in ("127.0.0.1", "localhost"):
        return "localhost"
    try:
        socket.inet_aton(ip)
    except OSError:
        return ip  # already a hostname
    return ip.replace(".", "-") + ".nip.io"


async def serve(db_path, host, shown_host, base_port=BASE_PORT):
    orch = Orchestrator()
    servers = []
    for person_id in PEOPLE:
        config = uvicorn.Config(
            create_app(person_id, orch, db_path),
            host=host,
            port=base_port + person_id,
            log_level="warning",
        )
        servers.append(uvicorn.Server(config))
    for person_id, name in PEOPLE.items():
        print(f"{name}: http://{shown_host}:{base_port + person_id}", flush=True)
    await asyncio.gather(*(s.serve() for s in servers))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="bank.db", help="SQLite file (default: bank.db)")
    parser.add_argument("--host", default="0.0.0.0",
                        help="address to listen on (default: all, so other devices on the network can connect)")
    parser.add_argument("--base-port", type=int, default=BASE_PORT,
                        help="person N is served on base-port + N (default: 3000)")
    parser.add_argument("--reset", action="store_true", help="restore starting balances and exit")
    args = parser.parse_args()

    if args.reset:
        reset_db(args.db)
        print("Database reset: every person has 10 000 CZK, no payments.")
        return
    init_db(args.db)
    shown_host = display_host(lan_ip() if args.host == "0.0.0.0" else args.host)
    asyncio.run(serve(args.db, args.host, shown_host, args.base_port))


if __name__ == "__main__":
    main()
