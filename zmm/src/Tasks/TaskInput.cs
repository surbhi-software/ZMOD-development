using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace ZMM.Tasks
{
    public class Input
    {

        private Dictionary<string, string> metaData;
        public Input(JObject jobject)
        {
            metaData = JsonConvert.DeserializeObject<Dictionary<string, string>>(jobject.ToString());
        }
        
        public Dictionary<string, string> MetaData { get => metaData; set => metaData = value; }

        public ProcessStartInfo GetInfo()
        {
            ProcessStartInfo startInfo = new ProcessStartInfo();
            if (HasProcessWorkingDirectory()) startInfo.WorkingDirectory = GetProcessWorkingDirectory();
            startInfo.FileName = GetProcessFileName();
            startInfo.Arguments = GetProcessArguments();
            return startInfo;
        }

        private string GetProcessWorkingDirectory()
        {
            return MetaData["WorkingDirectory"].ToString();
        }        

        private bool HasProcessWorkingDirectory()
        {
            return bool.Parse(MetaData["HasWorkingDirectory"].ToString());
        }

        private string GetProcessFileName()
        {
            return MetaData["ProcessFileName"].ToString();
        }

        private string GetProcessArguments()
        {
            return PopulateValues(MetaData["ProcessArguments"]);
        }

        private string PopulateValues(string inputString)
        {
            
            string updatedCommand = inputString;
            string keyFormat = string.Empty;
            foreach (KeyValuePair<string, string> keyValue in metaData)
            {
                keyFormat = "{" + keyValue.Key + "}";
                updatedCommand = updatedCommand.Replace(keyFormat, keyValue.Value);
            }
            return updatedCommand;
        }
    }
}
