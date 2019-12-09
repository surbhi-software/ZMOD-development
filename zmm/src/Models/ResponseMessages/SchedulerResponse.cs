using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{
    public class SchedulerResponse
    {        
        [JsonProperty("id")] public string Id { get; set; }
        [JsonProperty("name")] public string Name { get; set; }        
        [JsonProperty("createdOn")] public string CreatedOn { get; set; }
        [JsonProperty("editedOn")] public string EditedOn { get; set; }
        [JsonProperty("type")] public string Type { get; set; }
        [JsonProperty("url")] public string Url { get; set; }
        [JsonProperty("filePath")] public string FilePath { get; set; }    
        [JsonProperty("cronExpression")] public string CronExpression { get; set; }  
        [JsonProperty("startDate")] public string StartDate { get; set; }
        [JsonProperty("startTimeH")] public string StartTimeH { get; set; }    
        [JsonProperty("startTimeM")] public string StartTimeM { get; set; }
        [JsonProperty("recurrence")] public string Recurrence { get; set; }   
        [JsonProperty("zmkResponse")] public List<object> ZMKResponse { get; set; }   
        [JsonProperty("history")] public List<object> History { get; set; }
        [JsonProperty("status")] public string Status { get; set; }   
        public DateTime DateCreated{get; set;}
    }
}