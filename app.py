
import streamlit as st
from azure.core.exceptions import ClientAuthenticationError
import requests
import json
import ssl
from cosmosdb import create_user_chat_history_container, save_user_chat, get_user_chat_history
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
import config
import pandas as pd
import os
from msal import PublicClientApplication

import webbrowser
from msal import PublicClientApplication

# Register Edge as the default browser using the system alias "msedge"
webbrowser.register('edge', None, webbrowser.BackgroundBrowser("msedge"))


import os

# Load environment variables from the .env file
load_dotenv()

client_id = os.getenv("client_id")
tenant_id = os.getenv("tenant_id")



app = PublicClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

def authenticate_user():
    try:
        print("Starting authentication with MSAL PublicClientApplication...")

        # Check the cache for available accounts
        accounts = app.get_accounts()
        result = None

        if accounts:
            print("Accounts found in cache. Using the first available account.")
            chosen_account = accounts[0]
            result = app.acquire_token_silent(["User.Read"], account=chosen_account)

        # If no cached token, initiate interactive login
        if not result:
            print("No token in cache, prompting for interactive sign-in.")
            result = app.acquire_token_interactive(scopes=["User.Read"])

        # Debugging: Print the result to check for the token
        print("Authentication result:", result)

        # Process the result
        if "access_token" in result:
            token = result["access_token"]
            print("Token retrieved successfully.")
            user_info = get_user_info(token)
            if user_info:
                print("User info retrieved:", user_info)
                return user_info
            else:
                print("Failed to retrieve user info.")
                return None
        else:
            print("Authentication failed:", result.get("error"))
            print("Error description:", result.get("error_description"))
            return None
    except Exception as e:
        print("An unexpected error occurred during authentication:", str(e))
        return None

def get_user_info(token):
    graph_api_url = 'https://graph.microsoft.com/v1.0/me'  # User-specific endpoint
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(graph_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error retrieving user info:", response.status_code, response.text)
        return None

# Allow self-signed certificates if necessary
def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)



# Streamlit session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = ''

st.title("Azure Authentication and Chat History App")

if not st.session_state.authenticated:
    if st.button("Authenticate with Azure"):
        user_info = authenticate_user()
        if user_info:
            st.session_state.authenticated = True
            st.session_state.username = user_info.get("userPrincipalName", "User")
            st.success(f"Authentication successful! Welcome, {st.session_state.username}.")
        else:
            st.error("Authentication failed! Please try again.")

if st.session_state.authenticated:
    st.write(f"Welcome, {st.session_state.username}!")

    # Add Refresh Chat History button
    if st.button("Refresh Chat History"):
        chat_history_df = get_user_chat_history(st.session_state.username)
        st.session_state.chat_history = chat_history_df if not chat_history_df.empty else pd.DataFrame()
    
    # Display Chat History if available
    if 'chat_history' in st.session_state and not st.session_state.chat_history.empty:
        st.write("Chat History")
        st.table(st.session_state.chat_history)
    else:
        st.write("No chat history found for this user.")

    conversation = st.text_area("Enter your message here:")
    if st.button("Submit"):
        save_user_chat(st.session_state.username, conversation)
        st.success("Conversation saved successfully.")
