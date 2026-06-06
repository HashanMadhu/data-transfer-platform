from sqlalchemy import Column, Integer, String, DateTime, text
from datetime import datetime
from database import Base

# 1. User table schema for the source database (MySQL)
class SourceUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # This sensitive field will be encrypted later

# 2. Secure User table schema for the target database (PostgreSQL)
class TargetUser(Base):
    __tablename__ = "secure_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    encrypted_password = Column(String(500), nullable=False)  # Stores the encrypted password string

# 3. Audit log table schema to track migration status (PostgreSQL)
class MigrationLog(Base):
    __tablename__ = "migration_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)  # Time of the migration process
    status = Column(String(50), nullable=False)             # Status: 'SUCCESS' or 'FAILED'
    rows_migrated = Column(Integer, default=0)              # Number of rows transferred
    message = Column(String(500), nullable=True)            # Holds error messages if failed