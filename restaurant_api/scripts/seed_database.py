#!/usr/bin/env python
"""CLI: python scripts/seed_database.py [--force]"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.seed_data import main

if __name__ == '__main__':
    main()
