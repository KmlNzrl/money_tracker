import psycopg2

def get_connection():
    return psycopg2.connect(
        host = "localhost",
        database = "money_tracker",
        user = "akmal",
        password = "1234"
    )