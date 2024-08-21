from google.cloud import bigquery
from google.oauth2 import service_account

service_account_file = "cred.json"
credentials = service_account.Credentials.from_service_account_file(
    service_account_file
)

client = bigquery.Client(credentials=credentials, project=credentials.project_id)


"""
We need 3 tables users,locations,whitelisted_users

"""



userSchema = [
        bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("isAnswer", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("iswhiteList", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("userName", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("password", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("userID", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("role", "STRING", mode="NULLABLE")
    ]


locationSchema = [
    bigquery.SchemaField("longitude", "STRING", mode="NULLABLE", description="The longitude coordinate of the location"),
    bigquery.SchemaField("latitude", "STRING", mode="NULLABLE", description="The latitude coordinate of the location"),
    bigquery.SchemaField("locationID", "STRING", mode="NULLABLE", description="The unique identifier for the location")
]




whitelisted_userSchema= [
        bigquery.SchemaField("name", "STRING", mode="NULLABLE", description="The name of the user"),
        bigquery.SchemaField("email", "STRING", mode="NULLABLE", description="The email address of the user"),
        bigquery.SchemaField("userID", "STRING", mode="NULLABLE", description="The unique identifier for the user")
    ]







def create_user_table():
    

    project_id = "your-project-id"
    dataset_id = "your-dataset-name"
    table_name = "your-table-name"

    table_id = f"{project_id}.{dataset_id}.{table_name}"



    schema = locationSchema



    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)  #
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

if __name__ == "__main__":
    create_user_table()