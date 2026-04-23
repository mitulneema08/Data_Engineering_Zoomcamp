import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

@click.command()
@click.option('--pg-user', required=True, help='PostgreSQL user')
@click.option('--pg-pass', required=True, help='PostgreSQL password')
@click.option('--pg-host', required=True, help='PostgreSQL host')
@click.option('--pg-port', required=True, type=int, help='PostgreSQL port')
@click.option('--pg-db', required=True, help='PostgreSQL database name')
@click.option('--target-table', required=True, help='Target table name')
@click.option('--url', required=True, help='URL of the CSV file')
def ingest(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, url):
    
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')
    
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=100000
    )

    first_chunk = next(df_iter)
    
    first_chunk.head(0).to_sql(
        name=target_table,
        con=engine,
        if_exists="replace"
    )
    print("Table created")

    first_chunk.to_sql(
        name=target_table,
        con=engine,
        if_exists="append"
    )
    print("Inserted first chunk:", len(first_chunk))

    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )

    print("Done! Data ingested successfully.")

if __name__ == '__main__':
    ingest()