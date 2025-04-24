- You can use just a json file, instead of the in-memory database (depends really on the events recieved) 

- Choice 01 (the one implemented)
    - Do not update the in-memory database in the first change stream, insert in the status collection
    - In the stream listening to the history, when a new document is inserted:  
        - if the change occured from Status DOWN to another status, then: 
            - Trigger the aggregation pipeline (cummulate the sum)
        - else: 
            - Update the status in the in-memory database

- Choice 02 
    - Change the structure of the dictionnary, add a field : prev_status, as well as the previous timestamp 
    - if prev_status is DOWN: 
        - trigger the aggregation pipeline

- Attention dependany between services, SaaS is down if NaaS is down for example 