using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class SchedulerPayload
    {
        #region Create
        /// <summary>
        /// Create SchedulerPayload
        /// </summary>
        /// <param name="newRecord"></param>
        /// <returns></returns>
        public static SchedulerResponse Create(SchedulerResponse newRecord)
        {
            GlobalStorage.SchedulerStorage.TryAdd(newRecord.Id, newRecord);
            return newRecord;
        }

        #endregion

        #region Read
        /// <summary>
        /// GetAllSchedulerPayload : get all Scheduler file information
        /// </summary>
        /// <returns>List<BaseResponse></returns>
        public static List<SchedulerResponse> Get()
        {
            List<SchedulerResponse> _scheduler = new List<SchedulerResponse>();
            if (GlobalStorage.SchedulerStorage != null)
            {
                foreach (var item in GlobalStorage.SchedulerStorage)
                {
                    _scheduler.Add(item.Value);
                }
            }
            var sortDesc = _scheduler.OrderByDescending(d => d.DateCreated);
            return sortDesc.ToList();
        }

        public static List<SchedulerResponse> GetById(string id)
        {
            List<SchedulerResponse> _scheduler = new List<SchedulerResponse>();
            if (GlobalStorage.SchedulerStorage != null)
            {
                foreach (var item in GlobalStorage.SchedulerStorage)
                {
                    if (item.Value.Id == id)
                    {
                        _scheduler.Add(item.Value);
                        break;
                    }
                }
            }
            
            return _scheduler;
        }

        #endregion

        #region Update
        public static SchedulerResponse Update(SchedulerResponse updatedRecord)
        {
            //
            SchedulerResponse _m = GlobalStorage.SchedulerStorage.Values
                .Where(a => a.Id == updatedRecord.Id)
                .Select(a => a).ToList()[0];
            //

            GlobalStorage.SchedulerStorage.TryUpdate(updatedRecord.Id, updatedRecord, _m);
            return updatedRecord;
        }
        #endregion

        #region Delete
        /// <summary>
        /// Delete record from the payload
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public static bool Delete(string id)
        {
            bool result = false;
            //logic to delete 
            SchedulerResponse _scheduler = new SchedulerResponse();

            foreach (var item in GlobalStorage.SchedulerStorage)
            {
                try
                {
                    if ((item.Key == id))
                    {
                        GlobalStorage.SchedulerStorage.TryRemove(id, out _scheduler);
                        result = true;
                        break;
                    }
                }
                catch (Exception ex)
                {
                    var err = ex.InnerException;
                }
            }
            return result;
        }
        #endregion

        #region Remove from GlobalStorage SchedulerPayload
        public static bool RemoveOnlyFromSchedulerPayload(string id)
        {
            bool result = false;

            SchedulerResponse _data = new SchedulerResponse();

            foreach (var item in GlobalStorage.SchedulerStorage)
            {
                GlobalStorage.SchedulerStorage.TryRemove(id, out _data);
                result = true;
            }
            return result;
        }
        #endregion

        #region Clear payload
        public static void Clear()
        {
            GlobalStorage.SchedulerStorage.Clear();
        }
        #endregion

        #region Search
        public static bool SearchSchedular()
        {
            bool isExists = false;
            List<SchedulerResponse> _scheduler = new List<SchedulerResponse>();
            if (GlobalStorage.SchedulerStorage != null)
            {
                foreach (var item in GlobalStorage.SchedulerStorage)
                {
                    _scheduler.Add(item.Value);
                }
            }
            var sortDesc = _scheduler.OrderByDescending(d => d.DateCreated);
            return isExists;
        }
        #endregion
    }
}
