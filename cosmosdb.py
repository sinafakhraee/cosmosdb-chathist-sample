import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import uuid
import config
import pandas as pd

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

# Create the chat history container if it does not exist
def create_user_chat_history_container(db):
    try:
        container = db.create_container(id='user_chat_history', partition_key=PartitionKey(path='/username'))
        print('Container with id \'user_chat_history\' created')
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client('user_chat_history')
        print('Container with id \'user_chat_history\' was found')
    return container

# Save user conversation to CosmosDB
def save_user_chat(username, conversation):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    db = client.get_database_client(DATABASE_ID)
    container = create_user_chat_history_container(db)
    
    item = {
        'id': str(uuid.uuid4()),
        'username': username,
        'conversation': conversation
    }
    container.create_item(body=item)
    print("Conversation saved for user:", username)

# Get chat history for a specific user
def get_user_chat_history(username):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    db = client.get_database_client(DATABASE_ID)
    container = create_user_chat_history_container(db)
    
    item_list = list(container.read_all_items(max_item_count=100))
    chat_data = [{"Username": item.get("username"), "Chat": item.get("conversation")}
                 for item in item_list if item.get("username") == username]
    
    return pd.DataFrame(chat_data)
