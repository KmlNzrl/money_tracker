import psycopg2

def get_connection():
    return psycopg2.connect(
        host = "localhost",
        database = "akmal",
        user = "akmal",
        password = "1234"
    )