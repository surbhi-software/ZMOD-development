using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{
    public class Property
    {
        [JsonProperty("key")]
        public string key { get; set; }

        [JsonProperty("value")]
        public string value { get; set; }

    }
}