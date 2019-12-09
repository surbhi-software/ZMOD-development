using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{
    public class ZSSettingResponse
    {
        [JsonProperty("zmodId")] public string ZmodId { get; set; }
        [JsonProperty("settings")] public List<SettingProperty> Settings { get; set; }
    }

    public class SettingProperty
    {
        [JsonProperty("name")] public string name { get; set; }
        [JsonProperty("type")] public string type { get; set; }
        [JsonProperty("tenantID")] public string tenantID { get; set; }
        [JsonProperty("username")] public string username { get; set; }
        [JsonProperty("password")] public string password { get; set; }
        [JsonProperty("url")] public string url { get; set; }
        [JsonProperty("selected")] public bool selected { get; set; }
    }    
}