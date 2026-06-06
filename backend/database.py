from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse

# 1. Database Connection Strings (URLs)
# Connection string for MySQL (XAMPP - default password is empty)
MYSQL_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/source_db"


# Connection string for PostgreSQL (Replace 'root' with your actual pgAdmin password if different)
#POSTGRES_DATABASE_URL = "postgresql://postgres:Hashan@1013@localhost:5432/target_db"

# Safely encode the password that contains special characters like '@'
raw_password = "Hashan@1013"
encoded_password = urllib.parse.quote_plus(raw_password)

# Safe connection string for PostgreSQL
POSTGRES_DATABASE_URL = f"postgresql://postgres:{encoded_password}@localhost:5432/target_db"


# 2. Create Database Engines (The bridges between Python and DBs)
mysql_engine = create_engine(MYSQL_DATABASE_URL)
postgres_engine = create_engine(POSTGRES_DATABASE_URL)

# 3. Create Session Factories (Used to handle actual database operations)
MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# Base class for database models
Base = declarative_base()

# 4. Dependency Functions (To open and close database connection per API request)
def get_mysql_db():
    db = MySQLSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()