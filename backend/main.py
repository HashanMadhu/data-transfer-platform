from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text  # Required instead of models.text
from sqlalchemy.orm import Session
import database
import models
import security
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

app = FastAPI(title="Heterogeneous Data Transfer API")

# Setup Jinja2 Templates (The templates folder must be in the project root)
templates = Jinja2Templates(directory="templates") 

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 0. Root Route - Serve the frontend HTML dashboard
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# 1. API Endpoint - Check the connection status of both databases
@app.get("/api/status")
def check_status(
    mysql_db: Session = Depends(database.get_mysql_db),
    postgres_db: Session = Depends(database.get_postgres_db)
):
    status = {"mysql": "Disconnected", "postgresql": "Disconnected"}
    
    # Check MySQL Connection
    try:
        mysql_db.execute(text("SELECT 1"))  # Directly using text()
        status["mysql"] = "Connected"
    except Exception as e:
        status["mysql"] = f"Error: {str(e)}"
        
    # Check PostgreSQL Connection
    try:
        postgres_db.execute(text("SELECT 1"))  # Directly using text()
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
        # Fetch all users from the source database (MySQL)
        source_users = mysql_db.query(models.SourceUser).all()
        
        if not source_users:
            return {"status": "SUCCESS", "rows_migrated": 0, "message": "No data found to migrate."}
            
        rows_counter = 0
        
        # Loop through each user, encrypt sensitive data, and save to target database (PostgreSQL)
        for user in source_users:
            # Check if user already exists in target DB to avoid duplicates
            exists = postgres_db.query(models.TargetUser).filter(models.TargetUser.email == user.email).first()
            if not exists:
                # Encrypt the plain text password
                secure_pwd = security.encrypt_data(user.password)
                
                # Create a new TargetUser object
                new_target_user = models.TargetUser(
                    name=user.name,
                    email=user.email,
                    encrypted_password=secure_pwd
                )
                postgres_db.add(new_target_user)
                rows_counter += 1
                
        # Commit changes to PostgreSQL
        postgres_db.commit()
        
        # Log the successful status into the migration logs table
        log_entry = models.MigrationLog(status="SUCCESS", rows_migrated=rows_counter, message="Migration completed successfully.")
        postgres_db.add(log_entry)
        postgres_db.commit()
        
        return {"status": "SUCCESS", "rows_migrated": rows_counter}
        
    except Exception as e:
        # Rollback changes in case of an error
        postgres_db.rollback()
        
        error_msg = str(e)
        # Log the failure status with the error message
        try:
            log_entry = models.MigrationLog(status="FAILED", rows_migrated=0, message=error_msg)
            postgres_db.add(log_entry)
            postgres_db.commit()
        except Exception:
            pass  # Ensure the primary exception is raised even if logging fails
            
        raise HTTPException(status_code=500, detail=f"Migration failed: {error_msg}")

# 3. API Endpoint - Retrieve historical logs for the dashboard
@app.get("/api/logs")
def get_migration_logs(postgres_db: Session = Depends(database.get_postgres_db)):
    # Fetch logs ordered by the most recent timestamp (Descending)
    logs = postgres_db.query(models.MigrationLog).order_by(models.MigrationLog.timestamp.desc()).all()
    return logs

# 4. API Endpoint - Insert a new plain-text user into MySQL (Source DB)
@app.post("/api/users/mysql")
def create_mysql_user(user_data: UserCreate, mysql_db: Session = Depends(database.get_mysql_db)):
    try:
        # Check if email is already registered to avoid duplication
        exists = mysql_db.query(models.SourceUser).filter(models.SourceUser.email == user_data.email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered in MySQL source database.")
        
        # Create a new source user object
        new_user = models.SourceUser(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        mysql_db.add(new_user)
        mysql_db.commit()
        mysql_db.refresh(new_user)
        
        return {"status": "SUCCESS", "message": f"User '{user_data.name}' successfully added to MySQL source DB."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        mysql_db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=f"Failed to insert user into MySQL: {str(e)}")