
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Load environment variables from the project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

# Build database connection
database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "company_db"),
)

engine = create_engine(database_url, pool_pre_ping=True)

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT DATABASE()")
            )
            print("MySQL connection successful!")
            print("Connected database:", result.scalar())

    except Exception as error:
        print("Database connection failed.")
        print("Error type:", type(error).__name__)

if __name__ == "__main__":
    test_connection()
