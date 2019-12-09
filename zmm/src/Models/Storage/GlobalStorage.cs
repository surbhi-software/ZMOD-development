using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Text;
using ZMM.Models.ResponseMessages;

namespace ZMM.Models.Storage
{
    public static class GlobalStorage
    {
        static GlobalStorage()
        {
            DataStorage = new ConcurrentDictionary<string, DataResponse>();
            CodeStorage = new ConcurrentDictionary<string, CodeResponse>();
            ModelStorage = new ConcurrentDictionary<string, ModelResponse>();
            TaskStorage = new ConcurrentDictionary<string, TaskResponse>();
            InstanceStorage = new ConcurrentDictionary<string, InstanceResponse>();
            SchedulerStorage = new ConcurrentDictionary<string, SchedulerResponse>();
            ZSSettingStorage = new ConcurrentDictionary<string, ZSSettingResponse>();
        }
        public static ConcurrentDictionary<string, DataResponse> DataStorage { get; set; }
        public static ConcurrentDictionary<string, CodeResponse> CodeStorage { get; set; }
        public static ConcurrentDictionary<string, ModelResponse> ModelStorage { get; set; }
        public static ConcurrentDictionary<string, TaskResponse> TaskStorage { get; set; }
        public static ConcurrentDictionary<string, InstanceResponse> InstanceStorage { get; set; } 
        public static ConcurrentDictionary<string, SchedulerResponse> SchedulerStorage { get; set; }
        public static ConcurrentDictionary<string, ZSSettingResponse> ZSSettingStorage { get; set; }
    }
}
