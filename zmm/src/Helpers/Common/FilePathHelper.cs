using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ZMM.Models.ResponseMessages;

namespace ZMM.Helpers.Common
{
    public static class FilePathHelper
    {
        public static string GetFilePathById<T>(string id, List<T> records)
        {
            string filePath = "";            
            IEnumerable<CodeResponse> _c = new List<CodeResponse>();
            IEnumerable<DataResponse> _d;
            IEnumerable<ModelResponse> _m;            

            if ((records == null) || (records.Count <= 0)) return "";            

            switch(typeof(T).Name)
            {               
                case "CodeResponse":
                    _c = records.Cast<CodeResponse>();                   
                    foreach(var resp in _c)
                    {			
			            if(resp.Id == id)
                        {
                            filePath = resp.FilePath;
                        }
		            }
                    break;

                 case "DataResponse":
                    _d = records.Cast<DataResponse>();
                    foreach(var resp in _d)
                    {			
			            if(resp.Id == id)
                        {
                            filePath = resp.FilePath;
                        }
		            }
                    break;
                case "ModelResponse":
                    _m = records.Cast<ModelResponse>();                   
                    foreach(var resp in _m)
                    {			
			            if(resp.Id == id)
                        {
                            filePath = resp.FilePath;
                        }
		            }
                    break;                 
            }
            return filePath;
        }
    }
}
