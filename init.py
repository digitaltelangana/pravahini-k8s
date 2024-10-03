import hashlib
import os
import subprocess
import random
import string
import psycopg2


def encode_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def api_token_configured(service_name):
    # Simulating retrieval from crudini
    try:
        token = (
            subprocess.check_output(
                [
                    "crudini",
                    "--get",
                    "/etc/xroad/conf.d/local.ini",
                    service_name,
                    "api-token",
                ]
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        print(f"api-token property not configured for {service_name}")
        return False

    prepare_db_props()  # Simulate database properties preparation

    # Read environment variables
    if os.path.exists("/etc/xroad/db_libpq.env"):
        with open("/etc/xroad/db_libpq.env") as f:
            for line in f:
                key, value = line.strip().split("=")
                os.environ[key] = value

    db_host = os.environ.get("PGHOST", "localhost")
    db_port = os.environ.get("PGPORT", "5432")
    db_name = os.environ.get("PGDATABASE", "xroad")
    db_user = os.environ.get("PGUSER", "xroad")
    db_password = os.environ.get("PGPASSWORD", "password")

    # Connect to the PostgreSQL database and query API keys
    conn = psycopg2.connect(
        host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password
    )
    cur = conn.cursor()

    cur.execute(
        """
        SELECT encodedkey FROM apikey a 
        INNER JOIN apikey_roles r ON a.id = r.apikey_id 
        WHERE r.role = 'XROAD_MANAGEMENT_SERVICE';
    """
    )
    apikeys = cur.fetchall()

    encoded_token = encode_token(token)

    for key in apikeys:
        if encoded_token == key[0]:
            cur.close()
            conn.close()
            return True

    print(f"Configured api-token for {service_name} not found in database")
    cur.close()
    conn.close()
    return False


def generate_api_key(service_name):
    token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    encoded_token = encode_token(token)

    prepare_db_props()  # Simulate database properties preparation

    # Insert new API key and role into the database
    db_host = os.environ.get("PGHOST", "localhost")
    db_port = os.environ.get("PGPORT", "5432")
    db_name = os.environ.get("PGDATABASE", "xroad")
    db_user = os.environ.get("PGUSER", "xroad")
    db_password = os.environ.get("PGPASSWORD", "password")

    conn = psycopg2.connect(
        host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password
    )
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO apikey(id, encodedkey) 
            VALUES (nextval('hibernate_sequence'), %s);
        """,
            (encoded_token,),
        )

        cur.execute(
            """
            INSERT INTO apikey_roles(apikey_id, role) 
            VALUES ((SELECT id FROM apikey WHERE encodedkey = %s), 'XROAD_MANAGEMENT_SERVICE');
        """,
            (encoded_token,),
        )

        conn.commit()
        cur.close()
        conn.close()

        # Simulating crudini configuration
        subprocess.run(
            [
                "crudini",
                "--set",
                "/etc/xroad/conf.d/local.ini",
                service_name,
                "api-token",
                token,
            ],
            check=True,
        )

        print("New API KEY successfully configured")
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        print(f"Failed to configure new API KEY: {e}")
        exit(1)


def main(service_name):
    if service_name not in ["management-service", "registration-service"]:
        print(
            'Must supply either "management-service" or "registration-service" as input argument'
        )
        return

    print(
        f"Checking whether a valid API KEY with Management Service role is configured for {service_name}..."
    )

    if api_token_configured(service_name):
        print("A valid API KEY with Management Service role already configured")
    else:
        print(
            f"Generating & configuring a new API KEY with Management Service role for {service_name}..."
        )
        generate_api_key(service_name)


# Simulate the bash script input argument
main("management-service")
