from promptflow import tool
from cosmosdbservice import CosmosConversationClient
import asyncio
import uuid
import config

# Azure Cosmos DB configuration
COSMOSDB_ENDPOINT = config.settings['host']
COSMOSDB_KEY = config.settings['master_key']
DATABASE_NAME = config.settings['database_id']
CONTAINER_NAME = config.settings['container_id']

@tool
def save_to_cosmos(user_id: str, message_content: str, conversation_id: str = None, role: str = "user") -> dict:
    """
    Save a message to the Cosmos DB, creating a conversation if necessary.
    
    Args:
        user_id (str): Unique identifier for the user.
        message_content (str): Content of the message.
        conversation_id (str): Unique identifier for the conversation (can be None for new conversations).
        role (str): Role of the sender (default is "user").
        
    Returns:
        dict: Contains status, conversation_id, and details of the saved message.
    """

    async def save_message():
        # Initialize the CosmosConversationClient
        client = CosmosConversationClient(
            cosmosdb_endpoint=COSMOSDB_ENDPOINT,
            credential=COSMOSDB_KEY,
            database_name=DATABASE_NAME,
            container_name=CONTAINER_NAME,
            enable_message_feedback=True
        )

        # Ensure the client is set up correctly
        is_ready, message = await client.ensure()
        if not is_ready:
            await client.cosmosdb_client.close()
            return {"status": f"Error initializing Cosmos DB client: {message}"}

        try:
            # Create a new conversation if no conversation_id is provided
            local_conversation_id = conversation_id  # Use a local variable for assignment
            if not local_conversation_id:
                new_conversation = await client.create_conversation(user_id=user_id, title="New Conversation")
                local_conversation_id = new_conversation["id"]  # Assign the new conversation ID
            
            # Create a message
            message_id = str(uuid.uuid4())  # Generate a unique ID for the message
            input_message = {
                "role": role,
                "content": message_content
            }
            created_message = await client.create_message(
                uuid=message_id,
                conversation_id=local_conversation_id,
                user_id=user_id,
                input_message=input_message
            )
            return {
                "status": "Message saved successfully",
                "conversation_id": local_conversation_id,  # Return the conversation ID
                "message": created_message
            }

        except Exception as e:
            return {"status": f"Error saving message: {str(e)}"}

        finally:
            # Ensure the Cosmos DB client connection is closed
            await client.cosmosdb_client.close()

    # Run the async save_message function
    result = asyncio.run(save_message())
    return result

