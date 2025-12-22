#!/usr/bin/env python3

from src.config import Config
from src.server import TaskServer


def main():
    config = Config.load()
    server = TaskServer(config)
    server.run()


if __name__ == '__main__':
    main()
