import logging, os,sys, json, datetime, requests
from fastapi import Depends, FastAPI, Request, HTTPException
from boxsdk import JWTAuth, Client
from pyproj import Transformer

app = FastAPI()
# logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# coordinate converter from 4326 to 3857 used by ArcGIS Online
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")

# box configuration
if os.path.exists('/etc/secrets/config.json'):
    auth = JWTAuth.from_settings_file('/etc/secrets/config.json')
    client = Client(auth)
elif os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json')):
    auth = JWTAuth.from_settings_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json'))
    client = Client(auth)
else:
    raise f'box config not found'

async def root():

    logger.info("info message")
    logger.warning("warning message")
    logger.debug("debug message")
    logger.error("error message")
    logger.critical("critical message")
    return {'boxgis api runnig!'}

@app.post("/webhook")
async def webhook(request: Request):
    body_dict = await request.json()

    # get box file id and webhook details
    webhook_id = body_dict['webhook']['id']
    webhook_trigger = body_dict['trigger']
    source_id = body_dict['source']['id']
    source_type = body_dict['source']['type']

    # get box file's capture metadata for location lat\long
    if webhook_trigger == "FILE.UPLOADED":
        file_metadata = client.file(file_id=source_id).get_all_metadata()
        for instance in file_metadata:
            if '$template' in instance and instance['$template'] == 'boxCaptureV1':
                latitude,north,longitute,west = instance['location'].split(' ')
                x,y = transformer.transform(float(latitude),-float(longitute))
                file_info = client.file(source_id).get()
                created_at = f'{datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}'
                shared_link = client.file(source_id).get_shared_link(access='open')
                features = [{"attributes":{"BoxFileID" : source_id,"SharedLink":shared_link, "FileName":file_info.name,"CreatedDate":created_at, "WebhookID":webhook_id, "WebhookTrigger":webhook_trigger},
                            "geometry" : {"x" : x,"y" : y}}]

                response = requests.post('https://services8.arcgis.com/ztWuThaRbt3zCysN/arcgis/rest/services/BoxCaptureData_gdb/FeatureServer/0/addFeatures?f=json', 
                                        data={"features": json.dumps(features)})

                logger.debug(f"arcgis_add_features_response:{response}")
    elif webhook_trigger == "FILE.TRASHED":
        response = requests.post('https://services8.arcgis.com/ztWuThaRbt3zCysN/arcgis/rest/services/BoxCaptureData_gdb/FeatureServer/0/deleteFeatures?f=json', 
                                data={"where": f'BoxFileID={source_id}'})

        logger.debug(f"arcgis_delete_features_response:{response}")

    return  {"success": True}



