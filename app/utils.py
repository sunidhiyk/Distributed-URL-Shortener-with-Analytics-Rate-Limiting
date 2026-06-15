from passlib.context import CryptContext
import random
import string

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def generate_short_code(length=6):

    chars = string.ascii_letters + string.digits

    return ''.join(
        random.choice(chars)
        for _ in range(length)
    )