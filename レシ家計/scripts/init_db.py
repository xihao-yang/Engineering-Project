from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import get_settings
from app.database import init_db, open_db


def main() -> None:
    settings = get_settings()
    with open_db(settings.db_path) as conn:
        init_db(conn)
    print(f"Initialized database: {settings.db_path}")


if __name__ == "__main__":
    main()
