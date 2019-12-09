using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class CodePayload
    {
        #region Create
        /// <summary>
        /// CreateCodePayload
        /// </summary>
        /// <param name="newRecord"></param>
        /// <returns></returns>
        public static CodeResponse Create(CodeResponse newRecord)
        {
            GlobalStorage.CodeStorage.TryAdd(newRecord.Id, newRecord);
            return newRecord;
        }

        #endregion

        #region Read
        /// <summary>
        /// GetAllCodePayload : get all code file information
        /// </summary>
        /// <returns>List<BaseResponse></returns>
        public static List<CodeResponse> Get()
        {
            List<CodeResponse> _code = new List<CodeResponse>();
            if (GlobalStorage.CodeStorage != null)
            {
                foreach (var item in GlobalStorage.CodeStorage)
                {
                    _code.Add(item.Value);
                }
            }
            var sortDesc = _code.OrderByDescending(d => d.DateCreated);
            return sortDesc.ToList();
        }

        public static CodeResponse GetById(string id)
        {
            CodeResponse result = new CodeResponse();
            if (GlobalStorage.CodeStorage != null)
            {
                foreach (var item in GlobalStorage.CodeStorage)
                {
                    if (item.Key == id)
                    {
                        result = item.Value;
                        break;
                    }
                }
            }
            return result;
        }
        #endregion

        #region Update
        public static CodeResponse Update(CodeResponse updatedRecord)
        {
            //
            CodeResponse _m = GlobalStorage.CodeStorage.Values
                .Where(a => a.Id == updatedRecord.Id)
                .Select(a => a).ToList()[0];
            //
            Delete(updatedRecord.Id);
            GlobalStorage.CodeStorage.TryAdd(updatedRecord.Id, updatedRecord);
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
            CodeResponse _code = new CodeResponse();

            foreach (var item in GlobalStorage.CodeStorage)
            {
                try
                {
                    if ((item.Key == id))
                    {
                        File.Delete(item.Value.FilePath);
                        if (item.Value.Type == "JUPYTER_NOTEBOOK")
                        {
                            Directory.Delete(item.Value.FilePath.Replace(item.Value.Name, ""), true);
                        }
                        GlobalStorage.CodeStorage.TryRemove(id, out _code);
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

        #region Remove from GlobalStorage CodePayload
        public static bool RemoveOnlyFromCodePayload(string id)
        {
            bool result = false;

            CodeResponse _data = new CodeResponse();

            foreach (var item in GlobalStorage.CodeStorage)
            {
                GlobalStorage.CodeStorage.TryRemove(id, out _data);
                result = true;
            }
            return result;
        }
        #endregion

        #region Clear payload
        public static void Clear()
        {
            GlobalStorage.CodeStorage.Clear();
        }
        #endregion


    }
}
