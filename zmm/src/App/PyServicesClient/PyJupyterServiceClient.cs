using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.IO;
using ZMM.Tools.JNB;

namespace ZMM.App.PyServicesClient
{
    public class PyJupyterServiceClient : IPyJupyterServiceClient
    {
        
        private JupyterNotebook JupyterNotebookTool;
        
        public PyJupyterServiceClient(string HostURL)
        {  
            JupyterNotebookTool = new JupyterNotebook(HostURL);          
        }      

        public JupyterNotebook GetJupyterNotebookTool()
        {
            return this.JupyterNotebookTool;
        }
        


    }
}