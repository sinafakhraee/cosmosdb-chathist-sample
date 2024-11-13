import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-cosmosdb-resources-portal#create-an-azure-cosmos-db-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Item resource for Azure Cosmos
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


import random
import uuid

# Additional function to create user_chat_history container and add random chat history
def create_user_chat_history_container(db):
    try:
        container = db.create_container(id='conversations', partition_key=PartitionKey(path='/username'))
        print('Container with id \'conversationsy\' created')
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client('conversations')
        print('Container with id \'conversations\' was found')

    # Creating random usernames and chat history
    usernames = ['user_' + str(i) for i in range(1, 6)]
    chat_history = [
        "Hello, how can I assist you today?",
        "What is the status of my order?",
        "Can you explain the billing process?",
        "Thank you for your help!",
        "I'm having an issue with the app."
    ]

    # Inserting chat history for each user
    for username in usernames:
        conversation = random.choices(chat_history, k=5)
        container.create_item(body={
            'id': str(uuid.uuid4()),
            'username': username,
            'conversation': conversation
        })
    return container

# Function to read and display chat history
def display_user_chat_history(container):
    print('\nDisplaying all chat history in user_chat_history container\n')

    item_list = list(container.read_all_items(max_item_count=10))
    
    for doc in item_list:
        print(f'Username: {doc.get("username")}')
        print(f'Chat Conversation: {doc.get("conversation")}')
        print('---')

def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        # setup database for this sample
        try:
            db = client.create_database(id=DATABASE_ID)
            print('Database with id \'{0}\' created'.format(DATABASE_ID))

        except exceptions.CosmosResourceExistsError:
            db = client.get_database_client(DATABASE_ID)
            print('Database with id \'{0}\' was found'.format(DATABASE_ID))

        # setup container for this sample
        try:
            container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))

        except exceptions.CosmosResourceExistsError:
            container = db.get_container_client(CONTAINER_ID)
            print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

       

        # Additional function calls for user chat history
        user_chat_container = create_user_chat_history_container(db)
        display_user_chat_history(user_chat_container)

        # cleanup database after sample
        # try:
        #     client.delete_database(db)

        # except exceptions.CosmosResourceNotFoundError:
        #     pass

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == '__main__':
    run_sample()