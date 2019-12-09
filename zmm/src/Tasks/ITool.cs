using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Text;

namespace ZMM.Tasks
{
    interface ITool
    {

        IConfiguration GetConfiguration();
        string GetPath();
        string GetParam();
        string GetParam(int ToolTaskType);

        string GetWorkingDirectory();

        bool HasWorkingDirectory();

        void StartTaskAsync(int taskType, string taskName, JObject info);

        Output StartTask(int taskType, string taskName, JObject info);

        ITask FindTask(string search);

        void StopTask(string search);

        void AddTask(string taskName, ITask task);

        List<ITask> ListTasks();


    }
}
