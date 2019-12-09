using System;
using System.Threading.Tasks;

namespace ZMM.App.ZSServiceClient
{
    public interface IZSModelPredictionClient
    {
        Task<string> GetModels(string zmodId);
        Task<string> UploadPmml(string dirFullPath,string zmodId);
        Task<string> DeletePmml(string modelName,string zmodId);
        Task<string> SingleScoring(string modelName,string record,string zmodId); 
        Task<string> MultipleScoring(string modelName,string record,string zmodId); 
        Task<string> ImageScoring(string modelName,string record,string zmodId);
    }
}