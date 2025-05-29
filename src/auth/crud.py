from src.auth import utils as au_utils
from src.users.schemas import UserSchema

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
