using System.Threading.Tasks;

namespace ZMM.App.PyServicesClient
{
    public interface IPyZMEServiceClient
    {
        Task<string> GetListOfLayers();        
        Task<string> AddUpdateLayers(string id, string body);
        Task<string> DeleteLayers(string id, string body);
        Task<string> PostConvertPmmlAsync(string oldFilePath,string newFilePath);
    }
}