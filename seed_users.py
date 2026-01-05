from db.auth import create_user

users = [
    ("admin", "admin"),
    ("abc", "123"),
    ("def", "456"),
]

for email, password in users:
    try:
        create_user(email, password)
        print(f"User created: {email}")
    except Exception as e:
        print(f"User {email} already exists or error: {e}")
