import logging, os,sys, requests, json, datetime
from typing import Optional
from fastapi import FastAPI
from boxsdk import JWTAuth, Client

app = FastAPI()
# logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logger.info('API is starting up')

@app.get("/")
async def root():

    logger.info("info message")
    logger.warning("warning message")
    logger.debug("debug message")
    logger.error("error message")
    logger.critical("critical message")


    # box configuration
    if os.path.exists('/etc/secrets/config.json'):
        auth = JWTAuth.from_settings_file('/etc/secrets/config.json')
    elif os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json')):
        auth = JWTAuth.from_settings_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json'))
    else:
        return {f'config not found'}

    client = Client(auth)
    service_account = client.user().get()
    return {f'The current user ID is {service_account}'}


