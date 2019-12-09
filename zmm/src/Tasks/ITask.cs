using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;

namespace ZMM.Tasks
{
    public interface ITask
    {

        string GetName();
        Input GetInput();
        void UpdateInput(string paramName, string paramValue);
        
        string GetId();
        string GetLogFile();
        ITaskResult GetResult();
        Output Start();
        void StartAsync();
        void SyncProgress(TaskProgessModel progress);
        void Stop();
        bool IsEmpty();
        bool IsAlive();
   }
}