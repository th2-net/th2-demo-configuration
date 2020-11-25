# How to start:
1. Change **configs** based on your **RabbitMQ** , **act** and **check1**
    1. Fill **grpc.json** in folder **config** with host and port of your **act** and **check1** pods.
    1. Fill **mq.json** in folder **config** with **RabbitMQ exchange** and **routing key** from **script** to **estore**.
    1. Fill **rabbit.json** in folder **config** with your **RabbitMQ credentials** 
1. Install required packages described in **requirements.txt**
1. Start **AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled.py**

# Test Scenario:

1. User1 submit buy order with Price=x and Size=30 - **Order1**
    1. User1 receives an Execution Report with ExecType=0
1. User1 submit buy order with Price=x+1 and Size=10 - **Order2**
    1. User1 receives an Execution Report with ExecType=0
1. User2 submit sell IOC order with price=x-1 and Size=100 - **Order3**
    1. User1 receives an Execution Report with ExecType=F on trade between **Order2** and **Order3**
    1. User2 receives an Execution Report with ExecType=F on trade between **Order3** and **Order2**
    1. User1 receives an Execution Report with ExecType=F on trade between **Order1** and **Order3**
    1. User2 receives an Execution Report with ExecType=F on trade between **Order3** and **Order1**
    1. User2 receives an Execution Report with ExecType=C on expired **Order3**