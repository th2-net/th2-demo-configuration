# Scenarios:


## Main Test Scenario - branch ver-1.6.1-main_scenario:
### Suitable schema configuration:
https://github.com/th2-net/th2-infra-schema-demo/tree/ver-1.6.1-main_scenario
Updated ver-1.5.3-main_scenario.


## Main Test Scenario - branch ver-1.5.3-main_scenario:
### Suitable schema configuration:
https://github.com/th2-net/th2-infra-schema-demo/tree/ver-1.5.3-main_scenario
### Scenario:
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
   

## Main Test Scenario - branch ver-1.3.0-common2(outdated):
### Suitable schema configuration:
https://github.com/th2-net/th2-infra-schema-demo/tree/ver-1.3.0
### Scenario:
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
