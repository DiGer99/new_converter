from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent.parent

class DBSettings(BaseModel):
    url: str = f"postgres+psycog2:///"
    echo: bool = True


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30



class Settings(BaseSettings):
    db: DBSettings = DBSettings()

    auth_jwt: AuthJWT = AuthJWT()

settings = Settings()