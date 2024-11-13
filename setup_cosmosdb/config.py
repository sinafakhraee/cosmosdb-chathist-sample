import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://{youcosmosaccnt}.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', ''),
    'database_id': os.environ.get('COSMOS_DATABASE', 'chat_history'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'user_chat_history'),
}