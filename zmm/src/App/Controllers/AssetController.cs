using System;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Helpers.Extensions;
using System.Collections.Generic;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Payloads;
using Newtonsoft.Json.Linq;
using System.Threading.Tasks;
using ZMM.Helpers.ZMMDirectory;
using ZMM.Tools.JNB;
using ZMM.Tasks;
using ZMM.App.PyServicesClient;
using ZMM.Tools.TB;
using System.IO;
using ZMM.Helpers.Common;
using Newtonsoft.Json;
using System.Linq;

namespace ZMM.App.Controllers
{
    [Authorize]
    [Route("api/instances")]
    public class AssetController : Controller
    {
        #region Variables
        private readonly IWebHostEnvironment _environment;
        readonly ILogger<AssetController> Logger;
        public IConfiguration Configuration { get; }
        private readonly IPyJupyterServiceClient jupyterClient;
        private readonly IPyTensorServiceClient tbClient;

        #endregion
        
        #region Constructor
        public AssetController(IWebHostEnvironment environment, IConfiguration configuration, ILogger<AssetController> log, IPyJupyterServiceClient _jupyterClient, IPyTensorServiceClient _tbClient)
        {
            //update 
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));
            this.Configuration = configuration;
            this.Logger = log;
            this.jupyterClient = _jupyterClient; 
            this.tbClient = _tbClient;
        }
        #endregion

        #region [Get] list of running instances
        [HttpGet]
        public IActionResult GetRunningInstances()
        {            
            string cmd = "";
            string output = ""; 
          
            List<InstanceResponse> getAllInstances = InstancePayload.Get();

            #region GPU listing

            cmd = "gpustat --json";
            try
            {
                output = cmd.Bash();
                if (!string.IsNullOrEmpty(output))
                {
                    JObject jsonObj = JObject.Parse(output);
                    JArray arr = (JArray)jsonObj["gpus"];
                    int gpuctr = 1;
                    foreach (var a in arr)
                    {
                        JArray tmpArr = (JArray)a["processes"];
                        List<InstanceProperty> _props = new List<InstanceProperty>();

                        _props.Add(new InstanceProperty { key = "temperature.gpu [celsius]", value = a["temperature.gpu"] });
                        _props.Add(new InstanceProperty { key = "utilization.gpu [%]", value = a["utilization.gpu"]});
                        _props.Add(new InstanceProperty { key = "power.draw [W]", value = a["power.draw"]});
                        _props.Add(new InstanceProperty { key = "enforced.power.limit [W]", value = a["enforced.power.limit"]});
                        _props.Add(new InstanceProperty { key = "memory.used [MB]", value = a["memory.used"]});
                        _props.Add(new InstanceProperty { key = "memory.total [MB]", value = a["memory.total"]});

                        InstanceResponse _instance = new InstanceResponse()
                        {
                            Id = a["uuid"].ToString(),
                            Name = $"GPU {gpuctr}",
                            Type = "GPU",
                            Properties = _props,
                            Processes = tmpArr
                        };
                        getAllInstances.Add(_instance);
                        gpuctr++;
                    }
                }
                var qry = getAllInstances.Where(x=>x.Type == "ZMK").Count();
                if(qry == 0)
                {
                    getAllInstances.Add(ZMKDockerCmdHelper.GetNonDockerZMK());
                }
            }
            catch (Exception ex)
            {
                string err = ex.StackTrace;
                getAllInstances.Add(ZMKDockerCmdHelper.GetNonDockerZMK());
                //return BadRequest(new {message="running instance loading failed.", exception=ex.StackTrace});             
            }
            
            #endregion
            
            #region ZMK listing
            IList<InstanceResponse> zmkList = ZMKDockerCmdHelper.GetAllRunningZMK();
            if(zmkList.Count > 0)
            {
                getAllInstances.AddRange(zmkList);
            }
            
            #endregion
            
            return Json(getAllInstances); 
        }
        #endregion
    
        #region [POST] start instances
        [HttpPost]
        public async Task<IActionResult> StartInstancesAsync()
        { 
            string reqBody = "";  
            string instanceType = "";  
            // string cmd ="";        
            try
            {
                //read request body
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = await reader.ReadToEndAsync();
                    reqBody = body.ToString();
                }
                //
                IList<InstanceResponse> getAllInstances = InstancePayload.Get();
                //
                JObject jObj = JObject.Parse(reqBody);
                instanceType = jObj["type"].ToString();

                switch(instanceType)
                {
                    case "ZMK":
                        #region start ZMK instances                
                        try
                        {
                            string unassigned = ZMKDockerCmdHelper.GetUnassignedZMKInstance();
                            if(!string.IsNullOrEmpty(unassigned)) ZMKDockerCmdHelper.StartZMKInstance(unassigned);
                        }
                        catch (Exception ex)
                        {
                            return BadRequest(new {message="starting instance failed.", exception=ex.StackTrace});             
                        }
                        #endregion
                            
                        break;
                }

                
            }
            catch(Exception ex)
            {
                 return BadRequest(new {message="starting instance failed.", exception=ex.StackTrace}); 
            }
            
            return Ok();
        }

        #endregion
        
        #region [Delete]API - stop/kill the running instances

        [HttpDelete("{id}")]
        public IActionResult DeleteInstancesAsync(string id)        
        {            
            bool result = false; 
            string type = "";          
            
            //check file type to delete - jupyter
            var codeResponse = CodePayload.Get();
            foreach(var item in codeResponse)
            {
                if(item.Id == id) 
                {
                    type= item.Type;
                }
            }

            //check got pmml file
            if (string.IsNullOrEmpty(type))
            {
                var modalResponse = ModelPayload.Get();
                foreach (var item in modalResponse)
                {
                    if (item.Id == id)
                    {
                        type = item.Type;
                    }
                }
            }
            //check for zmk
            if (string.IsNullOrEmpty(type))
            {
                type = "ZMK";
            }

            switch(type)
            {
                case "JUPYTER_NOTEBOOK":
                    result = StopJupyter(id);
                    InstancePayload.Delete(id);
                    break;
                case "PMML":
                    result = StopTensorboard(id);
                    InstancePayload.Delete(id); 
                    break;
                case "ZMK":
                    result = ZMKDockerCmdHelper.StopZMKInstance(id);                                      
                    break;
            }
            var zmkResponse1 = InstancePayload.Get();
            return Ok(new { user = string.Empty, id = id, type = type ,message="Instance deleted successfully.", Json = JsonConvert.SerializeObject(zmkResponse1)});
        }
        
        #endregion

        #region stop Jupyter Notebook
        [NonAction]
        public bool StopJupyter(string id)
        {       
            bool result = false;       
            string ResourceName = $"{id}.ipynb";
            string ResourceNameWithoutExtension = id;
            string notebookDir = DirectoryHelper.GetCodeDirectoryPath() + ResourceNameWithoutExtension;
            string ResourcePath = notebookDir + System.IO.Path.DirectorySeparatorChar + ResourceName; 
            string Message = "Error";
            System.Console.WriteLine("Resource Path " + ResourcePath);
            Dictionary<string,string> Result = new Dictionary<string, string>(); 
            //
            var obj = new
            {         
                base_url = "/",             
                NotebookDir = $"{notebookDir}",
                ResourcePath = $"{ResourcePath}"
            };
            //
            try
            {  
                JupyterNotebook  JNBTool = this.jupyterClient.GetJupyterNotebookTool();                 
                ITask JupyterNoteBookTask = JNBTool.FindTask(ResourcePath);         
                if(JupyterNoteBookTask.IsEmpty())
                {
                    Message = "Error : There is no such task running";
                    // var inst = InstancePayload.Get();
                    // foreach(var item in inst)
                    // {
                    //     if(item.Id == id)
                    //     {
                    //         InstancePayload.Delete(id); 
                    //         result = true;
                    //     }
                    // }
                }   
                else
                {
                    JNBTool.StopTask(ResourcePath);
                    result = true; 
                    InstancePayload.Delete(id);                  
                    Message = "Notebook successfully stop";                    
                }
                
            }
            catch(Exception ex)
            {
                Message =  ex.Message;
            }
            // Result.Add("Result", Message);
            return result;
        }
        
        #endregion
            
        #region stop TB Notebook
        [NonAction]
        public bool StopTensorboard(string id)
        {       
            bool result = false;       
            string ResourceName = $"{id}.pmml";
            string ResourceNameWithoutExtension = id;
            string notebookDir = DirectoryHelper.GetCodeDirectoryPath() + ResourceNameWithoutExtension;
            string ResourcePath = notebookDir + System.IO.Path.DirectorySeparatorChar + ResourceName; 
            string Message = "Error";
            System.Console.WriteLine("Resource Path " + ResourcePath);
            Dictionary<string,string> Result = new Dictionary<string, string>(); 
            //
            var obj = new
            {         
                base_url = "/",             
                NotebookDir = $"{notebookDir}",
                ResourcePath = $"{ResourcePath}"
            };
            //
            try
            {  
                TensorBoard  TBTool = this.tbClient.GetTensorBoardTool();                 
                ITask TBNoteBookTask = TBTool.FindTask(ResourcePath);         
                if(TBNoteBookTask.IsEmpty())
                {
                    Message = "Error : There is no such task running";                    
                }   
                else
                {
                    TBTool.StopTask(ResourcePath);
                    result = true; 
                    InstancePayload.Delete(id);                  
                    Message = "Tensorboard successfully stop";                    
                }
                
            }
            catch(Exception ex)
            {
                Message =  ex.Message;
            }
            
            return result;
        }
        #endregion
    }
}