using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{ 
    public class InstanceProperty
    {
        public string key { get; set; }
        public object value { get; set; }
    }

    public class InstanceResponse
    {
        [JsonProperty("id")] public string Id { get; set; }
        [JsonProperty("name")] public string Name { get; set; }
        [JsonProperty("type")] public string Type { get; set; }
        [JsonProperty("properties")] public List<InstanceProperty> Properties { get; set; }
        [JsonProperty("processes")] public object Processes { get; set; }
    
    }
}