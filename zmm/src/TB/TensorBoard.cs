using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Text;
using Newtonsoft.Json.Linq;
using ZMM.Tasks;

namespace ZMM.Tools.TB
{

    public enum TaskTypes
    {
        Start,
        List,
        Stop,
        Kill
    }
    public class TensorBoard : Tool
    {
        protected static string HostURL = "http://localhost";

        protected static string DataLogParentDirectory = string.Empty;

        //We can add this to configuration
        private static List<int> ListOfAllowedPorts = new List<int> { 6006, 6007, 6008 };

        public TensorBoard(string Host, string dataDirectory) : base(ToolTypes.TensorBoard, Host.Contains("https")) 
        {
            HostURL = Host;
            DataLogParentDirectory = dataDirectory + System.IO.Path.DirectorySeparatorChar + "logs";
        }

        public void StartTaskAsync(int taskType, string taskName, JObject info)
        {
            switch ((TaskTypes)taskType)
            {
                case TaskTypes.Start:
                    ITask tempTask = FindTask(taskName);
                    if (tempTask.IsEmpty())
                    {
                        int FreePort = GetAvailablePort(ListOfAllowedPorts.First(),ListOfAllowedPorts.Last());
                        string LogDirectory = CreateNewLogDir();
                        if (FreePort > 0)
                        {
                            UpdateStartTaskInfo(ref info, FreePort, LogDirectory);
                            tempTask = TaskFactory.Get(taskType, taskName, this, info);
                            tempTask.StartAsync();
                            if (WaitForTaskToStart(tempTask, FreePort)) AddTask(tempTask.GetName(), tempTask);
                            else throw new Exception("Unable to start tensorboard. Please, contact Administrator.");
                        }
                        else throw new Exception("It reaches maximum number of allowed tensorboard instance. Please, stop previously running notebook from \"Assets\" or contact Administrator.");
                    }
                    break;
                default:
                    base.StartTaskAsync(taskType, taskName, info);
                    break;
            }
        }

        private string CreateNewLogDir()
        {
            string LogDir = DataLogParentDirectory + System.IO.Path.DirectorySeparatorChar + System.IO.Path.GetRandomFileName();
            System.IO.Directory.CreateDirectory(LogDir);
            return LogDir;
        }

        private int GetPortFromLiveTask(ITask task)
        {
            if (task.IsAlive()) return int.Parse(task.GetInput().MetaData["Port"]);
            else return -1;
        }

        private void UpdateStartTaskInfo(ref JObject info, int port, string tensorBoardDir)
        {
            info.Add("Port", port.ToString());
            info.Add("TensorBoardDir", tensorBoardDir);
        }

        private void UpdateStopTaskInfo(ref JObject info, int port)
        {
            info.Add("Port", port.ToString());
        }

        private string GetLinkPrefix(int Port)
        {
            int Index = ListOfAllowedPorts.FindIndex(x => x == Port) + 1;
            string Prefix = "/tb" + Index.ToString() + "/";
            return Prefix;
        }

        public string GetResourceLink(string resourcePath, out string LogDirectory)
        {
            string LinkForResource = string.Empty;
            LogDirectory = string.Empty;
            ITask task = FindTask(resourcePath);
            if (!task.IsEmpty())
            {
                LogDirectory = task.GetInput().MetaData["TensorBoardDir"];
                if (task.GetInput().MetaData.ContainsKey("ResourceLink")) return task.GetInput().MetaData["ResourceLink"];
                else
                {
                    int taskPort = int.Parse(task.GetInput().MetaData["Port"]);
                    string portString = (TensorBoard.HostURL.Contains("localhost")) ? ":" + taskPort : string.Empty;
                    string linkPrefix = (TensorBoard.HostURL.Contains("localhost")) ? string.Empty : GetLinkPrefix(taskPort);
                    LinkForResource = TensorBoard.HostURL + portString + linkPrefix;
                    UpdateTask(resourcePath, task, "ResourceLink", LinkForResource);
                }
            }
            return LinkForResource;
        }


        public bool WaitForStartupMessage(ITask task)
        {
            bool Found = false;
            ITaskResult result = task.GetResult();
            if (result != null)
            {
                List<string> logs = result.GetLog();
                for (int i = 0; i < logs.Count; i++)
                {
                    if (logs[i].Contains("CTRL+C to quit"))
                    {
                        Found = true;
                        break;
                    }
                    if (i == 200) break;
                }
            }
            return Found;
        }

        private bool WaitForTaskToStart(ITask task, int TaskPort)
        {
            bool Status = WaitForStartupMessage(task);
            for (int i = 1; i < 20; i++)
            {
                if (Status) break;
                else
                {
                    if(IsPortAvailableInRange(TaskPort, ListOfAllowedPorts.First(), ListOfAllowedPorts.Last())) Console.WriteLine("Waiting for task port to start " + TaskPort);
                    else 
                    {
                        Console.WriteLine("Waiting for token id");                        
                        Status = WaitForStartupMessage(task);
                    }
                    System.Threading.Thread.Sleep(1000);
                }
            }
            System.Threading.Thread.Sleep(500);
            return Status;
        }
        
    }
}
