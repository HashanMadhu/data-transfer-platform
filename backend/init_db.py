import models
from database import mysql_engine, postgres_engine, Base

def initialize_databases():
    """
    Automatically creates the required tables in both MySQL and PostgreSQL databases
    based on the SQLAlchemy models defined in models.py
    """
    print("--- Starting Database Initialization ---")

    try:
        # Create tables in MySQL (Source DB)
        print("Creating tables in MySQL (Source Database)...")
        Base.metadata.create_all(bind=mysql_engine)
        print("Successfully created tables in MySQL.")

        # Create tables in PostgreSQL (Target DB)
        print("Creating tables in PostgreSQL (Target Database)...")
        Base.metadata.create_all(bind=postgres_engine)
        print("Successfully created tables in PostgreSQL.")

        print("--- Database Initialization Completed Successfully! ---")

    except Exception as e:
        print(f"Error during database initialization: {str(e)}")

if __name__ == "__main__":
    initialize_databases()