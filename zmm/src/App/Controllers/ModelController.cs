using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System.Text;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Configuration;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Serialization;
using ZMM.Models.Payloads;
using ZMM.Models.ResponseMessages;
using ZMM.Helpers.ZMMDirectory;
using ZMM.App.PyServicesClient;
using ZMM.App.ZSServiceClient;
using ZMM.Tools.TB;
using ZMM.Helpers.Common;
using Quartz;
using Quartz.Impl;

namespace ZMM.App.Controllers
{
    [Authorize]
    [Route("api/[controller]")]
    public class ModelController : Controller
    {
        #region Variables 
        private readonly string CURRENT_USER = "";

        private readonly IWebHostEnvironment _environment;
        readonly ILogger<ModelController> Logger;
        private IConfiguration Configuration { get; }
        private readonly IPyNNServiceClient nnclient;
        private readonly IPyZMEServiceClient zmeClient;
        private readonly IZSModelPredictionClient zsClient;

        private readonly IPyTensorServiceClient tbClient;
        private List<ModelResponse> responseData;
        private List<DataResponse> dataResponseData;
        private static string[] extensions = new[] { "pmml", "onyx" };
        private readonly IScheduler _scheduler;
        #endregion

        #region Constructor
        public ModelController(IWebHostEnvironment environment, IConfiguration configuration, ILogger<ModelController> log, IPyNNServiceClient srv, IPyZMEServiceClient _zmeClient, IZSModelPredictionClient _zsClient, IPyTensorServiceClient tbClientInstance, IScheduler factory)
        {
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));
            this.Configuration = configuration;
            this.nnclient = srv;
            this.Logger = log;
            this.zmeClient = _zmeClient;
            this.zsClient = _zsClient;
            this.tbClient = tbClientInstance;
            _scheduler = factory;
            try
            {
                responseData = ModelPayload.Get();
                dataResponseData = DataPayload.Get();
            }
            catch (Exception ex)
            {
                //ILogger
                string error = ex.Message;
            }

        }
        #endregion

        #region Post/ upload pmml file
        // POST api/model
        [HttpPost]
        [RequestFormLimits(MultipartBodyLengthLimit = 2147483648)]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> Post(List<IFormFile> file)
        {
            #region variables
            List<ModelResponse> _response = new List<ModelResponse>();
            List<ModelResponse> existingCodeData = new List<ModelResponse>();
            long size = file.Sum(f => f.Length);
            string type = string.Empty;
            bool IsFileExists = false;
            // full path to file in temp location
            var filePath = Path.GetTempFileName();
            string dirFullpath = DirectoryHelper.GetModelDirectoryPath();
            #endregion

            //check if folder path exists...if not then create folder
            if (!Directory.Exists(dirFullpath))
            {
                Directory.CreateDirectory(dirFullpath);
            }

            foreach (var formFile in file)
            {
                if (formFile.Length > 0)
                {
                    //check if the file with the same name exists
                    existingCodeData = ModelPayload.Get();
                    if (existingCodeData.Count > 0)
                    {
                        //
                        foreach (var record in existingCodeData)
                        {
                            if ((record.Name == formFile.FileName) && (record.User == CURRENT_USER))
                            {
                                IsFileExists = true;
                            }
                        }
                    }
                    existingCodeData.Clear();
                    //
                    if (!IsFileExists)
                    {
                        string fileExt = System.IO.Path.GetExtension(formFile.FileName).Substring(1).ToString().ToLower();
                        // upload file start
                        using (var fileStream = new FileStream(Path.Combine(dirFullpath, formFile.FileName), FileMode.Create))
                        {
                            //check file allowed extensions

                            if (!extensions.Contains(fileExt))
                            {
                                return BadRequest("File type not allowed");
                            }
                            else
                            {
                                await formFile.CopyToAsync(fileStream);
                            }
                        }

                        if (fileExt.Contains("pmml"))
                        {
                            type = "PMML";
                        }
                        else
                        {
                            type = fileExt.ToUpper();
                        }
                        List<Property> _props = new List<Property>();
                        string _url = DirectoryHelper.GetModelUrl(formFile.FileName);
                        string _filePath = Path.Combine(dirFullpath, formFile.FileName);
                        //
                        ModelResponse newRecord = new ModelResponse()
                        {
                            Created_on = DateTime.Now.ToString(),
                            Deployed = false,
                            Edited_on = DateTime.Now.ToString(),
                            Extension = fileExt,
                            FilePath = _filePath,
                            Id = formFile.FileName.Replace($".{fileExt}", ""),
                            Loaded = false,
                            MimeType = formFile.ContentType,
                            Name = formFile.FileName,
                            Size = formFile.Length,
                            Type = type,
                            Url = _url,
                            User = CURRENT_USER,
                            Properties = _props
                        };
                        //
                        _response.Add(ModelPayload.Create(newRecord));
                    }
                }
            }

            return Ok(_response);
        }
        #endregion

        #region Get all Models
        // GET api/model
        [HttpGet]
        public IActionResult Get(bool loaded, bool refresh)
        {
            //
            if (refresh)
            {
                ModelPayload.Clear();
                InitZmodDirectory.ScanModelsDirectory();
                responseData = ModelPayload.Get();
            }
            //
            DefaultContractResolver contractResolver = new DefaultContractResolver
            {
                NamingStrategy = new CamelCaseNamingStrategy()
            };
            string jsonStr = JsonConvert.SerializeObject(responseData, new JsonSerializerSettings
            {
                ContractResolver = contractResolver,
                Formatting = Formatting.Indented
            });
            var jsonObj = JsonConvert.DeserializeObject<List<ModelResponse>>(jsonStr);
            //loaded
            if (loaded)
            {
                List<ModelResponse> loadedModel = new List<ModelResponse>();
                foreach (var record in jsonObj)
                {
                    if (record.Loaded)
                    {
                        loadedModel.Add(record);
                    }
                }
                return Json(loadedModel);
            }

            return Json(jsonObj);
        }
        #endregion

        #region Get loaded model - api/model/loaded
        [HttpGet("loaded")]
        public async Task<IActionResult> GetLoadedModelAsync()
        {
            //response formatting
            DefaultContractResolver contractResolver = new DefaultContractResolver
            {
                NamingStrategy = new CamelCaseNamingStrategy()
            };
            string jsonStr = JsonConvert.SerializeObject(responseData, new JsonSerializerSettings
            {
                ContractResolver = contractResolver,
                Formatting = Formatting.Indented
            });
            //
            List<object> loadedModels = new List<object>();
            string zmkResponse = string.Empty;
            //try-catch block
            try
            {
                zmkResponse = await nnclient.GetAllModelList();
                if (!string.IsNullOrEmpty(zmkResponse) && !zmkResponse.Contains(ZMMConstants.ErrorFailed))
                {
                    JArray jArr = JArray.Parse(zmkResponse);
                    foreach (JObject parsedObject in jArr.Children<JObject>())
                    {
                        loadedModels.Add(new { Id = parsedObject["modelName"].ToString(), Name = parsedObject["modelName"].ToString(), Type = "PMML" });
                    }
                }
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.StackTrace);
                return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
            }
            return Json(loadedModels);
        }

        #endregion

        #region Delete...
        [HttpDelete("{id}")]
        public IActionResult Delete(string id)
        {
            bool result = ModelPayload.Delete(id);

            if (result == true)
            {
                return Ok(new { user = CURRENT_USER, id = id, message = "File deleted successfully." });
            }
            else
            {
                return BadRequest(new { user = CURRENT_USER, id = id, message = "Error deleting file. Try again or contact adminstrator." });
            }
        }
        #endregion

        #region Load model POST -  /api/model/{id}/load
        [HttpGet]
        [Route("{id}/load")]
        public async Task<IActionResult> LoadModelAsync(string id)
        {
            string response = string.Empty;
            JObject jsonResponse = new JObject();
            bool isExists = false;

            if (responseData.Count > 0)
            {
                foreach (var record in responseData)
                {
                    if (record.Id.ToString() == id)
                    {
                        try
                        {
                            string pyResponse = await nnclient.PostLoadModel(record.FilePath);
                            if (!pyResponse.Contains(ZMMConstants.ErrorFailed))
                            {
                                ModelResponse updateRecord = new ModelResponse()
                                {
                                    Created_on = record.Created_on,
                                    Deployed = record.Deployed,
                                    Edited_on = record.Edited_on,
                                    Extension = record.Extension,
                                    FilePath = record.FilePath,
                                    Id = record.Id,
                                    Loaded = true,
                                    MimeType = record.MimeType,
                                    Name = record.Name,
                                    Size = record.Size,
                                    Type = record.Type,
                                    Url = record.Url
                                };

                                ModelPayload.Update(updateRecord);
                                responseData = ModelPayload.Get();
                                response = "{ id: '" + record.Id + "', loaded: true}";
                                if (!string.IsNullOrEmpty(response)) jsonResponse = JObject.Parse(response);
                                isExists = true;
                            }
                            else
                            {
                                return BadRequest(new { message = "Model loading failed.", errorCode = 500, exception = "No response from server." });
                            }
                        }
                        catch (Exception ex)
                        {
                            Logger.LogCritical(ex, "Model loading failed.");
                            return BadRequest(new { message = "Model loading failed.", errorCode = 400, exception = ex.Message });
                        }
                    }
                }
            }
            if (!isExists)
            {
                return NotFound(new { message = "Model loading failed.", errorCode = 404, exception = "No such model." });
            }
            return Json(jsonResponse);
        }

        #endregion

        #region Unload model...
        [HttpGet]
        [Route("{id}/unload")]
        public async Task<IActionResult> UnloadModelAsync(string id)
        {
            //variables
            string response = string.Empty;
            JObject jsonResponse = new JObject();
            bool isExists = false;

            if (responseData.Count > 0)
            {
                foreach (var record in responseData)
                {
                    if (record.Id.ToString() == id)
                    {
                        try
                        {
                            string pyResponse = await nnclient.PostUnloadModel(record.Name.Replace(".pmml", string.Empty));
                            if (pyResponse != "fail")
                            {
                                //
                                ModelResponse updateRecord = new ModelResponse()
                                {
                                    Created_on = record.Created_on,
                                    Deployed = record.Deployed,
                                    Edited_on = record.Edited_on,
                                    Extension = record.Extension,
                                    FilePath = record.FilePath,
                                    Id = record.Id,
                                    Loaded = false,
                                    MimeType = record.MimeType,
                                    Name = record.Name,
                                    Size = record.Size,
                                    Type = record.Type,
                                    Url = record.Url
                                };
                                //
                                ModelPayload.Update(updateRecord);
                                responseData = ModelPayload.Get();
                                response = "{ id: '" + record.Id + "', loaded: false}";
                                if (!string.IsNullOrEmpty(response)) jsonResponse = JObject.Parse(response);
                                isExists = true;
                            }
                            else
                            {
                                return BadRequest(new { message = "Model loading failed.", errorCode = 500, exception = "No response from server." });
                            }
                        }
                        catch (Exception ex)
                        {
                            Logger.LogCritical(ex, ex.StackTrace);
                            return BadRequest(new { message = "Model loading failed.", errorCode = 400, exception = ex.Message });
                        }
                    }
                }
            }
            if (!isExists)
            {
                return NotFound(new { message = "Model loading failed.", errorCode = 404, exception = "No such model." });
            }
            return Json(jsonResponse);
        }

        #endregion

        #region Create PMML- /api/model/create...
        // POST api/
        [HttpPost("create")]
        public async Task<IActionResult> CreatePmmlAsync(string type)
        {
            //create blank pmml file
            long fileSize = 0L;
            string dirFullpath = DirectoryHelper.GetModelDirectoryPath();
            string newFile = "New_" + DateTime.Now.Ticks.ToString() + ".pmml";
            string _filePath = Path.Combine(dirFullpath, newFile);
            ModelResponse _data = new ModelResponse();
            List<Property> _props = new List<Property>();
            StringBuilder fileContent = new StringBuilder();
            string _type = "";

            try
            {
                //check if folder path exists...if not then create folder
                if (!Directory.Exists(dirFullpath))
                {
                    Directory.CreateDirectory(dirFullpath);
                }

                //read request body                
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = await reader.ReadToEndAsync();
                    var reqBody = JObject.Parse(body);
                    _type = reqBody["type"].ToString();
                }

                if (_type == "NN")
                {
                    //create blank model data                    
                    fileContent.Append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>,@,");
                    fileContent.Append("<PMML xmlns=\"http://www.dmg.org/PMML-4_3\" version=\"4.3Ext\">,@,");
                    fileContent.Append("<Header copyright=\"Copyright (c) 2018 Software AG\" description=\"Neural Network Model\">,@,");
                    fileContent.Append("<Timestamp>" + DateTime.Now.ToString("yyyy-MM-dd H:mm:ss.") + TimeSpan.TicksPerMillisecond + "</Timestamp>,@,");
                    fileContent.Append("</Header>,@,");
                    fileContent.Append("<DeepNetwork>,@,");
                    fileContent.Append("</DeepNetwork>,@,");
                    fileContent.Append("</PMML>");
                    //
                }
                else if (_type == "WF")
                {
                    //create blank model data for WORKFLOW                    
                    fileContent.Append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>,@,");
                    fileContent.Append("<PMML xmlns=\"http://www.dmg.org/PMML-4_3\" version=\"4.3Ext\" type=\"multi\">,@,");
                    fileContent.Append("<Header copyright=\"Copyright (c) 2018 Software AG\" description=\"Work Flow\">,@,");
                    fileContent.Append("<Timestamp>" + DateTime.Now.ToString("yyyy-MM-dd H:mm:ss.") + TimeSpan.TicksPerMillisecond + "</Timestamp>,@,");
                    fileContent.Append("</Header>,@,");
                    fileContent.Append("<DeepNetwork>,@,");
                    fileContent.Append("</DeepNetwork>,@,");
                    fileContent.Append("</PMML>");
                    //
                }

                using (StreamWriter writer = new StreamWriter(_filePath))
                {
                    foreach (string line in fileContent.ToString().Split(",@,"))
                        writer.WriteLine(line);

                    writer.Flush();
                    fileSize = writer.BaseStream.Length;
                }
                string _url = DirectoryHelper.GetModelUrl(newFile);
                //
                ModelResponse newRecord = new ModelResponse()
                {
                    Created_on = DateTime.Now.ToString(),
                    Deployed = false,
                    Edited_on = DateTime.Now.ToString(),
                    Extension = "pmml",
                    FilePath = _filePath,
                    Id = newFile.Replace($".pmml", ""),
                    Loaded = false,
                    MimeType = "application/octet-stream",
                    Name = newFile,
                    Size = fileSize,
                    Type = "PMML",
                    Url = _url,
                    User = CURRENT_USER,
                    Properties = _props
                };
                //
                _data = ModelPayload.Create(newRecord);
                await Task.FromResult(0);
            }
            catch (Exception ex)
            {
                //write to Ilogger
                string message = ex.Message;
            }
            string jsonStr = JsonConvert.SerializeObject(_data, Formatting.None);
            return Json(_data);
        }
        #endregion

        #region Get PMML by id
        [HttpGet("{id}")]
        public async Task<IActionResult> GetPmmlAsync(string id)
        {
            string pmmlProps = string.Empty;
            responseData = ModelPayload.Get();
            string jsonStr = JsonConvert.SerializeObject(responseData, Formatting.Indented);
            string filePath = string.Empty;
            //jsonStr = jsonStr.ToPrettyJsonString();
            var jsonObj = JsonConvert.DeserializeObject<List<ModelResponse>>(jsonStr);
            ModelResponse _data = new ModelResponse();

            foreach (var record in responseData)
            {
                if (record.Id.ToString() == id)
                {
                    _data = record;
                }
            }
            try
            {
                pmmlProps = await nnclient.GetPmmlProperties(_data.FilePath);
                //  
                string strjObj1 = JsonConvert.SerializeObject(_data);
                JObject jObj1 = JObject.Parse(strjObj1);
                JObject jObj2 = JObject.Parse(pmmlProps);

                if (!string.IsNullOrEmpty(pmmlProps))
                {
                    jObj1.Merge(jObj2, new JsonMergeSettings
                    {
                        // union array values together to avoid duplicates
                        MergeArrayHandling = MergeArrayHandling.Union
                    });
                }
                //
                return Json(jObj1);
            }
            catch (Exception ex)
            {
                string _ex = ex.Message;
                return BadRequest();
            }
        }
        #endregion

        #region NN Edit pmml - api/model/{id}/edit
        // Get 
        [HttpGet("{id}/edit")]
        public async Task<IActionResult> EditPmmlAsync(string id)
        {
            if (!String.IsNullOrEmpty(id))
            {
                string response = string.Empty;
                JObject jsonResp = new JObject();
                string jsonStr = JsonConvert.SerializeObject(responseData, Formatting.None);
                ModelResponse _data = new ModelResponse();
                try
                {
                    var jsonObj = JsonConvert.DeserializeObject<List<ModelResponse>>(jsonStr);
                    foreach (var record in responseData)
                    {
                        if (record.Id.ToString() == id)
                        {
                            _data = record;
                        }
                    }
                    response = await nnclient.PostEditPmml(id, _data.FilePath);
                    if (!string.IsNullOrEmpty(response))
                        jsonResp = JObject.Parse(response);
                }
                catch (Exception ex)
                {
                    string message = ex.Message;
                }
                return Json(jsonResp);
            }
            else
            {
                return new EmptyResult();
            }

        }
        #endregion

        #region List of layers...
        [HttpGet("layers")]
        public async Task<IActionResult> GetListOfLayersAsync()
        {
            string response = string.Empty;
            JObject jsonObj = new JObject();
            try
            {
                response = await zmeClient.GetListOfLayers();
                if (!string.IsNullOrEmpty(response))
                    jsonObj = JObject.Parse(response);
                return Json(jsonObj);
            }
            catch (Exception ex)
            {
                //TO DO: ILogger
                string _ex = ex.Message;
                return NoContent();
            }
        }
        #endregion

        #region Add/Update layer
        [HttpPost("{id}/layer")]
        public async Task<IActionResult> AddLayersAsync(string id)
        {
            string response = string.Empty;
            string reqBody = string.Empty;
            JObject jsonObj = new JObject();
            if (Request.Body!= null)
            {
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }
                try
                {
                    response = await zmeClient.AddUpdateLayers(id, reqBody);
                    if (!string.IsNullOrEmpty(response)) jsonObj = JObject.Parse(response);
                    return Json(jsonObj);
                }
                catch (Exception ex)
                {
                    //TO DO: ILogger
                    string _ex = ex.Message;
                    return BadRequest();
                }
            }
            else
            {
                return BadRequest();
            }
        }
        #endregion

        #region Delete layer
        [HttpDelete("{id}/layer")]
        public async Task<IActionResult> DeleteLayersAsync(string id)
        {
            string response = string.Empty;
            string reqBody = string.Empty;
            JObject jsonObj = new JObject();
            if (Request.Body!=null)
            {
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }
                try
                {
                    response = await zmeClient.DeleteLayers(id, reqBody);
                    if (!string.IsNullOrEmpty(response))
                        jsonObj = JObject.Parse(response);

                    return Json(jsonObj);
                }
                catch (Exception ex)
                {
                    //TO DO: ILogger
                    string _ex = ex.Message;
                    return BadRequest();
                }
            }
            else
            {
                return BadRequest();
            }

        }
        #endregion

        #region Download Pmml
        [HttpGet("{id}/download")]
        public async Task<IActionResult> Download(string id)
        {
            string filePath = string.Empty;
            string type = string.Empty;
            string _contentType = string.Empty;
            try
            {
                if (responseData.Count > 0)
                {
                    foreach (var record in responseData)
                    {
                        if (record.Id.ToString() == id)
                        {
                            filePath = record.FilePath;
                        }
                    }
                }

                type = Path.GetExtension(filePath);
                _contentType = string.Empty;
                var memory = new MemoryStream();

                using (var stream = new FileStream(filePath, FileMode.Open))
                {
                    await stream.CopyToAsync(memory);
                }
                memory.Position = 0;
                //
                string fileName = Path.GetFileName(filePath);
                _contentType = "application/pmml";
                return File(memory, _contentType, fileName);
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message + "filePath :" + filePath);
            }
        }


        #endregion

        #region Training POST - /api/model/{id}/train (ScheduledJob)
        [HttpPost("{id}/train")]
        public async Task<IActionResult> PostModelTrainAsync(string id)
        {
            if (Request.Body!= null)
            {
                string response = string.Empty;
                string dirFullpath = DirectoryHelper.GetDataDirectoryPath();//create new folder in data folder with the name of the file
                string reqBody = string.Empty;
                string filePath = string.Empty;
                string dataFolder = string.Empty;
                JObject jObjOrig = new JObject();

                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }
                try
                {
                    //get file name
                    if (responseData.Count > 0)
                    {
                        foreach (var record in responseData)
                        {
                            if (record.Id.ToString() == id)
                            {
                                //set the filePath
                                filePath = record.FilePath;
                                //create dir with filename in data folder
                                if (!Directory.Exists(dirFullpath + record.Name.Replace(".pmml", string.Empty)))
                                {
                                    Directory.CreateDirectory(dirFullpath + record.Name.Replace(".pmml", string.Empty));
                                    dataFolder = dirFullpath + record.Name.Replace(".pmml", string.Empty);
                                }
                            }
                        }
                    }
                    //json merge
                    //Add TensorBoard Info 
                    if (!string.IsNullOrEmpty(reqBody)) jObjOrig = JObject.Parse(reqBody);
                    if (!string.IsNullOrEmpty(filePath))
                    {
                        string ResourcePath = filePath;
                        string TensorBoardLink = string.Empty;
                        string TensorboardLogFolder = string.Empty;

                        var obj = new
                        {
                            base_url = "/",
                            ResourcePath = $"{ResourcePath}"
                        };
                        try
                        {
                            var portRegex = new Regex(@"(?<![^/]/[^/]*):\d+");//to remove port number
                            TensorBoard TBTool = this.tbClient.GetTensorBoardTool();
                            ZMM.Tasks.ITask TensorBoardTask = TBTool.FindTask(ResourcePath);
                            if (TensorBoardTask.IsEmpty())
                            {
                                TBTool.StartTaskAsync((int)TaskTypes.Start, ResourcePath, (JObject)JObject.FromObject(obj));
                            }
                            TensorBoardLink = TBTool.GetResourceLink(ResourcePath, out TensorboardLogFolder);
                            Console.WriteLine($"TensorBoardLink >>>>>>{TensorBoardLink}");
                            //                    
                            //TB redirection
                            string tbLink = "";
                            if (TensorBoardLink.Contains("6006")) tbLink = TensorBoardLink.Replace(":6006", "/tb1");
                            else if (TensorBoardLink.Contains("6007")) tbLink = TensorBoardLink.Replace(":6007", "/tb2");
                            else if (TensorBoardLink.Contains("6008")) tbLink = TensorBoardLink.Replace(":6008", "/tb3");
                            else tbLink = TensorBoardLink;
                            //
                            jObjOrig.Add("filePath", ResourcePath);
                            jObjOrig.Add("tensorboardLogFolder", TensorboardLogFolder);
                            jObjOrig.Add("tensorboardUrl", tbLink);
                            Logger.LogInformation("PostModelTrainAsync", jObjOrig.ToString());
                            //for asset
                            // int sIdx =  TensorBoardLink.IndexOf(":6");
                            // var tbInst = new List<InstanceProperty>();
                            // tbInst.Add(new InstanceProperty(){ key = "port", value = TensorBoardLink.Substring(sIdx,6)});

                            //
                            var objJNBInst = new InstanceResponse()
                            {
                                Id = id,
                                Name = $"{id}",
                                Type = "TB"
                            };
                            InstancePayload.Create(objJNBInst);
                            //
                        }
                        catch (Exception ex)
                        {
                            Logger.LogCritical("PostModelTrainAsync", ex.Message);
                            //return BadRequest(new { user = CURRENT_USER, id = id, message = ex.Message});
                        }

                    }
                    if (!string.IsNullOrEmpty(dataFolder)) jObjOrig.Add("dataFolder", dataFolder);
                    try { jObjOrig.Add("filePath", filePath); } catch (Exception ex) { }
                    /* remove what is not needed to send to zmk api */
                    jObjOrig.Remove("recurrence");
                    jObjOrig.Remove("cronExpression");
                    /* end */
                    /* call NN train api */
                    response = await nnclient.TrainModel(jObjOrig.ToString());
                    //
                    var objresp = JsonConvert.DeserializeObject<TrainingResponse>(response);
                    objresp.executedAt = DateTime.Now;
                    List<TrainingResponse> tresp = new List<TrainingResponse>();
                    tresp.Add(objresp);
                    //
                    #region schedule training
                    JObject cronjson = JObject.Parse(reqBody);
                    if (cronjson["recurrence"].ToString() == "REPEAT")
                    {
                        //check if same job is scheduled
                        ISchedulerFactory schfack = new StdSchedulerFactory();
                        IScheduler scheduler = await schfack.GetScheduler();
                        var jobKey = new JobKey(filePath);
                        if (await scheduler.CheckExists(jobKey))
                        {
                            await scheduler.ResumeJob(jobKey);
                        }
                        else
                        {
                            #region create quartz job for training model
                            ITrigger trigger = TriggerBuilder.Create()
                            .WithIdentity($"Training Model Job-{DateTime.Now}")
                            .WithCronSchedule(cronjson["cronExpression"].ToString())
                            .WithPriority(1)
                            .Build();

                            IJobDetail job = JobBuilder.Create<TrainModelJob>()
                            .WithIdentity(filePath)
                            .Build();

                            job.JobDataMap["id"] = id;
                            job.JobDataMap["filePath"] = filePath;
                            job.JobDataMap["reqBody"] = jObjOrig.ToString();
                            job.JobDataMap["baseurl"] = Configuration["PyServiceLocation:srvurl"];

                            await _scheduler.ScheduleJob(job, trigger);
                            //add to scheduler payload                            
                            SchedulerResponse schJob = new SchedulerResponse()
                            {
                                CreatedOn = DateTime.Now.ToString(),
                                CronExpression = cronjson["cronExpression"].ToString(),
                                DateCreated = DateTime.Now,
                                EditedOn = DateTime.Now.ToString(),
                                FilePath = filePath,
                                Id = id,
                                Name = id,
                                Type = "NN",
                                Url = "",
                                Recurrence = cronjson["recurrence"].ToString(),
                                StartDate = cronjson["startDate"].ToString(),
                                StartTimeH = (cronjson["startTimeH"].ToString() == null) ? "" : cronjson["startTimeH"].ToString(),
                                StartTimeM = (cronjson["startTimeM"].ToString() == null) ? "" : cronjson["startTimeM"].ToString(),
                                History = tresp.ToList<object>(),
                                Status = "Scheduled"
                            };
                            SchedulerPayload.Create(schJob);
                            #endregion
                        }
                    }
                    else
                    {
                        //add to scheduler payload                            
                        SchedulerResponse schJob = new SchedulerResponse()
                        {
                            CreatedOn = DateTime.Now.ToString(),
                            CronExpression = "",
                            DateCreated = DateTime.Now,
                            EditedOn = DateTime.Now.ToString(),
                            FilePath = filePath,
                            Id = id,
                            Name = id,
                            Type = "NN",
                            Url = "",
                            Recurrence = "ONE_TIME",
                            StartDate = "",
                            StartTimeH = "",
                            StartTimeM = "",
                            History = tresp.ToList<object>(),
                            Status = objresp.status
                        };
                        SchedulerPayload.Create(schJob);
                    }
                    #endregion
                    return Json(response);
                }
                catch (Exception ex)
                {
                    //TO DO: ILogger
                    string _ex = ex.Message;
                    return BadRequest();
                }
            }
            else
            {
                return BadRequest();
            }
        }
        #endregion

        #region Zementis Server API calls

        #region Check for the model existence - [GET]
        [HttpGet("zsmodels")]
        public async Task<IActionResult> GetZSModels()
        {
            string zsResponse = string.Empty;
            try
            {
                zsResponse = await zsClient.GetModels(ZSSettingPayload.GetUserNameOrEmail(HttpContext));
                await Task.FromResult(0);
            }
            catch (Exception ex)
            {
                return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
            }

            if (!string.IsNullOrEmpty(zsResponse))
            {
                zsResponse = Regex.Unescape(zsResponse);
                JObject jo = JObject.Parse(zsResponse);
                return Json(jo);
            }
            else
            {
                return Ok(new { message = "No content", errorCode = 204, exception = "No content" });
            }
        }
        #endregion

        #region Unload/delete pmml from zementis server [DELETE] i.e deployed = false
        [HttpGet("{id}/unloadFromZS")]
        public async Task<IActionResult> DeletePmmlFromZementisServer(string id)
        {
            string response = string.Empty;
            JObject jsonResponse = new JObject();
            bool isExists = false;

            if (responseData.Count > 0)
            {
                foreach (var record in responseData)
                {
                    if (record.Id.ToString() == id)
                    {
                        try
                        {
                            string zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                            string zsResponse = await zsClient.DeletePmml(record.ModelName, zmodId);
                            if (zsResponse != "fail")
                            {
                                //
                                ModelResponse updateRecord = new ModelResponse()
                                {
                                    Created_on = record.Created_on,
                                    Deployed = false,
                                    Edited_on = record.Edited_on,
                                    Extension = record.Extension,
                                    FilePath = record.FilePath,
                                    Id = record.Id,
                                    Loaded = record.Loaded,
                                    MimeType = record.MimeType,
                                    Name = record.Name,
                                    Size = record.Size,
                                    Type = record.Type,
                                    Url = record.Url
                                };
                                //
                                ModelPayload.Update(updateRecord);
                                responseData = ModelPayload.Get();
                                response = "{ id: '" + record.Id + "', deployed: false}";
                                if (!string.IsNullOrEmpty(response)) jsonResponse = JObject.Parse(response);
                                isExists = true;
                            }
                            else
                            {
                                return BadRequest(new { message = "Model loading failed.", errorCode = 500, exception = "No response from server." });
                            }
                        }
                        catch (Exception ex)
                        {
                            Logger.LogCritical(ex, ex.StackTrace);
                            return BadRequest(new { message = "Model loading failed.", errorCode = 400, exception = ex.Message });
                        }
                    }
                }
            }
            if (!isExists)
            {
                return NotFound(new { message = "Model loading failed.", errorCode = 404, exception = "No such model." });
            }
            return Json(jsonResponse);

        }
        #endregion

        #region Load/upload pmml [POST] i.e- deployed = true
        [HttpGet("{id}/loadInZS")]
        public async Task<IActionResult> PostZSUploadPmmlAsync(string id)
        {
            string response, modelName, convertedPath = string.Empty;
            JObject jsonResponse = new JObject();
            bool isExists = false;

            if (responseData.Count > 0)
            {
                foreach (var record in responseData)
                {
                    if (record.Id.ToString() == id)
                    {
                        try
                        {
                            /* TODO: Add code to call ZMK service to get compatible pmml*/
                            RemoveAttribuesIfPresentInPMMLFileBeforeDeploy(record.FilePath);
                            string zmkResponse = await zmeClient.PostConvertPmmlAsync(record.FilePath, record.FilePath.Replace(id, $"Converted_{id}"));
                            Logger.LogInformation("PostZSUploadPmmlAsync ZMK Response after post " + zmkResponse);
                            if (!string.IsNullOrEmpty(zmkResponse) && !zmkResponse.Contains("Failed"))
                            {
                                JObject jo = JObject.Parse(zmkResponse);
                                convertedPath = jo["filePath"].ToString();
                            }
                            if (string.IsNullOrEmpty(convertedPath)) return BadRequest(new { message = "Model loading failed.", errorCode = 400, exception = ZMMConstants.ErrorFailed });
                            string zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                            string zsResponse = await zsClient.UploadPmml(convertedPath, zmodId);
                            Logger.LogInformation("PostZSUploadPmmlAsync ZS Response on deploy " + zsResponse);
                            //remove file after upload
                            if (System.IO.File.Exists(convertedPath))
                            {
                                System.IO.File.Delete(convertedPath);
                            }
                            if (zsResponse != "Fail" && zsResponse != "FileExists")
                            {
                                //
                                modelName = JObject.Parse(zsResponse)["modelName"].ToString();
                                ModelResponse updateRecord = new ModelResponse()
                                {
                                    Created_on = record.Created_on,
                                    Deployed = true,
                                    Edited_on = record.Edited_on,
                                    Extension = record.Extension,
                                    FilePath = record.FilePath,
                                    Id = record.Id,
                                    Loaded = record.Loaded,
                                    MimeType = record.MimeType,
                                    ModelName = modelName,
                                    Name = record.Name,
                                    Size = record.Size,
                                    Type = record.Type,
                                    Url = record.Url
                                };
                                //
                                ModelPayload.Update(updateRecord);
                                responseData = ModelPayload.Get();
                                response = @"{ id: '" + record.Id + "', deployed: true}";
                                if (!string.IsNullOrEmpty(response)) jsonResponse = JObject.Parse(response);
                                isExists = true;
                            }
                            else
                            {
                                return BadRequest(new { message = "Model loading failed.", errorCode = 500, exception = "No response from server." });
                            }
                        }
                        catch (Exception ex)
                        {
                            Logger.LogCritical(ex, ex.StackTrace);
                            return BadRequest(new { message = "Model loading failed.", errorCode = 400, exception = ex.StackTrace });
                        }
                    }
                }
            }
            if (!isExists)
            {
                return NotFound(new { message = "Model loading failed.", errorCode = 404, exception = "No such model." });
            }
            return Json(jsonResponse);
        }


        #endregion

        #region Work around for anomaly detection in pmml as suggested by Vinay, this should be removed or re-factored
        //It removes attribute for=model1 and score
        private void RemoveAttribuesIfPresentInPMMLFileBeforeDeploy(string PMMLModel)
        {
            FileInfo FInfo = new FileInfo(PMMLModel);
            string Contents = string.Empty;
            if (FInfo.Extension.ToLower().Equals(".pmml"))
            {
                Contents = System.IO.File.ReadAllText(PMMLModel);
                Contents = Contents.Replace("for=\"model1\"/>", "/>");
                Contents = Contents.Replace("taskType=\"score\">", ">");
                System.IO.File.WriteAllText(PMMLModel, Contents);
            }
        }
        #endregion

        #region Get deployed models
        [HttpGet("~/api/model/deployed")]
        public async Task<IActionResult> GetDeployedModelAsync()
        {
            //response formatting
            DefaultContractResolver contractResolver = new DefaultContractResolver
            {
                NamingStrategy = new CamelCaseNamingStrategy()
            };
            string jsonStr = JsonConvert.SerializeObject(responseData, new JsonSerializerSettings
            {
                ContractResolver = contractResolver,
                Formatting = Formatting.Indented
            });
            // var jsonObj = JsonConvert.DeserializeObject<List<ModelResponse>>(jsonStr);            
            List<object> deployedModels = new List<object>();
            string zsResponse = string.Empty;
            //try-catch block
            try
            {
                zsResponse = await zsClient.GetModels(ZSSettingPayload.GetUserNameOrEmail(HttpContext));
                if (!string.IsNullOrEmpty(zsResponse) && !zsResponse.Contains(ZMMConstants.ErrorFailed))
                {
                    JObject jo = JObject.Parse(zsResponse);
                    foreach (var m in jo["models"])
                    {
                        deployedModels.Add(new { Id = m, Name = m, Type = "PMML" });
                    }
                }
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.StackTrace);
                return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
            }
            return Json(deployedModels);
        }
        #endregion
        //
        #endregion

        #region modify model filename
        [HttpPut("{id}/rename")]
        public async Task<IActionResult> ModifyFilenameAsync(string id)
        {
            string newFileName = "";
            string reqBody = "";
            await System.Threading.Tasks.Task.FromResult(0);
            try
            {
                //read request body
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }
                //get new filename
                if (!string.IsNullOrEmpty(reqBody))
                {
                    var content = JObject.Parse(reqBody);
                    newFileName = (string)content["newName"];
                    newFileName = Regex.Replace(newFileName, "[\n\r\t]", string.Empty);
                    newFileName = Regex.Replace(newFileName, @"\s", string.Empty);
                }

                if (!string.IsNullOrEmpty(newFileName))
                {
                    //if same name exist - BadRequest
                    foreach (var record in responseData)
                    {
                        if (record.Id.ToLower() == newFileName.ToLower())
                        {
                            return BadRequest(new { message = "File with same name already exists." });
                        }
                    }
                    //rename the file and/or folder
                    foreach (var record in responseData)
                    {
                        if (record.Id.ToString() == id)
                        {
                            var newfilePath = record.FilePath.Replace($"{id}.{record.Extension}", $"{newFileName}.{record.Extension}");
                            FileFolderHelper.RenameFile(record.FilePath, newfilePath);
                            var newRecord = new ModelResponse()
                            {
                                Created_on = record.Created_on,
                                Edited_on = record.Edited_on,
                                Extension = record.Extension,
                                FilePath = newfilePath,
                                Id = newFileName,
                                MimeType = record.MimeType,
                                Name = $"{newFileName}.{record.Extension}",
                                Properties = record.Properties,
                                Size = record.Size,
                                Type = record.Type,
                                Url = record.Url.Replace(id, newFileName),
                                User = record.User
                            };
                            ModelPayload.Create(newRecord);
                            ModelPayload.RemoveOnlyFromModelPayload(id);
                            return Json(newRecord);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                return BadRequest(new { message = "Renaming file failed.", exception = ex.StackTrace });
            }

            return BadRequest(new { message = "Renaming file failed." });
        }
        #endregion

    }
}
