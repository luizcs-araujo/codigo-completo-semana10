from __future__ import annotations
import argparse, json
from .events import make_event, EVENTS
from .repository import Repository
from .tools import tool_specs
from .seed import reseed


def main():
    parser = argparse.ArgumentParser(prog='opspilot')
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('seed')
    sub.add_parser('list-tools')
    ev = sub.add_parser('emit-event')
    ev.add_argument('name', choices=sorted(EVENTS.keys()))
    sub.add_parser('audit')
    args = parser.parse_args()
    repo = Repository()
    if args.cmd == 'seed':
        reseed()
        print('seed ok')
    elif args.cmd == 'list-tools':
        print(json.dumps(tool_specs(), indent=2, ensure_ascii=False))
    elif args.cmd == 'emit-event':
        event = make_event(args.name)
        repo.record_event(**event)
        print(json.dumps(event, indent=2, ensure_ascii=False))
    elif args.cmd == 'audit':
        print(json.dumps(repo.list_audit(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
