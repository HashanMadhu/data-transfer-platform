from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request # Request එක දැනටමත් නැත්නම් විතරක් දාන්න
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import models
import security

app = FastAPI(title="Heterogeneous Data Transfer API")
templates = Jinja2Templates(directory="templates") 

# 0. Root Route to serve the frontend HTML dashboard
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Enable CORS so our frontend (React) can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API Endpoint to check the connection status of both databases
@app.get("/api/status")
def check_status(
    mysql_db: Session = Depends(database.get_mysql_db),
    postgres_db: Session = Depends(database.get_postgres_db)
):
    status = {"mysql": "Disconnected", "postgresql": "Disconnected"}
    
    # Check MySQL Connection
    try:
        mysql_db.execute(models.text("SELECT 1"))
        status["mysql"] = "Connected"
    except Exception as e:
        status["mysql"] = f"Error: {str(e)}"
        
    # Check PostgreSQL Connection
    try:
        postgres_db.execute(models.text("SELECT 1"))
        status["postgresql"] = "Connected"
    except Exception as e:
        status["postgresql"] = f"Error: {str(e)}"
        
    return status

# 2. API Endpoint to trigger the data migration process
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
                
                # Create new target user object
                new_target_user = models.TargetUser(
                    name=user.name,
                    email=user.email,
                    encrypted_password=secure_pwd
                )
                postgres_db.add(new_target_user)
                rows_counter += 1
                
        # Commit the changes to PostgreSQL
        postgres_db.commit()
        
        # Log the success status into the migration logs table
        log_entry = models.MigrationLog(status="SUCCESS", rows_migrated=rows_counter, message="Migration completed successfully.")
        postgres_db.add(log_entry)
        postgres_db.commit()
        
        return {"status": "SUCCESS", "rows_migrated": rows_counter}
        
    except Exception as e:
        # If something fails, log the failure status with the error message
        error_msg = str(e)
        log_entry = models.MigrationLog(status="FAILED", rows_migrated=0, message=error_msg)
        postgres_db.add(log_entry)
        postgres_db.commit()
        raise HTTPException(status_code=500, detail=f"Migration failed: {error_msg}")

# 3. API Endpoint to retrieve history logs for the frontend dashboard
@app.get("/api/logs")
def get_migration_logs(postgres_db: Session = Depends(database.get_postgres_db)):
    # Fetch logs ordered by the most recent timestamp
    logs = postgres_db.query(models.MigrationLog).order_by(models.MigrationLog.timestamp.desc()).all()
    return logs