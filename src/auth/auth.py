from fastapi import (
    APIRouter, Depends, Form, HTTPException, status
)

from src.users.schemas import UserSchema, TokenInfo
from src.auth import utils as au_utils

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
        password: str = Form() # python-multipart
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


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
        user: UserSchema = Depends(validate_auth_user)
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email
    }
    token = au_utils.encode_jwt(
        payload=jwt_payload
    )
    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )