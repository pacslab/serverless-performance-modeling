# Workload for Serverless Performance Modeling

The python function from [faas_measure](https://github.com/liangw89/faas_measure) with minor modifications.


## Changes from the original version

Here are a few changes I have made to the original version.

### sleep and sleep_till

Here, `sleep` gives the number of milliseconds that the function should sleep, and `sleep_till` tells the function until when it should sleep. I believe this is easier to understand and use. Besides,
client and server might not be synchronized in terms of clock, so sleep adds some pre-calculated time to the request serving time.

## Original Info

There are several ways we could use it depending on which tests we want to run. You need to take a look at the original github repo to have an idea on how to use it.

Here are a few examples of how to invoke this function:

```bash
echo -n '{"cmds": {"sleep": 0}}' | sls invoke -f fmpy --log

echo -n '{"cmds": {"sleep": 0,"stat":{"argv": 1}}}' | sls invoke -f fmpy --log
```

```py
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke
import boto3

client = boto3.client('lambda')

response = client.invoke(
    FunctionName='faas-measure-py-dev-fmpy',
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=b'{"cmds": {"sleep": 0}}',
)

print(response)

# This is how we get the payload
r = response['Payload'].read()
```

Which results in an output like this:
```json
{
   "ResponseMetadata":{
      "RequestId":"d4a532ed-29b0-40be-9d69-74bf9fa49a7b",
      "HTTPStatusCode":200,
      "HTTPHeaders":{
         "date":"Tue, 18 Jun 2019 00:14:05 GMT",
         "content-type":"application/json",
         "content-length":"53",
         "connection":"keep-alive",
         "x-amzn-requestid":"d4a532ed-29b0-40be-9d69-74bf9fa49a7b",
         "x-amzn-remapped-content-length":"0",
         "x-amz-executed-version":"$LATEST",
         "x-amz-log-result":"U1RBUlQgUmVxdWVzdElkOiBkNGE1MzJlZC0yOWIwLTQwYmUtOWQ2OS03NGJmOWZhNDlhN2IgVmVyc2lvbjogJExBVEVTVApFTkQgUmVxdWVzdElkOiBkNGE1MzJlZC0yOWIwLTQwYmUtOWQ2OS03NGJmOWZhNDlhN2IKUkVQT1JUIFJlcXVlc3RJZDogZDRhNTMyZWQtMjliMC00MGJlLTlkNjktNzRiZjlmYTQ5YTdiCUR1cmF0aW9uOiAyLjA0IG1zCUJpbGxlZCBEdXJhdGlvbjogMTAwIG1zIAlNZW1vcnkgU2l6ZTogMTI4IE1CCU1heCBNZW1vcnkgVXNlZDogNTQgTUIJCg==",
         "x-amzn-trace-id":"root=1-5d082ccc-37e6618ea946686bdadd12c6;sampled=0"
      },
      "RetryAttempts":0
   },
   "StatusCode":200,
   "LogResult":"U1RBUlQgUmVxdWVzdElkOiBkNGE1MzJlZC0yOWIwLTQwYmUtOWQ2OS03NGJmOWZhNDlhN2IgVmVyc2lvbjogJExBVEVTVApFTkQgUmVxdWVzdElkOiBkNGE1MzJlZC0yOWIwLTQwYmUtOWQ2OS03NGJmOWZhNDlhN2IKUkVQT1JUIFJlcXVlc3RJZDogZDRhNTMyZWQtMjliMC00MGJlLTlkNjktNzRiZjlmYTQ5YTdiCUR1cmF0aW9uOiAyLjA0IG1zCUJpbGxlZCBEdXJhdGlvbjogMTAwIG1zIAlNZW1vcnkgU2l6ZTogMTI4IE1CCU1heCBNZW1vcnkgVXNlZDogNTQgTUIJCg==",
   "ExecutedVersion":"$LATEST"
}
```

The `x-amz-log-result` is base64 encode of the log for this invocation:

```bash
echo -n "THE_CONTENTS_OF_LOG" | base64 -d
```

Which gives us something like this:

```
START RequestId: 529d1f4f-b3ac-4cd6-92cb-4e23c6e84a85 Version: $LATEST
END RequestId: 529d1f4f-b3ac-4cd6-92cb-4e23c6e84a85
REPORT RequestId: 529d1f4f-b3ac-4cd6-92cb-4e23c6e84a85  Duration: 297.48 ms     Billed Duration: 300 ms         Memory Size: 128 MB     Max Memory Used: 55 MB
```

And in cold-starts we might have:

```
START RequestId: bdacbebe-c066-400f-bb0e-bf869f78705c Version: $LATEST
END RequestId: bdacbebe-c066-400f-bb0e-bf869f78705c
REPORT RequestId: bdacbebe-c066-400f-bb0e-bf869f78705c  Duration: 612.50 ms     Billed Duration: 700 ms         Memory Size: 128 MB     Max Memory Used: 55 MB
```
---
**1. Request time**

input:

```
{"cmds": {"sleep": 0}}
```

output:

start_time (time.time() * 1000) # end_time # (diff = start_time - end_time)

```
1560971055437.1123#1560971055437.125#0.0126953125
```

---
**2. stat**

input:

```
{"cmds": {"sleep": 0,"stat":{"argv": 1}}}
```

output:

exist_id # new_id # vm_id # inst_id # vm_priv_ip # vm_pub_ip # inst_priv_ip # uptime # cpu_info #

| name             | Description                                                                                                                                                                                                                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| exist_id, new_id | if `/tmp/inst_id.txt` exists, they are different, else, they are the same uuid4.                                                                                                                                                                                                                           |
| vm_id, inst_id   | get id of vm and instanse from `/proc/self/cgroup`                                                                                                                                                                                                                                                         |
| vm_priv_ip       | get private ip of vm                                                                                                                                                                                                                                                                                       |
| vm_pub_ip        | get vm public ip from outside from `http://ip.42.pl/raw`                                                                                                                                                                                                                                                   |
| inst_priv_ip     | private ip of instance (probably docker ip)                                                                                                                                                                                                                                                                |
| uptime           | uptime from `/proc/uptime`. The first value represents the total number of seconds the system has been up. The second value is the sum of how much time each core has spent idle, in seconds. Consequently, the second value may be greater than the overall system uptime on systems with multiple cores. |
| cpu_info         | Get cpu info from `/proc/cpuinfo`                                                                                                                                                                                                                                                                          |


```
bf059391-34f7-42b7-9f1b-97ce090b3ca3#bf059391-34f7-42b7-9f1b-97ce090b3ca3#sandbox-root-UeMFpg#sandbox-ef3135#169.254.26.61#b'3.215.183.233'#169.254.76.1#891.72,1782.32#2,Intel(R) Xeon(R) Processor @ 2.50GHz#1560971126581.375#1560971127303.3113#721.936279296875
```

---
**3. io**

input:

```
{"cmds": {"sleep": 0,"io":{"rd": 3, "size": "1kB", "cnt": 10}}}
```

| name | Description                         |
| ---- | ----------------------------------- |
| rd   | no. of rounds                       |
| size | the size of data to write each time |
| cnt  | the times to write in each round    |


(see doc of dd)

output:

total time spent, IO throughput(round 1); ... ; total time spent, IO throughput(round N) #

| name             | Description                                              |
| ---------------- | -------------------------------------------------------- |
| total time spent | total time it took for the test to finish                |
| IO throughput    | the throughput in kB/s etc. (read dd documentation test) |


Test Method:
```py
# Reading random bytes might stop any sort of caching that might occur
proc = subprocess.Popen(["dd",
                        "if=/dev/urandom",
                        "of=/tmp/ioload.log",
                        "bs=%s" % size,
                        "count=%s" % cnt,
                        "conv=fdatasync",
                        "oflag=dsync"],
                        stderr=subprocess.PIPE)
out, err = proc.communicate()
```


```
0.0407855, 245 kB/s;0.0266074, 376 kB/s;0.0451508, 221 kB/s#1560975342989.7178#1560975343169.6284#179.91064453125
```

---
**4. net**

Note that in order to use this feature, we need to install and run iperf3 server `iperf3 -s -p 5001` on a remote server in the region which is used to measure this performance.

```bash
docker run -d --restart unless-stopped --name=iperf3-server -p 5201:5201 networkstatic/iperf3 -s
```

input:

```
{"cmds": {"sleep": 0,"net":{"server_ip": "34.227.105.44", "port": 5001}}}
```

| name      | Description                 |
| --------- | --------------------------- |
| server_ip | the IP of the iperf server  |
| port      | port number of iperf server |


output:

throughput in bits, mean rtt (in microseconds), min rtt, max rtt #


```
386711509.800515,3363,2466,4440#1560978175129.0803#1560978185392.3027#10263.222412109375
```

This means a throughput of 368.7 Mbps which means about 46 MBps (`bits/1024/1024/8`).

**5. cpu**

input:

```
{"cmds": {"sleep": 0,"cpu":{"n": 10000}}}
```

calculates the following and measures the time taken (in ms):

```py
for i in range(1, n + 1):
   r *= i
```

output:

```
380.666015625#1560979247904.2852#1560979248285.0217#380.736572265625
```

**6. cpuu**

Performs cpus utilization test.

input:

```
{"cmds": {"sleep": 0,"cpuu":{"n": 1000}}}
```

output:

The timestamps recorded. Only return unique timestamps.

```
1560979522309.5725;..........;1560979522309.6077#1560979522309.5#1560979522309.8662#0.3662109375
```


## Modified Workload

```py
# Make a request
import time

cmds = {}
cmds['sleep'] = (time.time() + 30) * 1000
cmds['stat'] = {"argv": 1}
cmds['io'] = {"rd": 3, "size": "1M", "cnt": 5}
cmds['net'] = {"server_ip": "34.227.105.44", "port": 5201}
cmds['cpu'] = {"n": 10000}
cmds['cpuu'] = {"n": 3}

payload = {}
payload['cmds'] = cmds

b_payload = json.dumps(payload).encode()
print(b_payload)

response = client.invoke(
    FunctionName=func_name,
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=b_payload,
)

# This is how we get the payload
r = response['Payload'].read().decode('unicode_escape')
if r[0] == '"' and r[-1] == '"':
    r = r[1:-1]

pprint.pprint(json.loads(r))
```

Which uses the following request:

```
{"cmds": {"sleep": 1561075576760.353, "stat": {"argv": 1}, "io": {"rd": 3, "size": "1M", "cnt": 5}, "net": {"server_ip": "34.227.105.44", "port": 5201}, "cpu": {"n": 10000}, "cpuu": {"n": 3}}}
```

And gets the following output:

```
{'cpu': 396.04736328125,
 'cpuu': [1561075589536.7505, 1561075589536.7534, 1561075589536.754],
 'elapsed_time': 32296.193603515625,
 'end_time': 1561075589536.7688,
 'io': [{'speed': ' 8.5 MB/s', 'time': '0.61998'},
        {'speed': ' 9.4 MB/s', 'time': '0.5602'},
        {'speed': ' 9.7 MB/s', 'time': '0.539563'}],
 'net': {'bps': '441648195.402067',
         'maxr': '4051',
         'meanr': '2897',
         'minr': '2323'},
 'start_time': 1561075557240.5752,
 'stat': {'cpu_info': '2,Intel(R) Xeon(R) Processor @ 2.50GHz',
          'exist_id': '038b59dc-7cd3-4689-964a-d98ee74d66d6',
          'inst_id': 'sandbox-2da4a0',
          'inst_priv_ip': '169.254.76.1',
          'new_id': '038b59dc-7cd3-4689-964a-d98ee74d66d6',
          'uptime': '1035.28,2068.24',
          'vm_id': 'sandbox-root-cxm5iJ',
          'vm_priv_ip': '169.254.57.21',
          'vm_pub_ip': '34.200.242.82'}}
```


## TODO

- [X] Need to find the pattern for io.
- [X] Need to find the pattern for net.
- [X] Need to find the pattern for cpu.
- [X] Need to find the pattern for cpuu.
- [X] Need to find the pattern for sleep.
- [X] Need to find out how we can measure the cpu utilization from time.time()! (emailed, waiting for result)
   - Just sees what ratio of milliseconds are recorded using this method, assumes that is cpu utilization.

---
- [X] Need to automated deployment.
- [X] Need to invoke the function programatically from boto library.
