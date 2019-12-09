using System.Threading.Tasks;

namespace ZMM.App.PyServicesClient
{
    public interface IPyCompile
    {
        Task<string> CompilePy(string filePath);  
        Task<string> ExecutePy(string filePath, string _params); 
    }
}