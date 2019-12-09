using System.Collections.Generic;

namespace ZMM.Tasks
{
    public interface ITaskResult
    {
        int GetProcessId();
        List<string> GetLog();
        List<string> GetErrors();

        bool IsEmpty();
    }
}