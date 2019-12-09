using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ZMM.App.PyServicesClient;
using Microsoft.Extensions.Logging;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Payloads;
using ZMM.Helpers.ZMMDirectory;
using ZMM.Helpers.Common;
using ZMM.Tools.JNB;
using ZMM.Tasks;
using System.Text.RegularExpressions;
using Quartz;
using Quartz.Impl;

namespace ZMM.App.Controllers
{
    [Authorize]
    [Route("api/[controller]")]
    public class CodeController : Controller
    {
        #region Variables... 
        private readonly IWebHostEnvironment _environment;
        readonly ILogger<CodeController> Logger;
        public IConfiguration Configuration { get; }
        private readonly IPyJupyterServiceClient jupyterClient;
        private readonly IPyCompile pyCompileClient;
        private List<CodeResponse> codeResponse;

        private readonly string BASEURLJUP;
        private static string[] extensions = new[] { "py", "ipynb","r" };

        private readonly IScheduler _scheduler;

        #endregion

        #region Constructor...
        public CodeController(IWebHostEnvironment environment, IConfiguration configuration, ILogger<CodeController> log, IPyJupyterServiceClient _jupyterClient, IPyCompile _pyCodeCompile, IScheduler factory)
        {
            //update 
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));
            this.Configuration = configuration;
            this.jupyterClient = _jupyterClient;
            this.pyCompileClient = _pyCodeCompile;
            _scheduler = factory;
            this.Logger = log;
            this.BASEURLJUP = Configuration["JupyterServer:srvurl"];
            try
            {
                codeResponse = CodePayload.Get();
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.StackTrace);
            }
        }
        #endregion

        #region Post - upload file...
        // POST api/Code
        [HttpPost]
        public async Task<IActionResult> Post(List<IFormFile> file)
        {
            List<CodeResponse> response = new List<CodeResponse>();
            List<CodeResponse> existingCodeData = new List<CodeResponse>();
            long size = file.Sum(f => f.Length);
            bool IsFileExists = false;
            string type, dirFullpath, nbPath, _url = string.Empty;
            // full path to file in temp location
            var filePath = Path.GetTempFileName();

            foreach (var formFile in file)
            {
                dirFullpath = DirectoryHelper.GetCodeDirectoryPath();
                if (formFile.Length > 0)
                {
                    //check if the file with the same name exists
                    existingCodeData = CodePayload.Get();
                    if (existingCodeData.Count > 0)
                    {
                        //
                        foreach (var record in existingCodeData)
                        {
                            if (record.Name == formFile.FileName)
                            {
                                IsFileExists = true;
                            }
                        }
                    }
                    existingCodeData.Clear();
                    //
                    if (!IsFileExists)
                    {
                        var fileExt = System.IO.Path.GetExtension(formFile.FileName).Substring(1);
                        if (fileExt.ToLower() == "ipynb")
                        {
                            dirFullpath = dirFullpath + formFile.FileName.Replace(".ipynb", "/");
                            _url = DirectoryHelper.GetCodeUrl(formFile.FileName.Replace(".ipynb", string.Empty) + "/" + formFile.FileName);
                        }
                        else
                        {
                            _url = DirectoryHelper.GetCodeUrl(formFile.FileName);
                        }
                        nbPath = dirFullpath + formFile.FileName;

                        //check if folder path exists...if not then create folder
                        if (!Directory.Exists(dirFullpath))
                        {
                            Directory.CreateDirectory(dirFullpath);
                        }
                        // upload file start
                        using (var fileStream = new FileStream(Path.Combine(dirFullpath, formFile.FileName), FileMode.Create))
                        {
                            //check file allowed extensions                         
                            if (!extensions.Contains(fileExt.ToString().ToLower()))
                            {
                                return BadRequest("File type not allowed");
                            }

                            //file copy
                            await formFile.CopyToAsync(fileStream);

                            // upload file edn and start creating payload
                            switch (fileExt.ToLower())
                            {
                                case "py":
                                    type = "PYTHON";
                                    break;
                                case "ipynb":
                                    type = "JUPYTER_NOTEBOOK";
                                    break;
                                case "r":
                                    type = "R";
                                    break;
                                default:
                                    type = "UNRECOGNIZED";
                                    break;
                            }

                            CodeResponse newRecord = new CodeResponse()
                            {
                                Id = formFile.FileName.Replace("." + fileExt, ""),
                                Name = formFile.FileName,
                                User = "",
                                Created_on = DateTime.Now.ToString(),
                                Edited_on = DateTime.Now.ToString(),
                                Extension = fileExt,
                                MimeType = formFile.ContentType,
                                Size = formFile.Length,
                                Type = type,
                                Url = _url,
                                FilePath = nbPath,
                                DateCreated = DateTime.Now
                            };
                            CodePayload.Create(newRecord);
                            response.Add(newRecord);
                        }
                    }
                }
                IsFileExists = false;
            }

            if (response.Count > 0)
                return Ok(response);
            else
                return BadRequest("File already exists.");
        }
        #endregion

        #region Get

        [HttpGet]
        public IActionResult Get(bool refresh)
        {
            //
            if (refresh)
            {
                CodePayload.Clear();
                InitZmodDirectory.ScanCodeDirectory();
                codeResponse = CodePayload.Get();
            }

            //
            string jsonStr = JsonConvert.SerializeObject(codeResponse, Formatting.None);
            try
            {
                if (!string.IsNullOrEmpty(jsonStr))
                {
                    var jsonObj = JsonConvert.DeserializeObject<List<CodeResponse>>(jsonStr);
                    return Json(jsonObj);
                }
                else
                {
                    return Ok(new { message = "No Content", errorCode = 204, exception = "No Content" });
                }
            }
            catch (Exception ex)
            {
                return BadRequest(new { message = "Server error.", errorCode = 404, exception = ex.StackTrace });
            }

        }

        [HttpGet("{id}")]
        public async Task<IActionResult> Get(string id)
        {
            string fileContent = string.Empty;
            string filePath = FilePathHelper.GetFilePathById<CodeResponse>(id, codeResponse);
            string fileName = Path.GetFileName(filePath);
            CodeResponse _meta = new CodeResponse();
            JObject jsonObj = new JObject();

            //get file metadata
            foreach (var record in codeResponse)
            {
                if (record.Id.ToString() == id)
                {
                    fileName = record.Name;
                    _meta = record;
                }
            }

            try
            {
                if (!string.IsNullOrEmpty(fileName))
                {
                    using (StreamReader reader = new StreamReader(filePath))
                    {
                        fileContent = await reader.ReadToEndAsync();
                    }
                }

                string strjObj = JsonConvert.SerializeObject(_meta);
                JObject jObjCode = JObject.Parse(strjObj);

                //JObject jsonObj = JObject.Parse(); 
                jsonObj.Add("code", fileContent);

                jObjCode.Merge(jsonObj, new JsonMergeSettings
                {
                    // union array values together to avoid duplicates
                    MergeArrayHandling = MergeArrayHandling.Union
                });

                return Json(jObjCode);
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message);
            }
        }

        #endregion

        #region Post...
        [HttpPost("{id}")]
        public async Task<IActionResult> Post(string id, [FromBody] RequestParam fileContent)
        {
            string filePath = FilePathHelper.GetFilePathById<CodeResponse>(id, codeResponse);

            try
            {
                using (StreamWriter outputFile = new StreamWriter(filePath))
                {
                    await outputFile.WriteAsync(fileContent.FileContent);
                }
                return Ok(new { message = "File successfully updated." });
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message);
            }
        }
        #endregion

        #region Delete...
        [HttpDelete("{id}")]
        public IActionResult Delete(string id)
        {
            if(InstancePayload.IsInstanceExists(id) && CodePayload.GetById(id).Type == "JUPYTER_NOTEBOOK")
            {
                return BadRequest(new { user = string.Empty, id = id, message = "Error deleting file. Instance of the file is running. Check Assests module" });
            }

            bool result = CodePayload.Delete(id);

            if (result == true)
            {
                return Ok(new { user = string.Empty, id = id, message = "File deleted successfully." });
            }
            else
            {
                return BadRequest(new { user = string.Empty, id = id, message = "Error deleting file. Try again or contact adminstrator." });
            }
        }
        #endregion

        #region Jupyter related apis

        #region start jupyter nb
        [HttpGet("{id}/jupyter")]
        public async Task<IActionResult> GetJupyterNotebookUrlAsync(string id)
        {
            string response = string.Empty;
            string _jUrl = string.Empty;
            string message = "Notebook is up and running successfully";
            //We needs to populate Current User from request       
            string CURRENT_USER = string.Empty;
            string ResourcePath = Helpers.Common.FilePathHelper.GetFilePathById(id, codeResponse);
            FileInfo resourceInfo = new System.IO.FileInfo(ResourcePath);
            string notebookDir = resourceInfo.Directory.ToString();
            string notebookLinkURL = string.Empty;

            var obj = new
            {
                base_url = "/",
                NotebookDir = $"{notebookDir}",
                ResourcePath = $"{ResourcePath}"
            };
            try
            {
                var portRegex = new Regex(@"(?<![^/]/[^/]*):\d+");//to remove port number
                JupyterNotebook JNBTool = this.jupyterClient.GetJupyterNotebookTool();
                await System.Threading.Tasks.Task.FromResult(0);
                ITask JupyterNoteBookTask = JNBTool.FindTask(ResourcePath);
                if (JupyterNoteBookTask.IsEmpty())
                {
                    JNBTool.StartTaskAsync((int)TaskTypes.Start, ResourcePath, (JObject)JObject.FromObject(obj));
                }
                notebookLinkURL = JNBTool.GetResourceLink(ResourcePath);
                // notebookLinkURL = @"C:\myCode\Project\ZMOD\code\1_SVM\1_SVM.ipynb";
                //
                // JupyterNotebook nb = JupyterNotebook.Find(ResourcePath);
                var objJNBInst = new InstanceResponse()
                {
                    Id = id,
                    Name = $"{id}.ipynb",
                    Type = "JNB"
                    // Properties = new List<InstanceProperty>(){ new InstanceProperty{ key="port", value=nb.Info.Port}}
                };
                InstancePayload.Create(objJNBInst);
                notebookLinkURL = notebookLinkURL.Replace(@"//", @"/");
                //
                return Ok(new { user = CURRENT_USER, id = id, message = message, url = notebookLinkURL.Replace(notebookLinkURL.Substring(0, notebookLinkURL.IndexOf("jnb")), "") });
            }
            catch (Exception ex)
            {
                message = ex.Message;
                return BadRequest(new { user = CURRENT_USER, id = id, message = message });
            }
        }

        #endregion


        #endregion

        #region Download file...
        [HttpGet("{id}/download")]
        public async Task<IActionResult> Download(string id)
        {
            string fileUrl = string.Empty;
            string filePath = string.Empty;
            string type = string.Empty;
            string _contentType = string.Empty;
            try
            {
                filePath = FilePathHelper.GetFilePathById<CodeResponse>(id, codeResponse);
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

                switch (type.ToLower())
                {
                    case ".py":
                        _contentType = "application/py";
                        break;

                    case ".ipynb":
                        _contentType = "application/ipynb";
                        break;
                }
                return File(memory, _contentType, fileName);
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message + "filepath :" + filePath);
            }
        }
        #endregion

        #region modify code filename
        [HttpPut("{id}/rename")]
        public async Task<IActionResult> ModifyFilenameAsync(string id)
        {
            string newFileName = "";
            string newDirFullPath = "";
            string dirFullpath = DirectoryHelper.GetCodeDirectoryPath();
            string reqBody = "";
            await System.Threading.Tasks.Task.FromResult(0);
            //
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
                //if same name exist - BadRequest
                foreach (var record in codeResponse)
                {
                    if (record.Id.ToLower() == newFileName.ToLower())
                    {
                        return BadRequest(new { message = "File with same name already exists." });
                    }
                }

                if (!string.IsNullOrEmpty(newFileName))
                {
                    //rename the file and/or folder
                    foreach (var record in codeResponse)
                    {
                        if (record.Id.ToString() == id)
                        {
                            if (record.Type == "JUPYTER_NOTEBOOK")
                            {
                                //check if folder path exists...if not then move folder
                                newDirFullPath = $"{dirFullpath}{newFileName}";
                                if (!Directory.Exists(newDirFullPath))
                                {
                                    Directory.Move($"{dirFullpath}{id}", newDirFullPath);
                                    FileFolderHelper.RenameFile($"{newDirFullPath}/{id}.{record.Extension}", $"{newDirFullPath}/{newFileName}.{record.Extension}");
                                    newDirFullPath = $"{newDirFullPath}/{newFileName}.{record.Extension}";
                                }
                                else
                                    return BadRequest(new { message = "Folder with same name already exists. Please choose different file/folder name." });
                            }
                            else
                            {
                                newDirFullPath = record.FilePath.Replace($"{id}.{record.Extension}", $"{newFileName}.{record.Extension}");
                                FileFolderHelper.RenameFile(record.FilePath, newDirFullPath);
                            }
                            //update GlobalStorage dictionary
                            CodeResponse newRecord = new CodeResponse()
                            {
                                Id = newFileName,
                                Name = $"{newFileName}.{record.Extension}",
                                User = "",
                                Created_on = record.Created_on,
                                Edited_on = record.Edited_on,
                                Extension = record.Extension,
                                MimeType = record.MimeType,
                                Size = record.Size,
                                Type = record.Type,
                                Url = record.Url.Replace(id, newFileName),
                                FilePath = newDirFullPath,
                                DateCreated = record.DateCreated
                            };
                            CodePayload.Create(newRecord);
                            CodePayload.RemoveOnlyFromCodePayload(id);
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

        #region py compile and execute
        #region compile
        [HttpGet("{id}/compile")]
        public async Task<IActionResult> CompilePyAsync(string id)
        {
            string zmkResponse = "";
            string filePath = "";
            try
            {
                foreach (var record in codeResponse)
                {
                    if (record.Id.ToString() == id)
                    {
                        filePath = record.FilePath;
                        break;
                    }
                }
                if (!string.IsNullOrEmpty(filePath))
                {
                    zmkResponse = await pyCompileClient.CompilePy(filePath);
                    JObject json = JObject.Parse(zmkResponse);
                    return Json(json);
                }
                else
                {
                    return BadRequest(new { message = "File compilation failed." });
                }
            }
            catch (Exception ex)
            {
                return BadRequest(new { message = "File compilation failed.", exception = ex.StackTrace });
            }
        }
        #endregion

        #region execute (ScheduledJob)
        [HttpPost("{id}/execute")]
        public async Task<IActionResult> ExecutePyAsync(string id)
        {
            string zmkResponse = "";
            string filePath = "";
            string reqBody = "";
            try
            {
                //read cron information from the request body
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }

                //
                foreach (var record in codeResponse)
                {
                    if (record.Id.ToString() == id)
                    {
                        filePath = record.FilePath;
                        break;
                    }
                }
                //
                if (!string.IsNullOrEmpty(filePath))
                {
                    zmkResponse = await pyCompileClient.ExecutePy(filePath, "");
                    var jsonObj = JsonConvert.DeserializeObject<ExecuteCodeResponse>(zmkResponse);
                    jsonObj.executedAt = DateTime.Now;
                    List<ExecuteCodeResponse> tresp = new List<ExecuteCodeResponse>();
                    tresp.Add(jsonObj);

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
                            #region create quartz job for execute code
                            ITrigger trigger = TriggerBuilder.Create()
                            .WithIdentity($"Execute Code Job-{DateTime.Now}")
                            .WithCronSchedule(cronjson["cronExpression"].ToString())
                            .WithPriority(1)
                            .Build();

                            IJobDetail job = JobBuilder.Create<ExecuteCodeJob>()
                            .WithIdentity(filePath)
                            .Build();

                            job.JobDataMap["id"] = id;
                            job.JobDataMap["filePath"] = filePath;
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
                                Type = "PYTHON",
                                Url = "",
                                Recurrence = cronjson["recurrence"].ToString(),
                                StartDate = cronjson["startDate"].ToString(),
                                StartTimeH = (cronjson["startTimeH"].ToString() == null) ? "" : cronjson["startTimeH"].ToString(),
                                StartTimeM = (cronjson["startTimeM"].ToString() == null) ? "" : cronjson["startTimeM"].ToString(),
                                ZMKResponse = tresp.ToList<object>()
                            };
                            SchedulerPayload.Create(schJob);
                            #endregion
                        }
                    }
                    else
                    {
                        //add history
                        JArray jHist = new JArray();
                        foreach(var r in tresp)
                        {
                            jHist.Add(new JObject(){
                                    {"idforData", r.idforData},
                                    {"status", r.status},
                                    {"executedAt",r.executedAt}
                                });
                        }
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
                            Type = "PYTHON",
                            Url = "",
                            Recurrence = "ONE_TIME",
                            StartDate = "",
                            StartTimeH = "",
                            StartTimeM = "",
                            ZMKResponse = tresp.ToList<object>(),
                            Status = "",
                            History = jHist.ToList<object>()
                        };
                        
                        
                        SchedulerPayload.Create(schJob);
                    }


                    return Json(jsonObj);
                }
                else
                {
                    return BadRequest(new { message = "File execution failed." });
                }
            }
            catch (Exception ex)
            {
                return BadRequest(new { message = "File execution failed.", exception = ex.StackTrace });
            }
        }
        #endregion
        #endregion
    }
}