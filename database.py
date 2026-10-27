
import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Check for unified database URL (provided by Railway, Heroku, Aiven, etc.)
raw_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

if raw_url:
    # Ensure the pymysql driver is used if mysql:// protocol was passed
    if raw_url.startswith("mysql://"):
        DATABASE_URL = raw_url.replace("mysql://", "mysql+pymysql://", 1)
    else:
        DATABASE_URL = raw_url
else:
    # Read discrete environment variables, supporting both DB_* and Railway MYSQL* conventions
    DB_USER = os.getenv("DB_USER") or os.getenv("MYSQLUSER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD", "")
    DB_HOST = os.getenv("DB_HOST") or os.getenv("MYSQLHOST", "localhost")
    DB_PORT = os.getenv("DB_PORT") or os.getenv("MYSQLPORT", "3306")
    DB_NAME = os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE", "employee_db")

    # Safely URL-encode user and password to handle special characters (@, :, #, etc.)
    encoded_user = urllib.parse.quote_plus(DB_USER)
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

    DATABASE_URL = (
        f"mysql+pymysql://{encoded_user}:{encoded_password}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

