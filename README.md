# Description:
The th2-script is a code, which contains a set of requests to the th2 components, executed in turns. The script can be written in any language that supports a common library. This script is written on python and contains three general types of actions.

* Requests to **the act** (th2-act-uiframework-web-demo) for executing requests related with GUI automation from script. This act contains all logic about tested application (such as: element ids, windows, ...) 

* Requests to **the check1** for message verification based on the expected results that are executed asynchronously. This means that we are not waiting for the check to be completed.

* Sending events to **the estore** queue to organize test results into a structure, or to supplement information in the report.

## How to start:
**Schema(th2 environment) needed:** https://github.com/th2-net/th2-infra-schema-demo/tree/ver-1.5.4-hand_web_scenario

Python 3.7+ environment required.
1. Change **configs** based on your **RabbitMQ** , **act** and **check1**
    1. Fill **grpc.json** in a folder **config** with the host, and the port of your **act** and **check1** pods. You can found it in Kubernetes Dashboard in Services tab or execute in kubectl - kubectl get services
    1. Fill **mq.json** in a folder **config** with **RabbitMQ exchange** and **routing key** from **script** to **estore**. You can find this queue in Kubernetes Dashboard in Config Maps tab - script-entry-point-app-config. 
    1. Fill **rabbitMQ.json** in a folder **config** with your **RabbitMQ credentials**. You can find these credentials in Kubernetes Dashboard in Config Maps tab - rabbit-mq-app-config.
    1. Fill **custom.json** in a folder **config** with following options:
        1. **target_server_web** - alias to box with installed selenium server, browser and selenium driver. Should be 
        the same that in th2-hand config.
        All of them can be installed locally or in k8s.
1. Install required packages described in **requirements.txt**
1. Start **run_hand_web.py**

## Test Scenario:

###### Test case 1
1. Going to act-ui page.
1. Filling service parameters
1. Filling body message parameters
1. Sending message via act-ui.
1. Extracting link to rpt-viewer with act-ui result
1. Extracting sent via act-ui message from rpt-viewer
1. Searching response message in rpt-viewer and extracting it
1. Checking sent message with expected parameters in script
1. Checking response message with expected parameters in script

###### Test case 2
The same as *Test case 1* but filling not existing service parameters. `act-ui` doesn't send any message. This test case
 will be failed, because there is no result link.

###### Test case 3
The same as *Test case 1* but there are expected params that are used in comparison have errors. This test case will be 
failed in verification step.
