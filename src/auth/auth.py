from jwt.exceptions import InvalidTokenError
from fastapi import (
    APIRouter, Depends, Form, HTTPException, status
)
from fastapi.security import (
    OAuth2PasswordBearer
)

from src.auth.helpers import create_access_token, create_refresh_token
from src.users.schemas import UserSchema, TokenInfo
from src.auth import utils as au_utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")

router = APIRouter(prefix="/jwt", tags=["JWT"])

john = UserSchema(
    username="john",
    password=au_utils.hash_password("qwerty"),
    email="john@example.com"
)

sam = UserSchema(
    username="sam",
    password=au_utils.hash_password("secret"),
    email="sam@example.com"
)

users_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam
}


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


def get_current_token_payload(
        # credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
        token: str = Depends(oauth2_scheme)
) -> UserSchema:
    # token = credentials.credentials
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


def get_current_auth_user(
        payload: dict = Depends(get_current_token_payload)
) -> UserSchema:
    username: str | None = payload.get("sub")
    if (user := users_db.get(username)):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid"
    )


def get_current_active_auth_user(
        user: UserSchema = Depends(get_current_auth_user)
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive"
    )


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
        user: UserSchema = Depends(validate_auth_user)
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/users/me/")
def auth_user_check_self_info(
        payload: dict = Depends(get_current_token_payload),
        user: UserSchema = Depends(get_current_active_auth_user)
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat
    }
