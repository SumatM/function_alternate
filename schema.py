from google.cloud import bigquery

def create_table():
    # Construct a BigQuery client object.
    client = bigquery.Client()

    # Set table_id to the ID of the table to create.
    table_id = "your-project.your_dataset.your_table_name"

    # Define your table schema
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE", description="The unique identifier for the user"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="The user's full name"),
        bigquery.SchemaField("email", "STRING", mode="NULLABLE", description="The user's email address"),
        bigquery.SchemaField("signup_date", "DATE", mode="NULLABLE", description="The date the user signed up")
    ]

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)  # API request
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

if __name__ == "__main__":
    create_table()
