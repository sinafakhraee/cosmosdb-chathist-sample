import asyncio
import uuid
from datetime import datetime
from cosmosdbservice import CosmosConversationClient
import config
# Cosmos DB configuration
cosmosdb_endpoint = config.settings['host']
cosmosdb_key = config.settings['master_key']
database_name = config.settings['database_id']
container_name = config.settings['container_id']


async def main():
    # Initialize the CosmosConversationClient
    client = CosmosConversationClient(
        cosmosdb_endpoint=cosmosdb_endpoint,
        credential=cosmosdb_key,
        database_name=database_name,
        container_name=container_name,
        enable_message_feedback=True
    )

    # Ensure the client is set up correctly
    is_ready, message = await client.ensure()
    if not is_ready:
        print(f"Error: {message}")
        await client.cosmosdb_client.close()  # Ensure the connection is closed
        return
    print("Cosmos DB client initialized successfully.")

    try:
        # Example user ID
        user_id = str(uuid.uuid4())  # Random user ID

        # Create a conversation
        conversation_title = "Project Kickoff Discussion"
        conversation = await client.create_conversation(user_id, title=conversation_title)
        print(f"Created conversation: {conversation}")

        # Add a message to the conversation
        message_id = str(uuid.uuid4())  # Random message ID
        input_message = {
            "role": "user",
            "content": "What are the next steps for the project?"
        }
        created_message = await client.create_message(
            uuid=message_id,
            conversation_id=conversation["id"],
            user_id=user_id,
            input_message=input_message
        )
        print(f"Created message: {created_message}")

        # Retrieve all messages from the conversation
        messages = await client.get_messages(user_id=user_id, conversation_id=conversation["id"])
        print(f"Retrieved messages from conversation: {messages}")

        # Retrieve all conversations for the user
        conversations = await client.get_conversations(user_id=user_id, limit=5, sort_order='DESC')
        print(f"Retrieved conversations: {conversations}")

        # Delete the conversation and its messages
        # delete_messages_response = await client.delete_messages(conversation_id=conversation["id"], user_id=user_id)
        # print(f"Deleted messages: {delete_messages_response}")

        # delete_conversation_response = await client.delete_conversation(user_id=user_id, conversation_id=conversation["id"])
        # print(f"Deleted conversation: {delete_conversation_response}")

    finally:
        # Ensure the Cosmos DB client connection is closed
        await client.cosmosdb_client.close()
        print("Cosmos DB client connection closed.")

# Run the async main function
asyncio.run(main())
