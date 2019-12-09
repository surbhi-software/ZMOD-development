using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Xunit;

namespace ZMM.JNB.Tests
{
    public class UnitTests
    {
        static internal string TestDir = Environment.CurrentDirectory + "/ZMOD/testuser";
                  

        /*
        
        [Fact]
        [Trait("Category", "Default")]
        public void TestFindStart()
        {
            System.Console.WriteLine("Start Test : FindStart");    
            string NotebookFile = TestDir + "/data/HelloClass/HelloClass.ipynb";
            JupyterNotebook.Init("/home/nimesh/Zementis/Software/jupyter/bin/jupyter-notebook", "http://localhost");
            var obj = new
            {        
                notebook_dir = $"{TestDir}"                          
            };            
            NotebookInfo NewBook = new NotebookInfo(obj);            
            JupyterNotebook nb = JupyterNotebook.Find(NotebookFile);            
            Assert.Null(nb);
            nb = new JupyterNotebook(NewBook);
            nb.Start();       
            System.Threading.Thread.Sleep(5000);                            
            nb = JupyterNotebook.Find(NotebookFile);            
            Assert.NotNull(nb);  
            Assert.True(nb.Info.Status == JupyterNotebook.Status.Running); 
            Assert.True(nb.Info.Pid > 0);  
            Assert.True(nb.Info.Port == 8888); 
            string Ls = nb.Link(NotebookFile);
            System.Console.WriteLine("End Test : FindStart");                            
        }
        

        [Fact]
        public void TestFindStopStart()
        {
            System.Console.WriteLine("Start Test : FindStopStart");
            string NotebookFile = TestDir + "/data/HelloClass/HelloClass.ipynb";
            JupyterNotebook.Init("/home/nimesh/Zementis/Software/jupyter/bin/jupyter-notebook", "http://localhost");
            JupyterNotebook nb = JupyterNotebook.Find(NotebookFile);     
            Assert.NotNull(nb);
            Assert.True(nb.Info.Status == JupyterNotebook.Status.Running);                   
            nb.Stop();
            Task.Delay(20000).Wait(); 
            nb = JupyterNotebook.Find(NotebookFile);             
            Assert.Null(nb);  
            System.Console.WriteLine("End Test : FindStopStart");      
        }
        */
        
    }
}
