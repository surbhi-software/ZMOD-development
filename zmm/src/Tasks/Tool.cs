using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;

namespace ZMM.Tasks
{

    public enum ToolTypes
    {
        JupyterNotebook,
        TensorBoard
    }

    public class Tool : ITool
    {

        string name = string.Empty;
        IConfiguration configuration;
        private Dictionary<string, ITask> tasks = new Dictionary<string, ITask>();
        private bool WithHTTPSConfiguration = false;
        string path;
        string param;
        string workingDirectory;
        bool hasWorkindDirectory = false;
        
        public Tool(ToolTypes name, bool HTTPSConfiguration)
        {
            this.name = name.ToString();
            WithHTTPSConfiguration = false;
            Init();
        }

        private void Init()
        {
            string toolName = this.Name.ToString();
            ConfigurationBuilder configurationBuilder = new ConfigurationBuilder();                   
            var tempPath = "tools" + System.IO.Path.DirectorySeparatorChar + "tools.config.json";
            if(WithHTTPSConfiguration)  tempPath = "tools" + System.IO.Path.DirectorySeparatorChar + "tools.config.with.https.certificate.json";
            configurationBuilder.AddJsonFile(tempPath, false);
            var root = configurationBuilder.Build();
            this.configuration = root.GetSection(this.Name);
            this.path = this.configuration["Path"];
            this.param = this.configuration["Param"];
            string hasWorkingDir = this.configuration["HasWorkingDirectory"];
            this.hasWorkindDirectory = bool.Parse(hasWorkingDir == null ? "false" : hasWorkingDir);
            this.workingDirectory = this.hasWorkindDirectory ? this.configuration["WorkingDirectory"] : string.Empty;
            Console.WriteLine("Tool initializing " + toolName + " with configuration : " + this.path);
        }

        public string Name { get => name; set => name = value; }

        public string GetParam()
        {
            return this.param;
        }

        public string GetPath()
        {
            return this.path;
        }

        public string GetParam(int ToolTaskType)
        {
            string tempCommand = "Command." + ToolTaskType + ".Value";
            return this.param + "  " + this.configuration[tempCommand]; 
        }        

        public void StartTaskAsync(int taskType, string taskName ,JObject info)
        {           
            ITask tempTask = TaskFactory.Get(taskType, taskName, this, info);
            tempTask.StartAsync();
            AddTask(tempTask.GetName(), tempTask);
        }

        public Output StartTask(int taskType, string taskName, JObject info)
        {
            Output result;
            string tempTaskName = Regex.Replace(taskName, @"[^0-9a-zA-Z]+", "-");
            ITask tempTask = TaskFactory.Get(taskType, tempTaskName, this, info);
            result = tempTask.Start();
            AddTask(tempTaskName, tempTask);
            return result;
        }

        public Dictionary<string, ITask> GetTasks()
        {
            return tasks;
        }

        public ITask FindTask(string search)
        {
            ITask taskFound = Task.Empty;
            string sanitizedSearchInput = Regex.Replace(search, @"[^0-9a-zA-Z]+", "-").ToLower();
            if (tasks.ContainsKey(sanitizedSearchInput)) 
            {                
                if(DoRefreshAndCheckTaskAlive(tasks[sanitizedSearchInput])) taskFound = tasks[sanitizedSearchInput];
            }
            return taskFound;
        }

        private bool DoRefreshAndCheckTaskAlive(ITask task)
        {
            bool Status = true;
            if(!task.IsAlive()) 
            {
                tasks.Remove(task.GetName());
                Status = false;
            }
            return Status;
        }

        public void StopTask(string search)
        {
            ITask interestedTask = FindTask(search);
            if (!interestedTask.IsEmpty())
            {
                interestedTask.Stop();
                RemoveTask(search);
            }
        }

        public string GetWorkingDirectory()
        {
            return this.workingDirectory;
        }

        public bool HasWorkingDirectory()
        {
            return this.hasWorkindDirectory;
        }

        public void AddTask(string taskName, ITask task)
        {
            string sanitizedTaskName = Regex.Replace(taskName, @"[^0-9a-zA-Z]+", "-").ToLower();
            tasks[sanitizedTaskName] = task;
        }

        public void UpdateTask(string taskName, ITask task, string paramName, string paramValue)
        {
            task.UpdateInput(paramName, paramValue);
            AddTask(taskName, task);
        }

        public List<ITask> ListTasks()
        {
            List<ITask> list = new List<ITask>();
            list.AddRange(tasks.Values);
            return list;
        }

        public void RemoveTask(string taskName)
        {
            string sanitizedTaskName = Regex.Replace(taskName, @"[^0-9a-zA-Z]+", "-").ToLower();
            if (tasks.ContainsKey(sanitizedTaskName)) tasks.Remove(sanitizedTaskName);
        }

        public IConfiguration GetConfiguration()
        {
            return this.configuration;
        }

        public int GetAvailablePort(int StartingPortInRange, int EndingPortInRange)
        {
            List<int> PortArray = GetAvailablePortInRange(StartingPortInRange,EndingPortInRange);
            for (int i = StartingPortInRange; i<= EndingPortInRange; i++)
            {    
                if (!PortArray.Contains(i))
                    return i;
            }
            return 0;
        }

        private List<int> GetAvailablePortInRange(int StartingPortInRange, int EndingPortInRange)
        {
            IPEndPoint [] EndPoints;
            List<int> PortArray = new List<int>();
            try
            {
                IPGlobalProperties Properties = IPGlobalProperties.GetIPGlobalProperties();
                // getting active connections 
                TcpConnectionInformation[] Connections = Properties.GetActiveTcpConnections();
                PortArray.AddRange(from n in Connections
                                    where n.LocalEndPoint.Port >= StartingPortInRange
                                    select n.LocalEndPoint.Port);

                // getting active tcp listeneres - wcf service Listening in tcp
                EndPoints = Properties.GetActiveTcpListeners();
                PortArray.AddRange(from n in EndPoints
                                    where n.Port >= StartingPortInRange
                                    select n.Port);

                PortArray.Sort();
            }
            catch(Exception ex)
            {
                System.Console.Error.WriteLine(ex.StackTrace);
            }
            return PortArray;
        }
        public bool IsPortAvailableInRange(int TestPort, int StartingPortInRange, int EndingPortInRange)
        {
            bool Status = false;
            List<int> PortArray = GetAvailablePortInRange(StartingPortInRange,EndingPortInRange);
            Status = !PortArray.Contains(TestPort);
            Console.WriteLine("IsPortAvailableInRange " + StartingPortInRange + " , " + EndingPortInRange + "  : " + string.Join(',', PortArray) + "  Out : " + Status);
            return Status;            
        }
    }
}
