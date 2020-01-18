# Eveything we need to deploy a lambda function
import logging
from zipfile import ZipFile
import boto3
import os
import time
from botocore.exceptions import ClientError

client = None
default_zip_path = os.path.join(os.getcwd(), "pacsltk-tmp.zip")


def initialize(new_client):
    global client
    client = new_client

def zip_code(zip_name, code_path):
    """
    Zip the source function files to a deployment package
    """
    with ZipFile(zip_name, 'w') as lambda_zip:
        if not os.path.isdir(code_path):
            lambda_zip.write(code_path)
        else:
            for root, dirs, fs in os.walk(code_path):
                for f in fs:
                    abs_path = os.path.join(root, f)
                    if '.serverless' not in abs_path and '__pycache__' not in abs_path \
                            and '.gitignore' not in abs_path:
                        lambda_zip.write(abs_path, os.path.join(
                            root.replace(code_path, ''), f))


def deploy_function(func_name, func_handler, memory, role, code_path, runtime, zipped_code_path=default_zip_path):
    assert client is not None, "You need to initialize client first!"

    src_code_path = os.path.join(os.getcwd(), code_path)
    # print("deploying:", src_code_path)
    zip_code(zipped_code_path, src_code_path)

    src_file = zipped_code_path
    try:
        with open(src_file, 'rb') as zip_blob:
            response = client.create_function(
                Code={'ZipFile': zip_blob.read()},
                Description='',
                FunctionName=func_name,
                Handler=func_handler,
                MemorySize=memory,
                Publish=True,
                Role=role,
                Runtime=runtime,
                Timeout=300,
            )

            return True

    except ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]
        if status == 404:
            logging.warning("Missing object, %s", errcode)
        elif status == 403:
            logging.error("Access denied, %s", errcode)
        elif status == 409:
            logging.error("Resource Conflict, %s", errcode)
        else:
            logging.exception("Error(%s) in request, %s", status, errcode)

        return False


def delete_function(func_name):
    assert client is not None, "You need to initialize client first!"

    try:
        response = client.delete_function(FunctionName=func_name)
        return True

    except ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]
        if status == 404:
            logging.warning("Missing object, %s", errcode)
        elif status == 403:
            logging.error("Access denied, %s", errcode)
        else:
            logging.exception("Error(%s) in request, %s", status, errcode)

        return False
