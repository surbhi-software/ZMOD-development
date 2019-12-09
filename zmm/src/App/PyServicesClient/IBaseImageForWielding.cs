using System.Threading.Tasks;

namespace ZMM.App.PyServicesClient
{
    public interface IBaseImageForWielding
    {
        Task<string> GetBaseImage();
        Task<string> PostBaseImage(string configInfo);
        Task<string> PostGenerateBaseImage(string configInfo);

    }
}