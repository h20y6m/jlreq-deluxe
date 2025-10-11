#!/usr/bin/env python3
import logging

import generator

logger = logging.getLogger(__name__)


def main():
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    generator.generate_all()
    # dump_jfm()
    # dump_vf()


if __name__ == "__main__":
    main()
