import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from config import DB_CONFIG, logger

# Function to create a new database connection
def create_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info('Database connection established.')
        return conn
    except Exception as e:
        logger.error(f'Failed to connect to the database: {e}')
        raise

# Function to fetch general_information
def fetch_general_information(id_value):
    conn = create_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                'SELECT general_information FROM "Answers" WHERE id = %s',
                (id_value,)
            )
            result = cursor.fetchone()
            logger.info(f"Fetched general information: {result}")
        return result
    except Exception as e:
        logger.error(f"Error fetching general information: {e}")
        return None
    finally:
        conn.close()

# Function to fetch answer image path
def fetch_answer_image_path(id_value, subquestion_number):
    conn = create_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Use psycopg2.sql module to safely include dynamic column names
            column_name = sql.Identifier(f'a{subquestion_number}')
            query = sql.SQL('SELECT {field} AS image_path FROM "Answers" WHERE id = %s').format(
                field=column_name
            )
            cursor.execute(query, (id_value,))
            result = cursor.fetchone()
            logger.info(f"Fetched answer image path: {result}")
        return result
    except Exception as e:
        logger.error(f"Error fetching answer image path: {e}")
        return None
    finally:
        conn.close()
