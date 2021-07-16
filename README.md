# How to start:
Python 3.7+ environment required.
1. Change **configs** based on your **RabbitMQ** , **act** and **check1**
    1. Fill **grpc.json** in a folder **config** with the host, and the port of your **act** and **check1** pods. You can found it in Kubernetes Dashboard in Services tab or execute in kubectl - kubectl get services
    1. Fill **mq.json** in a folder **config** with **RabbitMQ exchange** and **routing key** from **script** to **estore**. You can find this queue in Kubernetes Dashboard in Config Maps tab - script-entry-point-app-config. 
    1. Fill **rabbit.json** in a folder **config** with your **RabbitMQ credentials**. You can find these credentials in Kubernetes Dashboard in Config Maps tab - rabbit-mq-app-config.
1. Install required packages described in **requirements.txt**
1. Start **run.py**

# Test Scenario:

1. User1 submit passive buy order with Price=x and Size=30 - **Order1**
1. User1 receives an Execution Report with ExecType=0
1. User1 submit passive buy order with Price=x+1 and Size=10 - **Order2**
1. User1 receives an Execution Report with ExecType=0
1. User2 submit an aggressive sell IOC order with price=x-1 and Size=100 - **Order3**
    1. User1 receives an Execution Report with ExecType=F on trade between **Order2** and **Order3**
    1. User2 receives an Execution Report with ExecType=F on trade between **Order3** and **Order2**
    1. User1 receives an Execution Report with ExecType=F on trade between **Order1** and **Order3**
    1. User2 receives an Execution Report with ExecType=F on trade between **Order3** and **Order1**
    1. User2 receives an Execution Report with ExecType=C on expired **Order3**