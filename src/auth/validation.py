from fastapi import Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from starlette import status


from src.auth import utils as au_utils
from src.auth.crud import users_db
from src.auth.helpers import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.users.schemas import UserSchema

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/jwt/login/"
)


def get_current_token_payload(
        token: str = Depends(oauth2_scheme)
) -> UserSchema:
    try:
        payload = au_utils.decode_jwt(
            token=token
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error"
        )
    return payload


def validate_token_type(
        payload: dict,
        token_type: str
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type} expected {token_type}"
    )


def get_user_by_token_sub(
        payload: dict = Depends(get_current_token_payload)
) -> UserSchema:
    username: str | None = payload.get("sub")
    if user := users_db.get(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid"
    )


def get_auth_user_from_token_type(token_type: str):
    def get_auth_user_from_token(
            payload: dict = Depends(get_current_token_payload)
    ):
        validate_token_type(payload, token_type)
        return get_user_by_token_sub(payload)

    return get_auth_user_from_token


get_current_auth_user = get_auth_user_from_token_type(ACCESS_TOKEN_TYPE)

get_current_auth_user_for_refresh = get_auth_user_from_token_type(REFRESH_TOKEN_TYPE)


def validate_auth_user(
        username: str = Form(),
        password: str = Form()  # python-multipart
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
    if not (user := users_db.get(username)):
        raise unauthed_exc

    if not au_utils.validate_password(
            password=password,
            hashed_password=user.password
    ):
        return unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive"
        )

    return user


def get_current_active_auth_user(
        user: UserSchema = Depends(get_current_auth_user)
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive"
    )
