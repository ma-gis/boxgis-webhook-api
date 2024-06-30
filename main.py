import logging, os, requests, json, datetime
from typing import Optional
from fastapi import FastAPI
from boxsdk import JWTAuth, Client

app = FastAPI()


@app.get("/")
async def root():

    # box configuration
    if os.path.exists('/etc/secrets/config.json'):
        return {f'config json found in secrets'}
    #     auth = JWTAuth.from_settings_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json'))
    # client = Client(auth)
    # service_account = client.user().get()
    #return {f'The current user ID is {service_account}'}
    return {f'config json not found in secrets'}

