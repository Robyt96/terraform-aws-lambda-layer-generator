import subprocess
import shutil
import boto3
import json
import os
import logging

BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_PATH_PREFIX = os.environ['BUCKET_PATH_PREFIX']
ORGANIZATION_ID = os.environ.get('ORGANIZATION_ID', '')

# logger config
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    event structure:
    {
        "packages": [
            {
                "name": <string>,
                "version: <string>
            }
        ],
        "layer_name": <string>,
        "regions": [<string>],
        "share_with_org": Optional<bool> # default false
    }

    example:
    {
        "packages": [
            {
                "name": "boto3",
                "version": "1.34.11"
            }
        ],
        "layer_name": "boto3_1_34_11",
        "regions": ["eu-central-1"],
        "share_with_org": true
    }
    """

    packages = event["packages"]
    layer_name = event["layer_name"]
    regions = event["regions"]
    share_with_org = event.get("share_with_org", False)

    # Delete tmp folder if already exists
    tmp_folder = "/tmp/python"
    try:
        shutil.rmtree(tmp_folder)
    except:
        pass
    
    #Create standard layer directory structure (per AWS guidelines)
    zip_folder = f"{tmp_folder}/python/"
    os.makedirs(zip_folder)

    #Pip install the packages, then zip it
    for p in packages:
        complete_process = subprocess.run(f'pip3 install {p["name"]}=={p["version"]} -t {zip_folder} --no-cache-dir'.split(), capture_output=True)
        return_code = complete_process.returncode
        
        if return_code != 0:
            logger.error(complete_process.stderr)
            return {'statusCode': 500,'body': json.dumps('Error!')}
    
    shutil.make_archive(tmp_folder, 'zip', tmp_folder)
    
    #Put the zip in your S3 Bucket
    S3 = boto3.resource('s3')
    try:
        s3_key = f'{BUCKET_PATH_PREFIX}/{layer_name}/python.zip'
        logger.info(BUCKET_NAME)
        logger.info(s3_key)
        S3.meta.client.upload_file('/tmp/python.zip', BUCKET_NAME, s3_key)
        logger.info(f"Zip uploaded on S3")
    except Exception as exception:
        print(exception)
        logger.error('Oops, Exception: ', exception)
        return {'statusCode': 500,'body': json.dumps('Error!')}
    
    for region in regions:
        # publish lambda layer
        lambda_client = boto3.client('lambda', region_name=region)
        response_publish_layer = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Description=f'Created by lambda',
            Content={
                'ZipFile': open('/tmp/python.zip', 'rb').read()
            },
            CompatibleRuntimes=[
                'python3.9',
                'python3.10',
                'python3.11',
                'python3.12',
            ]
        )
        logger.info(f"Publish layer response: {json.dumps(response_publish_layer, indent=2)}")

        # grant organization permission
        if share_with_org and ORGANIZATION_ID:
            response_add_permission = lambda_client.add_layer_version_permission(
                LayerName=response_publish_layer['LayerArn'],
                VersionNumber=response_publish_layer['Version'],
                StatementId='org_permission',
                Action='lambda:GetLayerVersion',
                Principal='*',
                OrganizationId=ORGANIZATION_ID,
            )
            logger.info(f"Add layer permission response: {json.dumps(response_add_permission, indent=2)}")
        
    return {'statusCode': 200,'body': json.dumps('Success!')}
