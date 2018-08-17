#r "System.Configuration"
#r "System.Data"
#r "Newtonsoft.Json"

using System.Configuration;
using System.Data.SqlClient;
using System.Threading.Tasks;
using System.Net;
using Newtonsoft.Json.Linq;
using System.Text.RegularExpressions;

public static async Task<HttpResponseMessage> Run(HttpRequestMessage req, TraceWriter log)
{
    log.Info("C# HTTP trigger function processed a request.");

    dynamic body = await req.Content.ReadAsAsync< object >();
    string eventID = null;
    string targetName = null;
    string temp = null;
    string timestamp = null;
    string eventType = null;
    string sensorName = null;
    string filepath = @"D:\home\site\wwwroot\HttpTriggerCSharp1\sensors.json";
    JObject jobj = null;

    string result = string.Empty;
    using (StreamReader r = new StreamReader(filepath)) {
        var json = r.ReadToEnd();
        jobj = JObject.Parse(json);
        r.Close();
   } 

    try {
        eventID = body.@event.eventId;
        targetName = body.@event.targetName;
        temp = body.@event.data.temperature.value;
        timestamp = body.@event.timestamp;
        eventType = body.@event.eventType;
        sensorName = (string) jobj["sensors"][Regex.Split(targetName, "/devices/")[1]];
        log.Info((string) jobj["sensors"][Regex.Split(targetName, "/devices/")[1]]);
    } catch (Exception e) {
        return req.CreateResponse(HttpStatusCode.OK);
    } 

    /* There might not be a human-like sensor name in the config file */
    if (sensorName == null) {
        return req.CreateResponse(HttpStatusCode.OK);
    }

    float temperatureValue;
    Single.TryParse(temp, out temperatureValue);
    
    string queryString = null;
    string [] parameterNames;
    string [] parameterValues;

    switch (eventType) {
        case "temperature": 
            queryString = "INSERT INTO SB_temperature_events (eventID, sensorName, temperatureValue, datestamp) " +
                            "VALUES (@eventID, @sensorName, @temperatureValue, @timestamp);" ;
            parameterNames = new string [] { "@eventID", "@sensorName", "@temperatureValue", "@timestamp"};
            parameterValues = new string [] { eventID, sensorName, temperatureValue.ToString(), timestamp};
            break;

        default:
            log.Error( "Unsupported event type received, check Data Connector. EventType = " + eventType);
            return req.CreateResponse(HttpStatusCode.OK);    
    }

    var str = ConfigurationManager.ConnectionStrings[ "sql_connection" ].ConnectionString;
    using (SqlConnection conn = new SqlConnection(str)) {
        conn.Open();

        using (SqlCommand cmd = new SqlCommand(queryString, conn)) {
            // Add the parameters
            for ( int i = 0 ; i < parameterValues.Length; i++) {
                cmd.Parameters.AddWithValue(parameterNames[i], parameterValues[i]);
            }
            
            // Execute the command
            var rows = await cmd.ExecuteNonQueryAsync();
        }
    }
    return req.CreateResponse(HttpStatusCode.OK);
}

