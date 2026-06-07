from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text 
from sqlalchemy.orm import Session
import database
import models
import security
from pydantic import BaseModel

# Pydantic Model for request validation
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

app = FastAPI(title="Heterogeneous Data Transfer API")

# CORS සැකසීම (මෙය වරක් පමණක් තිබීම ප්‍රමාණවත්)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API Endpoint - Check the connection status of both databases
@app.get("/api/status")
def check_status(
    mysql_db: Session = Depends(database.get_mysql_db),
    postgres_db: Session = Depends(database.get_postgres_db)
):
    status = {"mysql": "Disconnected", "postgresql": "Disconnected"}
    
    # Check MySQL Connection
    try:
        mysql_db.execute(text("SELECT 1"))
        status["mysql"] = "Connected"
    except Exception as e:
        status["mysql"] = f"Error: {str(e)}"
        
    # Check PostgreSQL Connection
    try:
        postgres_db.execute(text("SELECT 1"))
        status["postgresql"] = "Connected"
    except Exception as e:
        status["postgresql"] = f"Error: {str(e)}"
        
    return status

# 2. API Endpoint - Trigger the data migration from MySQL to PostgreSQL
@app.post("/api/migrate")
def trigger_migration(
    mysql_db: Session = Depends(database.get_mysql_db),
    postgres_db: Session = Depends(database.get_postgres_db)
):
    try:
        source_users = mysql_db.query(models.SourceUser).all()
        
        if not source_users:
            return {"status": "SUCCESS", "rows_migrated": 0, "message": "No data found to migrate."}
            
        rows_counter = 0
        
        for user in source_users:
            exists = postgres_db.query(models.TargetUser).filter(models.TargetUser.email == user.email).first()
            if not exists:
                secure_pwd = security.encrypt_data(user.password)
                
                new_target_user = models.TargetUser(
                    name=user.name,
                    email=user.email,
                    encrypted_password=secure_pwd
                )
                postgres_db.add(new_target_user)
                rows_counter += 1
                
        postgres_db.commit()
        
        # Log the success
        log_entry = models.MigrationLog(status="SUCCESS", rows_migrated=rows_counter, message="Migration completed successfully.")
        postgres_db.add(log_entry)
        postgres_db.commit()
        
        return {"status": "SUCCESS", "rows_migrated": rows_counter}
        
    except Exception as e:
        postgres_db.rollback()
        error_msg = str(e)
        try:
            log_entry = models.MigrationLog(status="FAILED", rows_migrated=0, message=error_msg)
            postgres_db.add(log_entry)
            postgres_db.commit()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Migration failed: {error_msg}")

# 3. API Endpoint - Retrieve historical logs
@app.get("/api/logs")
def get_migration_logs(postgres_db: Session = Depends(database.get_postgres_db)):
    logs = postgres_db.query(models.MigrationLog).order_by(models.MigrationLog.timestamp.desc()).all()
    return logs

# 4. API Endpoint - Insert new user into MySQL
@app.post("/api/users/mysql")
def create_mysql_user(user_data: UserCreate, mysql_db: Session = Depends(database.get_mysql_db)):
    try:
        exists = mysql_db.query(models.SourceUser).filter(models.SourceUser.email == user_data.email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered in MySQL.")
        
        new_user = models.SourceUser(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        mysql_db.add(new_user)
        mysql_db.commit()
        mysql_db.refresh(new_user)
        
        return {"status": "SUCCESS", "message": f"User '{user_data.name}' added to MySQL."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        mysql_db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert user: {str(e)}")