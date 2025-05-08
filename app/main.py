from fastapi import FastAPI
import os
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.responses import JSONResponse

app = FastAPI()

# Redis setup
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# PostgreSQL setup
pg_conn_params = {
    "host": os.getenv("POSTGRES_HOST", "db"),
    "database": os.getenv("POSTGRES_DB", "fastapi_db"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "adminpass"),
    "port": os.getenv("POSTGRES_PORT", 5432),
}


@app.get("/")
def root():
    return {"message": "FastAPI app running in production!"}


@app.get("/db-check")
def db_check():
    try:
        with psycopg2.connect(**pg_conn_params, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
        return {"db_status": "connected", "result": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"db_status": "error", "detail": str(e)})


@app.get("/redis-check")
def redis_check():
    try:
        redis_client.set("health_check", "ok", ex=10)
        value = redis_client.get("health_check")
        return {"redis_status": "connected", "value": value}
    except Exception as e:
        return JSONResponse(status_code=500, content={"redis_status": "error", "detail": str(e)})
