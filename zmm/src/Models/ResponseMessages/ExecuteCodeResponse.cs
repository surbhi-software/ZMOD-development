using System;
using System.Collections.Generic;

namespace ZMM.Models.ResponseMessages
{
    public class Information
    {
        public string property { get; set; }
        public List<object> value { get; set; }
    }

    public class ExecuteCodeResponse
    {
        public string idforData { get; set; }
        public string status { get; set; }
        public string createdOn { get; set; }
        public string type { get; set; }
        public long pid { get; set; }
        public string newPMMLFileName { get; set; }
        public List<Information> information { get; set; }
        public string taskName { get; set; }
        public DateTime executedAt { get; set; }
    }
}