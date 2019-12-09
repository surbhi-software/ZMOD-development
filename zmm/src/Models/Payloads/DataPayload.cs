using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class DataPayload
    {
        #region Create
        public static DataResponse Create(DataResponse newRecord)
        {
            GlobalStorage.DataStorage.TryAdd(newRecord.Id, newRecord);
            return newRecord;
        }
        #endregion

        #region Read
        public static List<DataResponse> Get()
        {
            List<DataResponse> _data = new List<DataResponse>();

            foreach (var item in GlobalStorage.DataStorage)
            {
                _data.Add(item.Value);
            }

            var sortDesc = _data.OrderByDescending(d => d.DateCreated);

            return sortDesc.ToList();
        }
        public static DataResponse Get(string id)
        {
            DataResponse single = new DataResponse();

            foreach (var item in GlobalStorage.DataStorage)
            {
                if (item.Key == id)
                {
                    single = item.Value;
                }
            }

            return single;
        }

       
        #endregion

        #region Update
        public static DataResponse Update(DataResponse updateRecord)
        {
            DataResponse _data = new DataResponse();
            bool isUpdated = false;
            if (GlobalStorage.DataStorage.Count <= 0) return _data;
            foreach (var item in GlobalStorage.DataStorage)
            {
                if (item.Key == updateRecord.Id)
                {
                    bool result = GlobalStorage.DataStorage.TryRemove(item.Key, out _data);
                    if (result)
                    {
                        GlobalStorage.DataStorage.TryAdd(updateRecord.Id, updateRecord);
                        isUpdated = true;
                    }
                }
            }

            if (isUpdated) return updateRecord;
            else return _data;
        }
        #endregion

        #region Delete
        public static bool Delete(string id)
        {
            bool result = false;            
            //logic to delete 
            DataResponse _data = new DataResponse();

            foreach (var item in GlobalStorage.DataStorage)
            {
                result = false;
                try
                {
                    if((item.Key == id) && (item.Value.Type == "FOLDER"))
                    {
                        //delete zip file and folder
                        if(File.Exists(item.Value.FilePath+".zip")) File.Delete(item.Value.FilePath+".zip");
                        Directory.Delete(item.Value.FilePath, true);                        
                        result = true;
                    }
                    else if ((item.Key == id))
                    {
                        File.Delete(item.Value.FilePath);    
                        result = true;
                    }
                    //
                    if(result)
                    {
                        GlobalStorage.DataStorage.TryRemove(id, out _data);
                        break;
                    }
                                       
                }
                catch (Exception ex)
                {
                    // var err = ex.InnerException;
                    Console.WriteLine(ex.StackTrace);
                }
            }
            return result;
        }
        #endregion

        #region Remove from GlobalStorage DataPayload
        public static bool RemoveOnlyFromDataPayload(string id)
        {
            bool result = false;
            
            DataResponse _data = new DataResponse();

            foreach (var item in GlobalStorage.DataStorage)
            {
                GlobalStorage.DataStorage.TryRemove(id, out _data);
                result = true;
            }
            return result;
        }
        #endregion
    
        #region Clear payload
        public static void Clear()
        {            
            GlobalStorage.DataStorage.Clear();
        }
        #endregion 
    }
}
