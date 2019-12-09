using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class ModelPayload
    {
        #region Create
        public static ModelResponse Create(ModelResponse newRecord)
        {
            newRecord.DateCreated = Convert.ToDateTime(newRecord.Created_on);
            GlobalStorage.ModelStorage.TryAdd(newRecord.Id, newRecord);
            return newRecord;
        }
        #endregion

        #region Read
        public static List<ModelResponse> Get()
        {
            List<ModelResponse> _model = new List<ModelResponse>();
            if (GlobalStorage.ModelStorage != null)
            {
                foreach (var item in GlobalStorage.ModelStorage)
                {
                    _model.Add(item.Value);
                }
            }

            var sortDesc = _model.OrderByDescending(d => d.DateCreated);
            return sortDesc.ToList();
        }
        #endregion

        #region Update
        public static ModelResponse Update(ModelResponse updatedRecord)
        {
            //
            ModelResponse _m = GlobalStorage.ModelStorage.Values
                .Where(a => a.Id == updatedRecord.Id)
                .Select(a => a).ToList()[0];
            //
            // Delete(updatedRecord.Id);
            ModelResponse newRecord = updatedRecord;
            newRecord.DateCreated = Convert.ToDateTime(newRecord.Created_on);
            GlobalStorage.ModelStorage.TryRemove(updatedRecord.Id, out updatedRecord);
            GlobalStorage.ModelStorage.TryAdd(updatedRecord.Id, newRecord);

            return newRecord;
        }
        #endregion

        #region Delete
        public static bool Delete(string id)
        {
            bool result = false;            
            ModelResponse _model = new ModelResponse();

            foreach (var item in GlobalStorage.ModelStorage)
            {
                try
                {
                    if ((item.Key == id))
                    {
                        File.Delete(item.Value.FilePath);
                        GlobalStorage.ModelStorage.TryRemove(id, out _model);
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
    
        #region Remove from GlobalStorage ModelPayload
        public static bool RemoveOnlyFromModelPayload(string id)
        {
            bool result = false;
            
            ModelResponse _data = new ModelResponse();

            foreach (var item in GlobalStorage.DataStorage)
            {
                GlobalStorage.ModelStorage.TryRemove(id, out _data);
                result = true;
            }
            return result;
        }
        #endregion
    
        #region Clear payload
        public static void Clear()
        {            
            GlobalStorage.ModelStorage.Clear();
        }
        #endregion 
    }
}
