using System;
using System.Threading.Tasks;

namespace ZMM.App.PyServicesClient
{
    public interface IPyAutoMLServiceClient
    {
        Task<string> GetPreprocessingForm(string filePath);
        Task<string> PostProcessingForm(string data); 
        Task<string> GetSelectedTask(string id);        
        Task<string> SaveBestPmml(string filePath);
        Task<Byte[]> DownloadFile(string filePath, string fileName); 
        Task<string> AnamolyModel(string data);
    }
}