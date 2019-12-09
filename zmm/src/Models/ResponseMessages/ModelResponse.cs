using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{
    public class ModelResponse :BaseResponse
    {
        [JsonProperty("loaded")]
        public bool Loaded { get; set; }
        [JsonProperty("deployed")]
        public bool Deployed { get; set; }

        [JsonProperty("modelName")]
        public string ModelName{get; set;}

        [JsonProperty("dateCreated")]
        public DateTime DateCreated{get; set;}
    }
}