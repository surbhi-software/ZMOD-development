using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{
    public class BaseResponse
    {        
        [JsonProperty("id")] public string Id { get; set; }
        [JsonProperty("name")] public string Name { get; set; }
        [JsonProperty("user")] public string User { get; set; }
        [JsonProperty("created_on")] public string Created_on { get; set; }
        [JsonProperty("edited_on")] public string Edited_on { get; set; }
        [JsonProperty("type")] public string Type { get; set; }
        [JsonProperty("url")] public string Url { get; set; }
        [JsonProperty("filePath")] public string FilePath { get; set; }
        [JsonProperty("size")] public long Size { get; set; }
        [JsonProperty("mimeType")] public string MimeType { get; set; }
        [JsonProperty("extension")] public string Extension { get; set; }
        [JsonProperty("properties")] public List<Property> Properties { get; set; }
    }
}