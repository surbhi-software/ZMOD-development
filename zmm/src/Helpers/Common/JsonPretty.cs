using Newtonsoft.Json.Linq;

namespace ZMM.Helpers.Common
{
    public static class JsonPretty
    {
        public static JToken ConvertToJToken(string s)
        {
            if (s == null)
                return JValue.CreateNull();
            
            //parse if already a json
            if ((s.StartsWith("{") && s.EndsWith("}")) || (s.StartsWith("[") && s.EndsWith("]")))
                return JToken.Parse(s);
            
            // else create
            return JToken.FromObject(s);
        }        
    }
}