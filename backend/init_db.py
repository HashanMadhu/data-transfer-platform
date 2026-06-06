import models
from database import mysql_engine, postgres_engine

def initialize_databases():
    print("--- Starting Database Initialization ---")

    try:
        
        # Create tables in MySQL (Source Database) 
        print("Creating table in MySQL (Source Database)...")
        models.SourceUser.__table__.create(bind=mysql_engine, checkfirst=True)
        print("Successfully created 'users' table in MySQL.")

        # Create tables in PostgreSQL 'secure_users', 'migration_logs'
        print("Creating tables in PostgreSQL (Target Database)...")
        models.TargetUser.__table__.create(bind=postgres_engine, checkfirst=True)
        models.MigrationLog.__table__.create(bind=postgres_engine, checkfirst=True)
        print("Successfully created target tables in PostgreSQL.")

        print("--- Database Initialization Completed Successfully! ---")

    except Exception as e:
        print(f"Error during database initialization: {str(e)}")

if __name__ == "__main__":
    initialize_databases()