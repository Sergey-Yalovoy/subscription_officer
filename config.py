import os
from pathlib import Path
import dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class DbSettings(BaseModel):
    db_name: str = "db.sqlite3"
    db_path: Path = Path(__file__).parent / "db.sqlite3"
    url: str = f"sqlite+aiosqlite:///{db_path}"
    url_sync: str = f"sqlite:///{db_path}"
    echo: bool = True


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    secret: str = 'secret'


settings = Settings()
