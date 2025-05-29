from pydantic import BaseModel, EmailStr, ConfigDict


class UserSchema(BaseModel):
    # чтобы сразу передавались верные типы и не было конвертации из одного в другое
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"

