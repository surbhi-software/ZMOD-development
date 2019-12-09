using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using System.Linq;
using System.Threading.Tasks;
using System;
using System.Diagnostics;
using System.IO;
using ZMM.Tasks;
using Microsoft.Extensions;
using TaskFactory = ZMM.Tasks.TaskFactory;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;


/// <summary>
/// see bottom of file for developer notes
/// </summary>
namespace ZMM.Tools.JNB
{
    
    public  enum TaskTypes
    {
        Start,
        List,
        Stop,
        Kill
    } 

    public class JupyterNotebook : Tool
    {

        
        protected static string HostURL = "http://localhost";

        private const string  TokenPattern = "?token=";

        //We can add this to configuration
        private static List<int> ListOfAllowedPorts = new List<int> { 8888, 8889, 8890 };

        public JupyterNotebook(string Host) : base(ToolTypes.JupyterNotebook, Host.Contains("https")) 
        {
             HostURL = Host;
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
                        if (FreePort > 0)
                        {
                            UpdateStartTaskInfo(ref info, FreePort);
                            tempTask = TaskFactory.Get(taskType, taskName, this, info);
                            tempTask.StartAsync();
                            string token = WaitForStartTaskToken(tempTask, FreePort);
                            if(token.Equals(string.Empty)) throw new Exception("Something went wrong. Jupyter notebook cannot be started. Try again.");
                            tempTask.UpdateInput("Token", token);
                            AddTask(tempTask.GetName(), tempTask);                            
                        }
                        else throw new Exception("It reaches maximum number of allowed jupyter notebook instance. Please, stop previously running notebook from \"Assets\" or contact Administrator.");
                    }
                    break;
                default:
                    base.StartTaskAsync(taskType, taskName, info);
                    break;                
            }
            
        }
        

        private int GetPortFromLiveTask(ITask task)
        {
            if (task.IsAlive()) return int.Parse(task.GetInput().MetaData["Port"]);
            else return -1;
        }

        private void UpdateStartTaskInfo(ref JObject info, int port)
        {
            string NotebookConfigFile = Environment.CurrentDirectory + System.IO.Path.DirectorySeparatorChar + "config" + System.IO.Path.DirectorySeparatorChar  + "zementis.notebook.config.py";
            string NotebookCertFile = Environment.CurrentDirectory + System.IO.Path.DirectorySeparatorChar + "config" + System.IO.Path.DirectorySeparatorChar  + "zmm.jnb.pem";
            string NotebookKeyFile = Environment.CurrentDirectory + System.IO.Path.DirectorySeparatorChar + "config" + System.IO.Path.DirectorySeparatorChar  + "zmm.jnb.key";
            string LinkPrefixString = GetLinkPrefix(port);
            bool IsProductionEnvironment = !HostURL.Contains("localhost");
            info.Add("Port", port.ToString());
            info.Add("NotebookConfigFile", NotebookConfigFile);
            info.Add("LinkPrefix", LinkPrefixString);
            info.Add("NotebookCertFile", NotebookCertFile);
            info.Add("NotebookKeyFile", NotebookKeyFile);
        }

        private void UpdateStopTaskInfo(ref JObject info, int port)
        {
            info.Add("Port", port.ToString());
        }

        private string GetLinkPrefix(int Port)
        {
            int Index = ListOfAllowedPorts.FindIndex(x => x == Port) + 1;
            string Prefix = "/jnb" + Index.ToString();
            return Prefix;
        }

        public string GetResourceLink(string resourcePath)
        {
            string LinkForResource = string.Empty;
            ITask task = FindTask(resourcePath);
            if (!task.IsEmpty())
            {
                if (task.GetInput().MetaData.ContainsKey("ResourceLink")) return task.GetInput().MetaData["ResourceLink"];
                else
                {
                    string RelativeNotebookPath = task.GetInput().MetaData["ResourcePath"].Substring(task.GetInput().MetaData["NotebookDir"].Length + 1);
                    int taskPort = int.Parse(task.GetInput().MetaData["Port"]);
                    //As It is internally reverse proxy so no need to , Need to find ZMM
                    string portString = (JupyterNotebook.HostURL.Contains("localhost")) ? ":" + 7007 : string.Empty; 
                    LinkForResource = JupyterNotebook.HostURL + portString + GetLinkPrefix(taskPort) + "/notebooks/" + RelativeNotebookPath + "?token=" + GetToken(task);
                    UpdateTask(resourcePath, task, "ResourceLink", LinkForResource);
                }
            }
            return LinkForResource;
        }

       

        private string GetToken(ITask task)
        {
            string tokenId = string.Empty;
            ITaskResult result = task.GetResult();
            if (result != null)
            {
                List<string> logs = result.GetLog();
                for (int i = 0; i < logs.Count; i++)
                {
                    if (logs[i].Contains(TokenPattern))
                    {
                        tokenId = logs[i].Substring(logs[i].IndexOf(TokenPattern) + 7);
                        break;
                    }
                    if (i == 200) break;
                }
            }
            return tokenId;
        }

        private string WaitForStartTaskToken(ITask task, int TaskPort)
        {            
            string tokenId = GetToken(task);
            for (int i = 1; i < 50; i++)
            {
                if (tokenId != string.Empty) break;
                else
                {
                    if(IsPortAvailableInRange(TaskPort, ListOfAllowedPorts.First(), ListOfAllowedPorts.Last())) Console.WriteLine("Waiting for task expected port " + TaskPort + "  to start"); 
                    else 
                    {
                        Console.WriteLine("Waiting for token id...");                        
                        tokenId = GetToken(task);
                    }
                    System.Threading.Thread.Sleep(500);
                }
            }
            System.Threading.Thread.Sleep(1000);
            return tokenId;
        }
        
    }
}
