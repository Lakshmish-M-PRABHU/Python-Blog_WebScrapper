import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host="host.docker.internal",
        port=5432,
        database="python_blog",
        user="postgres",
        password="secretpassword"
    )
