import pandas as pd
import os
import logging
import time
from sqlalchemy import create_engine, text

# ================= CONFIG =================

DATA_FOLDER = "DataV"
DATABASE_URL = "sqlite:///inventory.db"
CHUNK_SIZE = 100000

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

engine = create_engine(DATABASE_URL)


# ================= INGEST FUNCTION =================

def ingest_large_csv(file_path, table_name):
    try:
        logging.info(f"Ingesting {table_name}.csv in db")

        # Drop table if exists
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()

        for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
            chunk.to_sql(
                table_name,
                con=engine,
                if_exists="append",
                index=False
            )

    except Exception as e:
        logging.error(f"Error ingesting {table_name}: {e}")


# ================= MAIN LOADER =================

def load_raw_data():
    start = time.time()

    # SORTED order (important)
    files = sorted([
        f for f in os.listdir(DATA_FOLDER)
        if f.lower().endswith(".csv")
    ])

    for file in files:
        file_path = os.path.join(DATA_FOLDER, file)
        table_name = file[:-4]
        ingest_large_csv(file_path, table_name)

    end = time.time()
    total_time = (end - start) / 60

    logging.info("--------------Ingestion Complete--------------")
    logging.info(f"Total Time Taken: {total_time:.2f} minutes")


# ================= ENTRY =================

if __name__ == "__main__":
    load_raw_data()