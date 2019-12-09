using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace ZMM.Tasks
{

    public enum ProgessEvents
    {
        OnStart,
        OnUpdateStandardOutput,
        OnUpdateStandardError,
        OnError,
        OnExit
    }

    public class TaskProgessModel
    {        

        public TaskProgessModel(ProgessEvents pEvent, int pid, DateTime startTime)
        {
            ProcessId = pid;
            StartTime = startTime;
            IsAlive = true;
            StandardOutputPart = string.Empty;
            StandardErrorPart = string.Empty;
            ExitCode = 0;
            ProgressEvent = pEvent;
        }
        
        public TaskProgessModel(ProgessEvents pEvent, string stdMessage)
        {
            if(pEvent == ProgessEvents.OnUpdateStandardOutput) StandardOutputPart = stdMessage;
            else StandardErrorPart = stdMessage;
            ProgressEvent = pEvent;
        }

        public TaskProgessModel(ProgessEvents pEvent, int exitCode)
        {
            ProgressEvent = pEvent;
            ExitCode = exitCode;
        }

        public TaskProgessModel(ProgessEvents pEvent, string errorMessage, bool status, int exitCode)
        {
            StandardErrorPart = errorMessage;
            IsAlive = status;
            ProgressEvent = ProgessEvents.OnError;
            ExitCode = exitCode;
        }

        public int ProcessId { get; set; }  
        public string StandardOutputPart { get; set;  }       
        
        public string StandardErrorPart { get; set; }

        public bool IsAlive { get; set; }

        public int ExitCode { get; set; }

        public DateTime StartTime { get; set; }

        public ProgessEvents ProgressEvent { get; set; }

        public virtual string ToString()
        {
            return string.Format("Event : {0}, Process Id : {1}, StdOutPart : {2}, StdErrorPart : {3}, IsAlive : {4}, ExitCode : {5}", ProgressEvent , ProcessId, StandardOutputPart, StandardErrorPart, IsAlive, ExitCode);
        }

    }
}
