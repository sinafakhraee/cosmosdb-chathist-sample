import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
from azure.cosmos import CosmosClient, PartitionKey, exceptions

import config


cosmosdb_endpoint = config.settings['host']
cosmosdb_key = config.settings['master_key']
database_name = config.settings['database_id']
container_name = config.settings['container_id']




# Initialize Cosmos Client
client = CosmosClient(cosmosdb_endpoint, credential=cosmosdb_key)

# Create or get the database
try:
    database = client.create_database_if_not_exists(id=database_name)
    print(f"Database '{database_name}' created or already exists.")
except exceptions.CosmosHttpResponseError as e:
    print(f"Failed to create or access database: {e}")
    exit()

# Define container schema
partition_key_path = "/userId"  # Partition key based on userId

try:
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path=partition_key_path),
        offer_throughput=400  # Set the desired throughput
    )
    print(f"Container '{container_name}' created or already exists.")
except exceptions.CosmosHttpResponseError as e:
    print(f"Failed to create or access container: {e}")
    exit()

print("Setup complete.")
