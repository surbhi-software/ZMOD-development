using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class InstancePayload
    {
        #region Create
        /// <summary>
        /// CreateInstancePayload
        /// </summary>
        /// <param name="newRecord"></param>
        /// <returns></returns>
        public static InstanceResponse Create(InstanceResponse newRecord)
        {
            GlobalStorage.InstanceStorage.TryAdd(newRecord.Id, newRecord);
            return newRecord;
        }

        #endregion

        #region Read
        /// <summary>
        /// GetAllInstancePayload : get all running instance information
        /// </summary>
        /// <returns>List<InstanceResponse></returns>
        public static List<InstanceResponse> Get()
        {
            List<InstanceResponse> _inst = new List<InstanceResponse>();
            if (GlobalStorage.InstanceStorage != null)
            {
                foreach (var item in GlobalStorage.InstanceStorage)
                {
                    _inst.Add(item.Value);
                }
            }
            var sortDesc = _inst.OrderBy(d => d.Type).ThenBy(d=>d.Name);
            return sortDesc.ToList();
        }

        public static bool IsInstanceExists(string id)
        {
            bool result=false;
            if (GlobalStorage.InstanceStorage != null)
            {
                foreach (var item in GlobalStorage.InstanceStorage)
                {
                    if(item.Key == id)
                    {
                        result = true;
                        break;
                    }                    
                }
            }
            
            return result;
        }
        #endregion

        #region Delete
        /// <summary>
        /// Delete record from the payload
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public static bool Delete(string pid)
        {
            bool result = false;            
            //logic to delete 
            InstanceResponse _inst = new InstanceResponse();

            foreach (var item in GlobalStorage.InstanceStorage)
            {
                try
                {
                    if ((item.Key == pid))
                    {   
                        GlobalStorage.InstanceStorage.TryRemove(pid, out _inst);                       
                        result = true;
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
    
        #region Delete All
        /// <summary>
        /// Delete all record from the payload
        /// </summary>
        /// <returns></returns>
        public static bool DeleteAll()
        {
            bool result = false;            
            //logic to delete 
            InstanceResponse _inst = new InstanceResponse();
            try
            {
                foreach(var item in GlobalStorage.InstanceStorage)
                {
                    GlobalStorage.InstanceStorage.Clear();
                }                
                result = true;
            }
            catch (Exception ex)
            {
                var err = ex.InnerException;
            }

            return result;
        }
        #endregion
    
        #region Clear payload
        public static void Clear()
        {            
            GlobalStorage.InstanceStorage.Clear();
        }
        #endregion 
    }
}
