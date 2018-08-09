# StatsbyggIOT

This is a PoC-project under Statsbygg summer internship. This is not meant to be a production-scale solution. 

Each use-case uses `sb_sseStream.py` to stream live sensor data from the edge. All use-cases have been developed at their very own branch. Each use-case's logic is described in the top of the source file.

Secrets are not included in the project. Please refer to the project owner for secrets. 

There are a few notes about the components in this project that need to be clarified.

## Azure function ##

The Azure function inserts only temperature values. The code works like a guide to process other types of sensor data as well. Simply add another `case` under `switch (eventType)` and implement the rest of the functionality. The function hibernates after a few minutes. This is due to the pricing plan in Microsoft Azure. After some research, we believe someone with elevated permissions needs to change the pricing plan to `dedicated App Service Plan`. However, due to limited access, we are not absolutely sure this is the problem.

## Query function ##
The query generator is not entierly complete. DT API claims that a call to `/projects/{project}/devices/{device}/events` will return a `next_page_token` together with the sensor data. When developing the `query generator/sb_query_generator.py`, `next_page_token` was not present in the JSON response. Because of this, the response from DT only contains at most 1000 data points per sensor. The earilest data point is 22th of July. We know for certainty that there are data points registered prior to this date. Please refer to `query generator/data_fetch_config.json` to adjust the parameters. 

## JSON configuration files ##
Common for all JSON files is that you need to add key-value pairs for adjusting the behaviour of the scripts in the `usecases` directory. Refer to the DT documentation for parameters passed in HTTP requests, as they should be specified in JSON files and not in-line in the code. 
