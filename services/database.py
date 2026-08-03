import os
from pathlib import Path

import pandas as pd
from dotenv import dotenv_values, load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = APP_DIR.parent
PIPELINE_ENV_PATH = PROJECT_DIR / "social_data_pipeline" / ".env"

load_dotenv(APP_DIR / ".env")


def _dashboard_url():
    uri = os.getenv("POSTGRES_URI") or os.getenv("DATABASE_URL")

    if uri:
        return uri

    pipeline_values = dotenv_values(PIPELINE_ENV_PATH)
    pipeline_uri = pipeline_values.get("POSTGRES_URI")

    if pipeline_uri:
        return pipeline_uri

    return URL.create(
        drivername=os.getenv("DB_DRIVER", "postgresql+psycopg2"),
        username=os.getenv("DB_USER") or pipeline_values.get("POSTGRES_USER"),
        password=os.getenv("DB_PASSWORD") or pipeline_values.get("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT") or pipeline_values.get("POSTGRES_PORT") or 5432),
        database=os.getenv("DB_NAME") or pipeline_values.get("POSTGRES_DB") or "radar_odio",
    )


engine = create_engine(
    _dashboard_url(),
    pool_pre_ping=True,
    connect_args={
        "options": "-c max_parallel_workers_per_gather=0",
    },
)


def run_query(query, params=None):
    return pd.read_sql_query(
        text(query),
        engine,
        params=params,
    )
