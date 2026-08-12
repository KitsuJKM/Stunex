import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    jwt_secret_key: str = os.environ["JWT_SECRET_KEY"]

    mysql_host: str = os.environ["MYSQL_HOST"]
    mysql_port: int = int(os.environ["MYSQL_PORT"])
    mysql_user: str = os.environ["MYSQL_USER"]
    mysql_password: str = os.environ["MYSQL_PASSWORD"]
    mysql_database: str = os.environ["MYSQL_DATABASE"]

    resend_api_key: str = os.environ.get("RESEND_API_KEY", "")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


settings = Settings()
