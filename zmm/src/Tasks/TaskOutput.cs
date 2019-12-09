using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace ZMM.Tasks
{
    public sealed class Output : ITaskResult
    {

        public Output()
        { 

        }
        public Output(int pid)
        {
            ProcessId = pid;
            Logs = new List<string>();
            Errors = new List<string>();
            //RunTime = process.ExitTime - processStartTime;
        }
        private int ProcessId { get; set; }        
        private List<string> Logs { get; }
        private List<string> Errors { get; }
        
        public void UpdateLog(string part)
        {
            Logs.Add(part);
        }
        public void UpdateError(string part)
        {
            Errors.Add(part);
        }

        public int GetProcessId()
        {
            return ProcessId;
        }

        public List<string> GetLog()
        {
            return Logs;
        }

        public List<string> GetErrors()
        {
            return Errors;
        }

        public bool IsEmpty()
        {
            return ProcessId == 0 && Errors.Count == 0 && Logs.Count == 0;
        }
    }
}
