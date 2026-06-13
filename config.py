import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://auto-test-911-lg62.vercel.app/")
INFO_URL: str = os.getenv("INFO_URL", "https://avtot-test-malumotlar.vercel.app/")
