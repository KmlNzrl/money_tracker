from db.database import get_connection
from auth.utils import hash_password, verify_password

def create_user(email: str, password: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (email, password_hash)
        VALUES (%s, %s)
        """,
        (email, hash_password(password))
    )

    conn.commit()
    cur.close()
    conn.close()


def authenticate_user(email: str, password: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, password_hash FROM users WHERE email = %s",
        (email,)
    )
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and verify_password(password, user[1]):
        return user[0]  # user_id

    return None
