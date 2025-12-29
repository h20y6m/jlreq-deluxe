#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from generator import Config, generate_all

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Genarate jlreq-deluxe JFM/VF")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--tfmdir", default=Path("./tfm"), type=Path)
    parser.add_argument("--vfdir", default=Path("./vf"), type=Path)
    parser.add_argument("--dumpjpl", action="store_true")
    parser.add_argument("--jpldir", default=Path("./jpl"), type=Path)
    parser.add_argument("--dumpvpl", action="store_true")
    parser.add_argument("--vpldir", default=Path("./vpl"), type=Path)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    args.tfmdir.mkdir(parents=True, exist_ok=True)
    args.vfdir.mkdir(parents=True, exist_ok=True)
    if args.dumpjpl:
        args.jpldir.mkdir(parents=True, exist_ok=True)
    if args.dumpvpl:
        args.vpldir.mkdir(parents=True, exist_ok=True)

    generate_all(
        Config(
            args.tfmdir,
            args.vfdir,
            args.dumpjpl,
            args.jpldir,
            args.dumpvpl,
            args.vpldir,
        )
    )


if __name__ == "__main__":
    main()
