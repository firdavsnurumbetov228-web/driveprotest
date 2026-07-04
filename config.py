import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

for candidate in (
    BASE_DIR / ".env",
    BASE_DIR.parent / ".env",
    Path.cwd() / ".env",
):
    if candidate.exists():
        load_dotenv(candidate, override=False)
        break


def _read_env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip().strip('"').strip("'") if isinstance(value, str) else default


BOT_TOKEN: str = _read_env("BOT_TOKEN")
DATABASE_URL: str = _read_env("DATABASE_URL")
ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in _read_env("ADMIN_IDS", "0").split(",")
    if x.strip().isdigit()
]
WEBAPP_URL: str = _read_env("WEBAPP_URL", "https://auto-test-911-lg62.vercel.app/")
INFO_URL: str = _read_env("INFO_URL", "https://avtot-test-malumotlar.vercel.app/")
