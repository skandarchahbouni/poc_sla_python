- Proposition 01: MongoDB + Change stream
    - MAINTENANCE Status
    - Refactor the code (move some functions to common.py), change print by logging, add description to the newly added functions
    - Grafana + Rest APi
    - Root cause analyses --> Skip
    - README file redaction (Include the risks when following this approach...)
    - What should be done, when a new source is added ... 
        - Database for each data source, or collection prefixed for each source
        - Change stream for each source 
        - What to use for the cache (json, a collection in mongoDB, )
    - Turn this into modules



    - What to use as cache (capture the current state)
        - json files
        - in memory database 
        - a collection in mongodb 
        - Comparaison study between all the approaches
            - concurrency control, consistency, and availibility 
            - The choice depends on:
                - Frequency of access.. (rest api exposing to the dashboard, as well as all the change streams)
                - Frequency of events.. Whether we can have a lot of events at the same time ... or only few events coming little by little...
                    ==> Actually we have both, few or no events at all for a long period, but when they come, 
                        the arrive at the same time. This What makes the choice harder ... 
                -  Using In-memory database, with high availibilty, is the most secure choice

- Proposition 02: Apache Flink and Kafka sink, multilevl pivoting & ffill (ffill with custom logic actually)
        - Apache flink & windowing || Redis with circular list
        - 
    - 
    - 
    - 

- Comparaison between the two propositions
    - Diffculties (Implementation & Infrastructure management)
    - Data sources addition (Extending the architecture)
    - Licences & Open source tools
    - SLA computation logic: 
        - Count of downs, where each down is counted as 15 seconds .... 
        - Duration of the downtime based on event status change ... from Dowm to another status 
    - minio vs mongodb
        - mongoDB: May be Better for time series analyses, because of the timeseries collection (optimized for timeseries analyses)
        - minio  : May be better for batch processing ...  


Insert into the event 
    - Value will be 2 or maybe something else ==> Indicating planified maintenace, from, to, comment, impacted_services [SaaS, IaaS PaaS]
                                              ==> Most likely recieve an http request to declare planified maintenance
                                                - Post (declare maintenance)
                                                    - Add a document in the maintenance collection
                                                    - Set the key of planified maintenance in the cache
                                                    - No need to have a change stream actually
                                                    -  
                                                - PUT ==> That's why we should have an updated_at field: 
                                                    - Update the document with the new end_time timestamp
                                                    - 



    - Maintenance is not that easy:
        - Should we actually capture the problem events at that time ? 
            - To discuss with tutor

        - What to do when the mainteance interval is finished, and how to capture that the maintenance was finished
            - Set up a function in python that will be triggered at that time, But consider the case when
                the end date is updated (delayed or approached), the function must be triggered at the newly configured date...
                    ==> works with whatever cache you are using ...
            - Solutions depending on the cache you are using: 
                -  For example, if using memcached as the cache system, check whther it can trigger a callback function 
                    when a key is expired 


        - What if maintenance happends in the middle of updating something ... 
        - How to set maintenance: 
            - A key in the cache, with an expired at field
        - During maintenance: 
            - What should we ignore, ignore 
            - 
        -  


- Make choices like: 
    - Whether to have a database for each data source
        - zabbix:
            - events --> change stream
            - metrics
        - prometheus: 
            - events --> change stream 
            - metrics
        - fluentd:
            - ....
        - history:
            - status
            - maintenance
    - Or may be: 
        - 
        


# --- SCHEDULED MAINTENANCE 
Maintenance (schedule a maintenance):
    - Post request:
        - Insert a document into scheduled_maintenance_history collection.
        - Setup two callback functions:
            - **Start maintenance callback**
                - For each related service to the scheduled maintenance [SaaS, BaaS, PaaS] (related services passed as argument): 
                    - Insert a document in the status_history collection, to indicate that it is in maintenance mode.
                    - Update the cache:
                        - Servies status cache: must be updated to maintenance. 
                            - Downtime: cummulate the sum in case the the status switch happened from DOWN to MAINTENANCE.
            - **End maintenance callback**
                -  For each related to the maintennace that ended (related services list passed as argument): 
                    - Call the update_service_status function, to update the status of each service in the
                        cache as well as the services status history.

    
    - PUT Request (Optional):
        - Update is only allowed if the scheduled_maintenance didn't appear yet
        - Update the related document in the database ("based on a search criterea ... comment ot start date or something else"):
            - Delete the old callbacks, and schedule two new callbacks, in this case, we covered all the  

    - DELETE Request: 
        - Delete the related document (based on a search criteria).  
        - Cancel the two callbacks related to that scheduled_maintenance.


- What to change in the code:
    - For each related service to the maintenance:
        - Before calling the update_service_status function, you should ALWAYS check first whether it is in maintenance mode or not. 
        - If it is in maintenance mode:
            - just skip the update (update_services_status history). 


- For the callback function, when the key expires: 
    - If using redis, trigger the callbak function when the key expires
    - If using memcached, this option may not be pssible
    - Else do it natively in python


maintenance_history:
    - schema:  # May be add a field to do the searches for the case of Update or DELETE
        {
            "start": xxxxxxxxxxxxx,
            "end": xxxxxxxxxxxxx,
            "related_services": ["SaaS", "IaaS", "PaaS"], 
            "description": "Patching and updates" 
        }

- The callbacks must be persisted

Edge case (VERY LOW PROBABILITY TO HAPPEN, Actually Never Happen): 
    - When executing the callback, we must call the function to update the status.
        - Imagine that at this stage OK events aren't recieved yet, if it is the case then:
            - The status will shift from maintenance to Down, before switching to another status when recieving the ok events. 
                - Maintenance --> DOWN --> UP (when recieving OK events)
        - When OK events are generated in real time 
        - This will not happen actually, this is really an edge case that will never happen, because usually when the schedule maintenance
            - They take always extra 5 or 10 or xx minutes, at this time we are sure that ok events are generated at this time. 


- Edge cases: 
    - The one related to maintenance.
    - Concurrency control (Suddenly burst of events recieved).



- Commands:
    - fastapi dev api/main.py
    - python -m change_stream.zabbix.main
    - python -m kafka_consumer.zabbix_events




- GRAFANA Threshold configuration:

    - Comoputed based on red_sla threshold, not based in maximum allowed downtime
            ==> SLA & TIME UNTILL SLA BREACH
                - Green : 98% ==> downtime from 0 up to 20 seconds ==> MAXIMUM TIME BREACH (60-20=40) ==> 40
                - Orange: 96% ==> from 20 seconds up to 40 seconds ==> MAXIMUM TIME BREACH (40,20) ==> 20
                - Base: red ==> MAXIMUM TIME BREACH (20) ==> BASE
            
    - Granted SLA is 94%, however:
        - The red color starts from below 96%

    - TOTAL_SECONDS is set to 1000 just for testing puproses and demonstration purposes 


# TODO: 
    - End to End demo (Record end to end video)
    - How to deploy it: 
        - A linux service for each terminal session? 
            - One service for kafka consumer
            - A service for the rest api
            - A service for each change_stream ... 
    - Add other grafana panels
    - Add documentation (readme file and so on ...)
    - Start making the report:
        - Current architecture study 
            - Talk espicially about the cache/current_state (what to use there ... and why ...)
            - Whether it is really necessary to use kafka or just send to the api
            - Risks (Edge cases study): Integrating new datasources, Recieving other events ... 

    - Tools selection (details)
        - Company preferences .... redis vs memcached .... OpenSearch or Another storage solution instead of mongodb
    - Integrating other datasources (prometheus, nagios) ... In depth study ...


-- compute in batch using python
- may be it would be interesting to use kafka in this case, kafka queue and read from the 
begenning of the queue... since most likely we don't have a lot of events ... 

the diffculty you may encounter is that you have several topics: 
    - zabbix.events
    - xxx.events 
    - ....


you should count using the timestamp provided in the event : 
- Refactor, move some functions to the cache
