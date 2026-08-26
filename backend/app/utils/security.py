from passlib.context import CryptContext

# Configure bcrypt hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """
    Convert a plain password into a bcrypt hash.
    """
    return pwd_context.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Compare plain password with stored hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )