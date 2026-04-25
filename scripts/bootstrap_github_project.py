#!/usr/bin/env python3
"""Compatibilidade: use scripts/roadmap_builder.py para novos comandos."""

import sys

from roadmap_builder import main


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
