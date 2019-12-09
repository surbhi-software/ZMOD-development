using System.Collections.Generic;
using System.Linq;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class TaskPayload
    {
        public static List<TaskResponse> Get()
        {
            List<TaskResponse> _task = new List<TaskResponse>();
            if (GlobalStorage.TaskStorage != null)
            {
                foreach (var item in GlobalStorage.TaskStorage)
                {
                    _task.Add(item.Value);
                }
            }
            var sortDesc = _task.OrderByDescending(d => d.Created_on);
            return sortDesc.ToList();
        }
    }
}
