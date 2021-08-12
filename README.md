# Description:
The th2-script is a code, which contains a set of requests to the th2 components, executed in turns. The script can be written in any language that supports a common library. This script is written on python and contains three general types of actions.

* Requests to **the act** (th2-act-uiframework-win-demo) for executing requests related with GUI automation from script. This act contains all logic about tested application (such as: element ids, windows, ...) 

* Requests to **the check1** for message verification based on the expected results that are executed asynchronously. This means that we are not waiting for the check to be completed.

* Sending events to **the estore** queue to organize test results into a structure, or to supplement information in the report.

## How to start:
**Schema(th2 environment) needed:** https://github.com/th2-net/th2-infra-schema-demo/tree/ver-1.5.4-hand_win_scenario

Python 3.7+ environment required.
1. Change **configs** based on your **RabbitMQ** , **act** and **check1**
    1. Fill **grpc.json** in a folder **config** with the host, and the port of your **act** and **check1** pods. You can found it in Kubernetes Dashboard in Services tab or execute in kubectl - kubectl get services
    1. Fill **mq.json** in a folder **config** with **RabbitMQ exchange** and **routing key** from **script** to **estore**. You can find this queue in Kubernetes Dashboard in Config Maps tab - script-entry-point-app-config. 
    1. Fill **rabbitMQ.json** in a folder **config** with your **RabbitMQ credentials**. You can find these credentials in Kubernetes Dashboard in Config Maps tab - rabbit-mq-app-config.
    1. Fill **custom.json** in a folder **config** with following options:
        1. **target_server_win** - alias to box with installed WinAppDriver and MiniFix application. Should be the same that in th2-hand config 
        1. **application_folder** and **exec_file** - path and executable file to MiniFix application installed on target box
        1. **sender_comp_id** and **target_comp_id** - fields in FIX message.
        1. **fix_server_host** and **fix_server_port** - host and port of fix server
1. Install required packages described in **requirements.txt**
1. Start **run_hand_win.py**

## Test Scenario:

1. Opening the MiniFIX application thought WinAppDriver. Executable file is specified in config file custom.json.
1. Connecting the MiniFix application to System (simulator).
1. Sending an order to simulator with specified parameters.
1. Extracting displayed FIX message (pipe-separated) and sending it to codecs.
1. Checking displayed FIX message against:
    1. Expected parameters from script
    1. Parsed message from table displayed in GUI
    1. Incorrect expected parameters from scipt (failed)
1. Disconnecting in MiniFix from System
1. Closing the application



