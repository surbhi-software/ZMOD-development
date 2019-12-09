using System.Threading.Tasks;
using ZMM.Tools.JNB;


namespace ZMM.App.PyServicesClient
{
    public interface IPyJupyterServiceClient
    {        
        JupyterNotebook GetJupyterNotebookTool();
    }
}