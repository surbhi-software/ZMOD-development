using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace ZMM.Tasks
{
    public static class TaskFactory
    {
        public static ITask Get(int taskType, string taskName , Tool tool, JObject input)
        {
            string tempTaskName = Regex.Replace(taskName, @"[^0-9a-zA-Z]+", "-").ToLower();
            string tempParam = tool.GetParam(taskType);
            Input tInfo = new Input(input);
            tInfo.MetaData["ToolName"] = tool.Name;
            tInfo.MetaData["TaskName"] = tempTaskName;
            tInfo.MetaData["HasWorkingDirectory"] = tool.HasWorkingDirectory().ToString();
            tInfo.MetaData["WorkingDirectory"] = tool.HasWorkingDirectory() ? tool.GetWorkingDirectory() : string.Empty;
            tInfo.MetaData["ProcessFileName"] = tool.GetPath();            
            tInfo.MetaData["ProcessArguments"] = tempParam;            
            ITask tempTask = new Task(tInfo);
            return tempTask;
        }
    }
}
