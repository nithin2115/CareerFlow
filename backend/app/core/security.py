from argon2 import PasswordHasher
password_hasher =PasswordHasher()
def hash_password(password: str) -> str:
    return password_hasher.hash(password)
def verify_password(password: str, Stored_password_hash: str) -> bool:
    return password_hasher.verify(Stored_password_hash, password)

