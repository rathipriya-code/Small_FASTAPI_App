import time
from fastapi import FastAPI
from celery import Celery
from celery.result import AsyncResult
from pydantic import BaseModel
from typing import Any


CELERY_BROKER = "redis://localhost:6379/0"
CELERY_BACKEND = "redis://localhost:6379/0"


celery_app = Celery("Jobs", broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(task_track_started=True, result_extended=True)



@celery_app.task(name="tasks.dynamic_delay_job")
def dynamic_delay_job(job_name: str, delay_in_sec: int):
    print(f"Starting job: {job_name} for {delay_in_sec} seconds...")
    
    
    time.sleep(delay_in_sec) 
    
    return f"Job '{job_name}' completed successfully!"



app = FastAPI(title="Dynamic Job Worker Demo (Corrected Version)", version="1.0.0")



class JobCreateInput(BaseModel):
    job_name: str
    delay_in_sec: int
    


@app.post("/create-job", status_code=202)
def create_job(payload: JobCreateInput):
    
    task = dynamic_delay_job.delay(payload.job_name, payload.delay_in_sec)
    
    
    return {
        "job_id": task.id
    }



@app.get("/status/{job_id}")
def get_job_status(job_id: str):
    
    task_result = AsyncResult(job_id, app=celery_app)
    
   
    current_status = task_result.status.lower()
        
    
    return {
        "status": current_status
    }


