import functools
import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def run_command(command: str, *args: str) -> list[str]:
    result = subprocess.run(
        [command, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,  # 標準エラーは無視
        text=True,
        check=True,  # 失敗したら例外を投げる
    )
    return result.stdout.splitlines()


@functools.cache
def find_file(name):
    if os.path.isfile(name):
        return name
    logger.debug(f"calling: kpsewhich {name}")
    p = run_command("kpsewhich", name)
    logger.debug(f"returns: {p}")
    if len(p) == 0 or len(p[0]) == 0:
        raise FileNotFoundError()
    return p[0]
