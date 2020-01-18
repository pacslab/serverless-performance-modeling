# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke
import boto3
import json

import pprint

pp = pprint.PrettyPrinter(indent=4)

client = boto3.client('lambda')

cmds = {}
cmds['sleep'] = 0
cmds['stat'] = {"argv": 1}
cmds['io'] = {"rd": 3, "size": "1M", "cnt": 10}
cmds['net'] = {"server_ip": "34.227.105.44", "port": 5001}
cmds['cpu'] = {"n": 10000}
# cmds['cpuu'] = {"n": 1000}

payload = {}
payload['cmds'] = cmds

response = client.invoke(
    FunctionName='faas-measure-py-dev-fmpy',
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=json.dumps(payload).encode(),
)

# print(response)

# This is how we get the payload
r = response['Payload'].read().decode('unicode_escape')

pp.pprint(json.loads(r[1:-1]))