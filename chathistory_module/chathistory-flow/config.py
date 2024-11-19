import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', ''),
    'master_key': os.environ.get('ACCOUNT_KEY', ''),
    'database_id': os.environ.get('COSMOS_DATABASE', 'ChatDatabase'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'ConversationsAndMessages'),
}