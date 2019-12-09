using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ZMM.Tasks
{


    public class Task : ITask
    {

        Guid id;
        Input taskInfo;
        Output result;
        string logFileName;
        System.IO.StreamWriter logFile;
        CancellationTokenSource cancelToken;
        public Task()
        {

        }


        public Task(Input input)
        {
            this.id = Guid.NewGuid();           
            this.taskInfo = input;            
            this.cancelToken = new CancellationTokenSource();
            InitTaskLog();
        }

        public DateTime StartTime { get; set; }

        public int ExitCode { get; set; }
        public TimeSpan RunTime { get; set; }

        private bool isAlive = false;

        private async void RunAsync(ProcessStartInfo processStartInfo, IProgress<TaskProgessModel> progress, CancellationToken cancellationToken)
        {
            Process process;
            try
            {
                processStartInfo.UseShellExecute = false;
                processStartInfo.RedirectStandardOutput = true;
                processStartInfo.RedirectStandardError = true;
                DateTime startTime = DateTime.Now;
                int processId = 0;
                var tcs = new TaskCompletionSource<Output>();
                process = new Process
                {
                    StartInfo = processStartInfo,
                    EnableRaisingEvents = true
                };

                var standardOutputResults = new TaskCompletionSource<string[]>();
                process.OutputDataReceived += (sender, args) =>
                {
                    if (args.Data != null)
                    {
                        progress.Report(new TaskProgessModel(ProgessEvents.OnUpdateStandardOutput, args.Data));
                    }
                };

                var standardErrorResults = new TaskCompletionSource<string[]>();
                process.ErrorDataReceived += (sender, args) =>
                {
                    string errorMessage = args.Data;
                    if (errorMessage != null)
                    {
                        string tempError = errorMessage.ToLower();
                        if (tempError.Contains("error") || tempError.Contains("fail")) progress.Report(new TaskProgessModel(ProgessEvents.OnUpdateStandardError, args.Data));
                        else progress.Report(new TaskProgessModel(ProgessEvents.OnUpdateStandardOutput, args.Data));
                    }
                };

                var processStartTime = new TaskCompletionSource<DateTime>();

                process.Exited += async (sender, args) =>
                {
                    isAlive = false;
                    progress.Report(new TaskProgessModel(ProgessEvents.OnExit, process.ExitCode));
                };

                using (cancellationToken.Register(
                    () =>
                    {
                        tcs.TrySetCanceled();
                        try
                        {
                            if (!process.HasExited)
                            {      
                                isAlive = false;                          
                                process.Kill();                                
                                progress.Report(new TaskProgessModel(ProgessEvents.OnExit, process.ExitCode));
                            }
                        }
                        catch (InvalidOperationException) { }
                    }))
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    Console.WriteLine("Run Task file " + processStartInfo.FileName);
                    Console.WriteLine("Run Task args " + processStartInfo.Arguments);
                    startTime = DateTime.Now;
                    if (process.Start() == false)
                    {
                        tcs.TrySetException(new InvalidOperationException("Failed to start process"));
                        progress.Report(new TaskProgessModel(ProgessEvents.OnError, "Failed to start process", !process.HasExited, process.ExitCode));
                    }
                    else
                    {
                        try
                        {
                            startTime = process.StartTime;
                            processId = process.Id;
                            isAlive = true;
                            progress.Report(new TaskProgessModel(ProgessEvents.OnStart, processId, startTime));
                        }
                        catch (Exception ex)
                        {
                            progress.Report(new TaskProgessModel(ProgessEvents.OnError, ex.Message, !process.HasExited, process.ExitCode));
                        }
                        process.BeginOutputReadLine();
                        process.BeginErrorReadLine();
                    }
                }
            }
            catch (Exception ex)
            {
                isAlive = false;
                Console.WriteLine("Error in Process Ex " + ex.StackTrace);                
                progress.Report(new TaskProgessModel(ProgessEvents.OnError, ex.Message, false, 0));
            }
        }

        public Output Start()
        {
            StartAsync();
            while (true)
            {
                if (IsAlive()) Thread.Sleep(500);
                else break;
            }
            return this.result;
        }

        public void StartAsync()
        {
            IProgress<TaskProgessModel> pr = new Progress<TaskProgessModel>(SyncProgress);            
            System.Threading.Tasks.Task.Run(() => RunAsync(taskInfo.GetInfo(), pr, this.cancelToken.Token), this.cancelToken.Token);
        }        

        public void Stop()
        {
            this.cancelToken.Cancel();
            Process tempProcess = Process.GetProcessById(this.result.GetProcessId());
            tempProcess.Kill();
        }

        public void SyncProgress(TaskProgessModel taskProgressModel)
        {            
            switch (taskProgressModel.ProgressEvent)
            {
                case ProgessEvents.OnStart:
                    OnStart(taskProgressModel);
                    break;
                case ProgessEvents.OnUpdateStandardOutput:
                    OnUpdateStandardOutput(taskProgressModel);
                    break;
                case ProgessEvents.OnUpdateStandardError:
                    OnUpdateStandardError(taskProgressModel);
                    break;
                case ProgessEvents.OnError:
                    OnError(taskProgressModel);
                    break;
                case ProgessEvents.OnExit:
                    OnExit(taskProgressModel);
                    break;
            }
            
        }

        private void OnStart(TaskProgessModel taskProgress)
        {
            result = new Output(taskProgress.ProcessId);
            this.StartTime = taskProgress.StartTime;
            LogTask(string.Format("Start Task with Process Id : {0}, Time : {1}", taskProgress.ProcessId, this.StartTime));            
        }

        private void OnUpdateStandardOutput(TaskProgessModel taskProgress)
        {
            try
            {
                lock (result)
                {
                    result.UpdateLog(taskProgress.StandardOutputPart);
                    LogTask(taskProgress.StandardOutputPart);
                }
            }
            catch(Exception ex){}
        }

        private void OnUpdateStandardError(TaskProgessModel taskProgress)
        {
            try
            {
                lock (result)
                {
                    result.UpdateError(taskProgress.StandardErrorPart);
                    LogTask(taskProgress.StandardErrorPart);
                }
            }
            catch(Exception ex){}
        }

        private void OnError(TaskProgessModel taskProgress)
        {
            try
            {
                lock (result)
                {
                    result.UpdateLog(taskProgress.StandardErrorPart);
                    LogTask(taskProgress.StandardErrorPart);
                }
                this.ExitCode = taskProgress.ExitCode;
                this.isAlive = taskProgress.IsAlive;
            }
            catch(Exception ex){}
        }

        private void OnExit(TaskProgessModel taskProgress)
        {
            try
            {
                this.ExitCode = taskProgress.ExitCode;
                this.RunTime = DateTime.Now - this.StartTime;
                this.isAlive = false;
                LogTask(string.Format("Exit Code : {0}, RunTime : {1}", this.ExitCode, this.RunTime));
                LogTask("End Task", true);
            }
            catch(Exception ex){}
        }        

        public static ITask Empty
        {
            get
            {
                return new Task();
            }
        }

        public bool IsAlive() { return this.isAlive; }
        public Output Result { get => result; set => result = value; }

        public bool IsEmpty()
        {
            return (taskInfo == null);
        }        

        public string GetLogFile()
        {
            return this.logFileName;
        }

        private void LogTask(string logMessage, bool closeFile=false)
        {
            try
            {
                Console.WriteLine(logMessage);                
            }
            catch (Exception ex) { }
        }

        private void InitTaskLog()
        {    
            /*      
            string logDir = "tools" + Path.DirectorySeparatorChar + taskInfo.MetaData["ToolName"] + Path.DirectorySeparatorChar + "tasks";
            this.logFileName = Environment.CurrentDirectory + Path.DirectorySeparatorChar+  logDir + Path.DirectorySeparatorChar +  this.taskInfo.MetaData["TaskName"] + "-" + Path.GetRandomFileName() + ".log";
            System.IO.Directory.CreateDirectory(logDir);
            this.logFile = new System.IO.StreamWriter(this.logFileName);
             */ 
        }

        public Input GetInput()
        {
            return this.taskInfo;
        }

        public string GetName()
        {
            return this.taskInfo.MetaData["TaskName"];
        }

        public ITaskResult GetResult()
        {
            return this.result;
        }

        public void UpdateInput(string paramName, string paramValue)
        {
            taskInfo.MetaData[paramName] = paramValue;
        }

        public string GetId()
        {
            return id.ToString();
        }
    }
    
}
