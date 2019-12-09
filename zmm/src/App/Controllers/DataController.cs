using System;
using System.Text;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Net.Http.Headers;
using Microsoft.AspNetCore.Hosting;
using System.IO;
using System.Threading;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Extensions;
using System.Net;
using Microsoft.AspNetCore.Cors;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ZMM.App.PyServicesClient;
using Microsoft.Extensions.Configuration;
using Microsoft.AspNetCore.WebUtilities;
using System.Drawing;
using Microsoft.Extensions.Logging;
using ZMM.Models.Payloads;
using ZMM.Helpers.Extensions;
using ZMM.Helpers.ZMMDirectory;
using ZMM.Helpers.Common;
using ZMM.Helpers.Zipper;
using ZMM.Models.ResponseMessages;
using Newtonsoft.Json.Serialization;
using ZMM.App.ZSServiceClient;
using Microsoft.AspNetCore.Mvc.ModelBinding;
using Helpers.CustomAttributes;
using xml = System.Xml;
using System.Data;
using System.Text.RegularExpressions;

namespace ZMM.App.Controllers
{
    [Authorize]
    [Route("api/[controller]")]
    public class DataController : Controller
    {
        #region Variables
        private readonly IWebHostEnvironment _environment;
        private IConfiguration Configuration { get; }
        readonly ILogger<DataController> Logger;
        private readonly IPyAutoMLServiceClient _client;
        private readonly IPyNNServiceClient _nnclient;
        private readonly IZSModelPredictionClient zsClient;

        private readonly IBaseImageForWielding baseImageClient;

        private List<DataResponse> responseData;
        private List<ModelResponse> modelResponseData;
        private List<CodeResponse> codeResponseData;
        private static string[] extensions = new[] { "csv", "jpg", "jpeg", "png", "json", "webp", "zip", "mp4", "txt" };
        string zipOr7zPath = string.Empty;
        string extractPath = string.Empty;
        string fileName = string.Empty;
        private readonly string CURRENT_USER = "";
        private static bool IsScanned = false;
        #endregion

        #region Constructor...
        public DataController(IWebHostEnvironment environment, IConfiguration configuration, ILogger<DataController> log, IPyAutoMLServiceClient srv, IPyNNServiceClient nnsrv, IZSModelPredictionClient _zsClient,
            IBaseImageForWielding _baseImageClient)
        {
            this._client = srv;
            this._nnclient = nnsrv;
            this.zsClient = _zsClient;
            this.baseImageClient = _baseImageClient;
            this.Configuration = configuration;
            this.Logger = log;
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));

            //Initialise ZMOD Dir scanning
            if (!IsScanned)
            {
                ZMKDockerCmdHelper.InitZMKInstances();
                InitZmodDirectory.ScanDirectoryToSeed();
                IsScanned = true;
            }
            //
            // InitZmodDirectory.ScanDirectoryToSeed();
            //
            responseData = DataPayload.Get();
            modelResponseData = ModelPayload.Get();
            codeResponseData = CodePayload.Get();
        }

        #endregion

        #region Get uploaded data - api/data
        [HttpGet]
        public async Task<IActionResult> Get(string[] type, bool refresh)
        {
            //
            if (refresh)
            {
                DataPayload.Clear();
                InitZmodDirectory.ScanDataDirectory();
                responseData = DataPayload.Get();
            }
            //
            string jsonStr = JsonConvert.SerializeObject(responseData, Formatting.Indented);
            // jsonStr = jsonStr.ToPrettyJsonString();
            var jsonObj = JsonConvert.DeserializeObject<List<DataResponse>>(jsonStr);

            List<DataResponse> _data = new List<DataResponse>();
            //
            if (type.Length > 0)
            {
                foreach (string _type in type)
                {
                    if (!string.IsNullOrEmpty(_type))
                    {
                        foreach (var record in jsonObj)
                        {
                            if (record.Type.ToLower() == _type.ToLower())
                            {
                                _data.Add(record);
                            }
                        }
                    }
                }
                await Task.FromResult(0);
                return Json(_data);
            }

            return Json(jsonObj);
        }
        #endregion

        #region POST api/Data - Upload Data file
        [HttpPost]
        [RequestFormLimits(MultipartBodyLengthLimit = 2147483648)]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> PostAsync(List<IFormFile> file)
        {
            #region variables
            List<DataResponse> _response = new List<DataResponse>();
            List<Property> _props = new List<Property>();
            List<DataResponse> existingData = new List<DataResponse>();
            long size = file.Sum(f => f.Length);
            string type = string.Empty;
            bool IsFileExists = false;
            // path variables
            var filePath = Path.GetTempFileName();
            string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
            string fileContent = string.Empty;
            #endregion

            #region check for multipart
            if (!MultipartRequestHelper.IsMultipartContentType(Request.ContentType))
            {
                return BadRequest($"Expected a multipart request, but got {Request.ContentType}");
            }
            #endregion

            try
            {
                //check if folder path exists...if not then create folder
                if (!Directory.Exists(dirFullpath))
                {
                    Directory.CreateDirectory(dirFullpath);
                }

                foreach (var formFile in file)
                {
                    if (formFile.Length > 0)
                    {
                        fileName = formFile.FileName;
                        //check if the file with the same name exists
                        existingData = DataPayload.Get();
                        if (existingData.Count > 0)
                        {
                            //
                            foreach (var record in existingData)
                            {
                                if (record.Name == fileName)
                                {
                                    IsFileExists = true;
                                }
                            }
                        }
                        existingData.Clear();
                        //
                        if (!IsFileExists)
                        {
                            string fileUrl = Path.Combine(dirFullpath, fileName);
                            string fileExt = System.IO.Path.GetExtension(fileUrl).Substring(1).ToLower();
                            FileStream fileStream;

                            using (fileStream = new FileStream(fileUrl, FileMode.Create))
                            {
                                //check file allowed extensions
                                if (!extensions.Contains(fileExt))
                                {
                                    return BadRequest("File type not allowed");
                                }
                                else
                                {
                                    // uploading file ...
                                    try
                                    {
                                        await formFile.CopyToAsync(fileStream);
                                    }
                                    catch (Exception ex)
                                    {
                                        Logger.LogCritical(ex, ex.Message);
                                        return BadRequest("File upload failed");
                                    }
                                }
                            }

                            if (formFile.ContentType.Contains("image"))
                            {
                                type = "IMAGE";
                                using (var image = new Bitmap(fileUrl))
                                {
                                    _props.Add(new Property { key = "Width", value = image.Width.ToString() + " px" });
                                    _props.Add(new Property { key = "Height", value = image.Height.ToString() + " px" });
                                    image.Dispose();
                                }
                            }
                            else if (formFile.ContentType.Contains("json") || fileExt == "json")
                            {
                                type = "JSON";
                                //read json file from filestream
                                if (!string.IsNullOrEmpty(fileName))
                                {
                                    using (StreamReader reader = new StreamReader(fileUrl))
                                    {
                                        fileContent = await reader.ReadToEndAsync();
                                    }
                                }
                                //parse
                                if (!string.IsNullOrEmpty(fileContent))
                                {
                                    JsonTextReader reader = new JsonTextReader(new StringReader(fileContent));
                                    int objCtr = 0;
                                    while (reader.Read())
                                    {
                                        if (reader.TokenType == JsonToken.EndObject)
                                        {
                                            objCtr++;
                                        }
                                    }
                                    _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });

                                }
                            }
                            else if (formFile.ContentType.Contains("csv") || fileExt == "csv" || formFile.ContentType.Contains("excel")
                                || formFile.ContentType.Contains("comma-separated-value"))
                            {
                                type = "CSV";
                                //get properties row and column count
                                int[] csvProps = CsvHelper.GetCsvRowColumnCount(dirFullpath + @"/" + fileName);
                                _props.Add(new Property { key = "Number of rows", value = csvProps[0].ToString() });
                                _props.Add(new Property { key = "Number of columns", value = csvProps[1].ToString() });
                            }
                            else if (formFile.ContentType.Contains("zip") || fileExt == "zip")
                            {
                                type = "FOLDER";
                                string zipFileName = fileName.Substring(0, fileName.Length - 4);

                                //extract
                                await ZipHelper.ExtractAsync(fileStream.Name, $"{dirFullpath}{zipFileName}");
                                //add properties
                                _props.Add(new Property
                                {
                                    key = "Subdirectories",
                                    value = DirectoryHelper.CountDirectories(fileStream.Name.Replace(".zip", "")).ToString()
                                });
                                _props.Add(new Property
                                {
                                    key = "Files",
                                    value = DirectoryHelper.CountFiles(fileStream.Name.Replace(".zip", "")).ToString()
                                });

                                //extract end
                                fileName = formFile.FileName.Replace(".zip", "");
                            }
                            else if (formFile.ContentType.Contains("mp4") || fileExt == "mp4")
                            {
                                type = "VIDEO";
                            }
                            else if (formFile.ContentType.Contains("text") || fileExt == "txt")
                            {
                                type = "TEXT";
                            }
                            else
                            {
                                type = "UNRECOGNIZED";
                            }
                            //
                            string _url = DirectoryHelper.GetDataUrl(formFile.FileName);
                            string _filePath = Path.Combine(dirFullpath, fileName);
                            //
                            DataResponse newRecord = new DataResponse()
                            {
                                Created_on = DateTime.Now.ToString(),
                                Edited_on = DateTime.Now.ToString(),
                                Extension = fileExt,
                                FilePath = _filePath,
                                Id = fileName.Replace($".{fileExt}", ""),
                                MimeType = formFile.ContentType,
                                Name = fileName,
                                Properties = _props,
                                Size = formFile.Length,
                                Type = type,
                                Url = _url,
                                User = CURRENT_USER,
                                DateCreated = DateTime.Now
                            };
                            //
                            _response.Add(DataPayload.Create(newRecord));
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message + "filepath :" + filePath);

            }

            if (_response.Count > 0)
                return Ok(_response);
            else
                return BadRequest("File already exists.");
        }
        #endregion

        #region Delete Data...
        [HttpDelete("{id}")]
        public IActionResult Delete(string id)
        {
            //TODO: update currentuser from keycloak
            bool result = DataPayload.Delete(id);
            if (result == true)
            {
                return Ok(new { user = CURRENT_USER, id = id, message = "File deleted successfully." });
            }
            else
            {
                return BadRequest(new { exception = "", id = id, message = "Error deleting file. Try again or contact adminstrator." });
            }
        }
        #endregion

        #region AutoML Preprocessing form...
        [HttpGet]
        [Route("{id}/automl")]
        public async Task<IActionResult> GetAutoML(string id)
        {
            string response = string.Empty;
            string filePath = string.Empty;
            JObject jsonObj = new JObject();

            foreach (var item in responseData)
            {
                if (item.Id.ToString() == id)
                {
                    filePath = item.FilePath;
                    break;
                }
            }
            try
            {
                response = await _client.GetPreprocessingForm(filePath);
                if (!string.IsNullOrEmpty(response))
                {
                    jsonObj = JObject.Parse(response);
                }
                return Json(jsonObj);
            }
            catch (Exception ex)
            {
                return BadRequest(ex.StackTrace);
            }
        }

        [HttpPost]
        [Route("{id}/automl")]
        public async Task<IActionResult> PostAutoML(string id)
        {
            string response = string.Empty;
            string reqBody = string.Empty;
            string userModelName = "";
            if (Request.Body != null)
            {
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }
                try
                {
                    //find model name
                    JObject rB = JObject.Parse(reqBody);
                    userModelName = (string)rB["parameters"]["model_name"];
                    //
                    response = await _client.PostProcessingForm(reqBody);
                }
                catch (Exception ex)
                {
                    //TO DO: ILogger
                    string _ex = ex.Message;
                }

                if (!string.IsNullOrEmpty(response))
                {
                    var jo = JsonConvert.DeserializeObject<AutoMLResponse>(response);
                    jo.executedAt = DateTime.Now;
                    List<AutoMLResponse> tresp = new List<AutoMLResponse>();
                    tresp.Add(jo);
                    //
                    //add to scheduler payload 
                    //add history
                    JArray jHist = new JArray();
                    foreach (var r in tresp)
                    {
                        jHist.Add(new JObject(){
                        {"idforData", r.idforData},
                        {"status", r.status},
                        {"executedAt",r.executedAt}
                    });
                    }
                    string idExisted = SchedulerPayload.GetById(id).Where(i => i.Type == "AUTOML" && i.Id == id).Select(i => i.Id).FirstOrDefault();
                    if (idExisted == id)
                    {
                        id = id + userModelName;
                    }

                    SchedulerResponse schJob = new SchedulerResponse()
                    {
                        CreatedOn = DateTime.Now.ToString(),
                        CronExpression = "",
                        DateCreated = DateTime.Now,
                        EditedOn = DateTime.Now.ToString(),
                        FilePath = "",
                        Id = id,
                        Name = userModelName,
                        Type = "AUTOML",
                        Url = "",
                        Recurrence = "ONE_TIME",
                        StartDate = "",
                        StartTimeH = "",
                        StartTimeM = "",
                        ZMKResponse = tresp.ToList<object>(),
                        Status = "COMPLETED",
                        History = jHist.ToList<object>()
                    };
                    SchedulerPayload.Create(schJob);

                    //
                    JObject jsonObj = JObject.Parse(response);
                    return Json(jsonObj);
                }
                else
                {
                    return NoContent();
                }
            }
            else
                return NoContent();
        }
        #endregion   

        #region Predict data...
        [HttpGet]
        [Route("predict")]
        public async Task<IActionResult> GetPrediction([FromQuery] string dataId, [FromQuery] string modelId)
        {
            string response = string.Empty;
            string modelName = string.Empty;
            string filePath = string.Empty;
            string data = string.Empty;
            long fileSize;
            JObject joPredict = new JObject();
            JObject joData = new JObject();

            string jsonDataStr = JsonConvert.SerializeObject(responseData, Formatting.None);
            string jsonModelStr = JsonConvert.SerializeObject(modelResponseData, Formatting.None);

            var jsonDataObj = JsonConvert.DeserializeObject<List<DataResponse>>(jsonDataStr);
            var jsonModelObj = JsonConvert.DeserializeObject<List<ModelResponse>>(jsonModelStr);

            //get modelname from modelid
            foreach (var record in jsonModelObj)
            {
                if (record.Id.ToString() == modelId)
                {
                    modelName = record.Name;
                    break;
                }
            }
            //get filepath from dataid= data.url
            foreach (var record in jsonDataObj)
            {
                if (record.Id.ToString() == dataId)
                {
                    filePath = record.FilePath;
                    break;
                }
            }
            try
            {
                //Get prediction and filepath
                response = await _nnclient.GetPredictionForImage(modelName, filePath);
                if (!string.IsNullOrEmpty(response))
                {
                    joPredict = JObject.Parse(response);
                }

                //send to py server
                if (!string.IsNullOrEmpty(joPredict.ToString()))
                {
                    data = await _client.SaveBestPmml(joPredict["result"].ToString());
                }
                string resultPath = joPredict["result"].ToString();
                string dirFullpath = string.Empty;

                //write the content of file and download
                #region save csv, txt and mp4
                if (resultPath.Contains("csv") && !string.IsNullOrEmpty(data))
                {
                    List<Property> _props = new List<Property>();
                    dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                    string newFile = $"Predicted_{dataId}" + ".csv";
                    string newFilePath = Path.Combine(dirFullpath, newFile);
                    if (!Directory.Exists(dirFullpath))
                    {
                        Directory.CreateDirectory(dirFullpath);
                    }
                    using (StreamWriter writer = new StreamWriter(Path.Combine(dirFullpath, newFile)))
                    {
                        await writer.WriteLineAsync(data);
                        writer.Flush();
                        fileSize = writer.BaseStream.Length;
                    }
                    //add to DataPayload
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = DateTime.Now.ToString(),
                        Edited_on = DateTime.Now.ToString(),
                        Extension = "csv",
                        FilePath = dirFullpath + newFile,
                        Id = newFile.Replace($".csv", ""),
                        MimeType = "application/json",
                        Name = newFile,
                        Properties = _props,
                        Size = fileSize,
                        Type = "CSV",
                        Url = DirectoryHelper.GetDataUrl(newFile),
                        User = CURRENT_USER,
                        DateCreated = DateTime.Now
                    };
                    DataPayload.Create(newRecord);
                    return Json(newRecord);
                }
                else if (resultPath.Contains("txt") && !string.IsNullOrEmpty(data))
                {
                    //create blank file
                    dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                    string newFile = $"Predicted_{dataId}" + ".json";
                    string newFilePath = Path.Combine(dirFullpath, newFile);
                    //check if folder path exists...if not then create folder
                    if (!Directory.Exists(dirFullpath))
                    {
                        Directory.CreateDirectory(dirFullpath);
                    }

                    //delete if same file exists
                    DataPayload.Delete($"Predicted_{dataId}");

                    //writes the json file and closes the file. No need to use flush or close
                    System.IO.File.WriteAllText(newFilePath, data);
                    FileInfo f = new FileInfo(newFilePath);
                    long size = f.Length;

                    List<Property> _props = new List<Property>();
                    JsonTextReader reader = new JsonTextReader(new StringReader(data));
                    int objCtr = 0;
                    while (reader.Read())
                    {
                        if (reader.TokenType == JsonToken.EndObject)
                        {
                            objCtr++;
                        }
                    }
                    _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });


                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = DateTime.Now.ToString(),
                        Edited_on = DateTime.Now.ToString(),
                        Extension = "json",
                        FilePath = dirFullpath + newFile,
                        Id = newFile.Replace($".json", ""),
                        MimeType = "application/json",
                        Name = newFile,
                        Properties = _props,
                        Size = size,
                        Type = "JSON",
                        Url = DirectoryHelper.GetDataUrl(newFile),
                        User = CURRENT_USER,
                        DateCreated = DateTime.Now
                    };
                    DataPayload.Create(newRecord);
                    return Json(newRecord);
                }
                else if (resultPath.Contains("mp4") && !string.IsNullOrEmpty(data))
                {
                    //download mp4 file from resultPath
                    Byte[] dataMP4 = null;
                    dataMP4 = await _client.DownloadFile(joPredict["result"].ToString(), $"Predicted_{dataId}" + ".mp4");

                    List<Property> _props = new List<Property>();
                    dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                    string newFile = $"Predicted_{dataId}" + ".mp4";
                    string newFilePath = Path.Combine(dirFullpath, newFile);

                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = DateTime.Now.ToString(),
                        Edited_on = DateTime.Now.ToString(),
                        Extension = "mp4",
                        FilePath = dirFullpath + newFile,
                        Id = newFile.Replace($".mp4", ""),
                        MimeType = "video/mp4",
                        Name = newFile,
                        Properties = _props,
                        Size = dataMP4.Length,
                        Type = "VIDEO",
                        Url = DirectoryHelper.GetDataUrl(newFile),
                        User = CURRENT_USER,
                        DateCreated = DateTime.Now
                    };
                    DataPayload.Create(newRecord);
                    return Json(newRecord);
                }
                else
                {
                    return BadRequest(new { message = "", errorCode = "404", exception = "" });
                }
                #endregion
            }
            catch (Exception ex)
            {
                return BadRequest(new { message = ex.Message, errorCode = "404", exception = ex.StackTrace });
            }
        }
        #endregion

        #region download data
        [HttpGet("{id}/download")]
        public async Task<IActionResult> Download(string id)
        {
            string fileName, filePath, type, _contentType = "";
            try
            {
                DataResponse data = DataPayload.Get(id);
                fileName = data.Name;
                filePath = data.FilePath;
                type = data.Type;
                _contentType = data.MimeType;

                if (type == "FOLDER") filePath = filePath + ".zip";
                //
                var memory = new MemoryStream();
                using (var stream = new FileStream(filePath, FileMode.Open))
                {
                    await stream.CopyToAsync(memory);
                }
                memory.Position = 0;
                //                
                return File(memory, _contentType, fileName);
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.Message);
                return BadRequest(ex.Message);
            }
        }
        #endregion

        #region  Get single scoring - ZS endpoint
        [HttpGet("score")]
        public async Task<IActionResult> GetSingleScoringAsync([FromQuery] string dataId, [FromQuery] string modelId)
        {
            string modelName = "";
            string record = "";
            string filePath = "";
            string zsResponse = "";
            DataResponse _response = null;
            string jsonDataStr = JsonConvert.SerializeObject(responseData, Formatting.None);
            string jsonModelStr = JsonConvert.SerializeObject(modelResponseData, Formatting.None);

            jsonDataStr = jsonDataStr.ToPrettyJsonString();
            jsonModelStr = jsonModelStr.ToPrettyJsonString();

            var jsonDataObj = JsonConvert.DeserializeObject<List<DataResponse>>(jsonDataStr);
            var jsonModelObj = JsonConvert.DeserializeObject<List<ModelResponse>>(jsonModelStr);

            try
            {
                foreach (var record1 in jsonDataObj)
                {
                    if (record1.Id == dataId)
                    {

                        if (record1.Type == "IMAGE")
                        {
                            string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                            string newFile = $"Predicted_{dataId}.json";
                            string newFilePath = Path.Combine(dirFullpath, newFile);
                            // try
                            // {
                            #region get modelname and json data
                            // get filepath of the data selected
                            if (responseData.Count > 0)
                            {
                                foreach (var item in responseData)
                                {
                                    if (item.Id == dataId)
                                    {
                                        filePath = item.FilePath;
                                        break;
                                    }
                                }
                            }
                            // get modelname of the selected model 
                            if (modelResponseData.Count > 0)
                            {
                                foreach (var item in modelResponseData)
                                {
                                    if (item.Id == modelId)
                                    {
                                        modelName = item.ModelName;
                                        break;
                                    }
                                }
                                if (string.IsNullOrEmpty(modelName)) modelName = modelId;
                            }

                            #endregion
                            string zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                            zsResponse = await zsClient.ImageScoring(modelName, filePath, zmodId);
                            zsResponse = zsResponse.Replace("\n", "");
                            JObject jo = JObject.Parse(zsResponse.Replace("\"", "'"));
                            System.IO.File.WriteAllText(newFilePath, zsResponse);
                            FileInfo f = new FileInfo(newFilePath);
                            long size = f.Length;
                            //
                            List<Property> _props = new List<Property>();
                            JsonTextReader jreader = new JsonTextReader(new StringReader(zsResponse));
                            int objCtr = 0;
                            while (jreader.Read())
                            {
                                if (jreader.TokenType == JsonToken.EndObject)
                                {
                                    objCtr++;
                                }
                            }
                            _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });
                            _response = new DataResponse()
                            {
                                Created_on = DateTime.Now.ToString(),
                                Edited_on = DateTime.Now.ToString(),
                                Extension = "json",
                                FilePath = dirFullpath + newFile,
                                Id = newFile.Replace($".json", ""),
                                MimeType = "application/json",
                                Name = newFile,
                                Properties = _props,
                                Size = size,
                                Type = "JSON",
                                Url = DirectoryHelper.GetDataUrl(newFile),
                                User = CURRENT_USER,
                                DateCreated = DateTime.Now
                            };
                            DataPayload.Create(_response);
                            return Json(_response);

                            // }
                            //  catch (Exception ex)
                            // {
                            //     Logger.LogCritical(ex,ex.StackTrace);
                            //     return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
                            // }    
                        }
                        if (record1.Type == "JSON")
                        {
                            //create blank file
                            string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                            string newFile = $"Predicted_{dataId}.json";
                            string newFilePath = Path.Combine(dirFullpath, newFile);
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
                            // try
                            // {
                            #region get modelname and json data
                            // get filepath of the data selected
                            if (responseData.Count > 0)
                            {
                                foreach (var item in responseData)
                                {
                                    if (item.Id == dataId)
                                    {
                                        filePath = item.FilePath;
                                    }
                                }
                            }
                            // get modelname of the selected model 
                            if (modelResponseData.Count > 0)
                            {
                                foreach (var item in modelResponseData)
                                {
                                    if (item.Id == modelId)
                                    {
                                        modelName = item.ModelName;
                                    }
                                }
                            }

                            if (!string.IsNullOrEmpty(filePath))
                            {
                                using (StreamReader reader = new StreamReader(filePath))
                                {
                                    record = await reader.ReadToEndAsync();
                                }
                            }
                            #endregion
                            //     
                            string zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                            zsResponse = await zsClient.SingleScoring(modelName, record, zmodId);

                            zsResponse = zsResponse.Replace("\n", "");

                            JObject jo = JObject.Parse(zsResponse.Replace("\"", "'"));


                            //writes the json file and closes the file. No need to use flush or close
                            System.IO.File.WriteAllText(newFilePath, zsResponse);
                            FileInfo f = new FileInfo(newFilePath);
                            long size = f.Length;
                            //
                            List<Property> _props = new List<Property>();
                            JsonTextReader jreader = new JsonTextReader(new StringReader(zsResponse));
                            int objCtr = 0;
                            while (jreader.Read())
                            {
                                if (jreader.TokenType == JsonToken.EndObject)
                                {
                                    objCtr++;
                                }
                            }
                            _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });
                            _response = new DataResponse()
                            {
                                Created_on = DateTime.Now.ToString(),
                                Edited_on = DateTime.Now.ToString(),
                                Extension = "json",
                                FilePath = dirFullpath + newFile,
                                Id = newFile.Replace($".json", ""),
                                MimeType = "application/json",
                                Name = newFile,
                                Properties = _props,
                                Size = size,
                                Type = "JSON",
                                Url = DirectoryHelper.GetDataUrl(newFile),
                                User = CURRENT_USER,
                                DateCreated = DateTime.Now
                            };
                            DataPayload.Create(_response);
                            return Json(_response);
                        }
                        if (record1.Type == "CSV")
                        {
                            string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                            // string newFile = $"{dataId}_Predicted.json";

                            string newFile = $"Predicted_{dataId}.csv";

                            string newFilePath = Path.Combine(dirFullpath, newFile);
                            // try
                            // {
                            #region get modelname and json data
                            // get filepath of the data selected
                            if (responseData.Count > 0)
                            {
                                foreach (var item in responseData)
                                {
                                    if (item.Id == dataId)
                                    {
                                        filePath = item.FilePath;
                                    }
                                }
                            }
                            // get modelname of the selected model 
                            if (modelResponseData.Count > 0)
                            {
                                foreach (var item in modelResponseData)
                                {
                                    if (item.Id == modelId)
                                    {
                                        modelName = item.ModelName;
                                    }
                                }
                            }

                            #endregion
                            string zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                            zsResponse = await zsClient.MultipleScoring(modelId, filePath, zmodId);
                            zsResponse = zsResponse.Replace("\n", "");
                            JObject jo = JObject.Parse(zsResponse.Replace("\"", "'"));
                            string outputs = jo["outputs"].ToString();

                            xml.XmlNode xml = JsonConvert.DeserializeXmlNode("{records:{record:" + outputs + "}}");
                            xml.XmlDocument xmldoc = new xml.XmlDocument();
                            //Create XmlDoc Object
                            xmldoc.LoadXml(xml.InnerXml);
                            //Create XML Steam 
                            var xmlReader = new xml.XmlNodeReader(xmldoc);
                            DataSet dataSet = new DataSet();
                            //Load Dataset with Xml
                            dataSet.ReadXml(xmlReader);
                            //return single table inside of dataset
                            var csv = dataSet.Tables[0].ToCSV(",");

                            using (StreamWriter writer = new StreamWriter(Path.Combine(dirFullpath, newFile)))
                            {
                                await writer.WriteLineAsync(csv);
                                writer.Flush();
                                long fileSize = writer.BaseStream.Length;
                            }
                            List<Property> _props = new List<Property>();
                            JsonTextReader jreader = new JsonTextReader(new StringReader(zsResponse));
                            int objCtr = 0;
                            while (jreader.Read())
                            {
                                if (jreader.TokenType == JsonToken.EndObject)
                                {
                                    objCtr++;
                                }
                            }
                            _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });
                            _response = new DataResponse()
                            {
                                Created_on = DateTime.Now.ToString(),
                                Edited_on = DateTime.Now.ToString(),
                                // Extension = "json",

                                Extension = "csv",

                                FilePath = dirFullpath + newFile,
                                // Id = newFile.Replace($".json", ""),

                                Id = newFile.Replace($".csv", ""),

                                MimeType = "application/json",
                                Name = newFile,
                                Properties = _props,
                                // Size = size,
                                // Type = "JSON",

                                Type = "CSV",

                                Url = DirectoryHelper.GetDataUrl(newFile),
                                User = CURRENT_USER,
                                DateCreated = DateTime.Now
                            };
                            DataPayload.Create(_response);
                            return Json(_response);

                            // }
                            //  catch (Exception ex)
                            // {
                            //     Logger.LogCritical(ex,ex.StackTrace);
                            //     return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
                            // }    
                        }
                    }
                }
                return Json(_response);
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.StackTrace);
                return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
            }
        }
        #endregion

        #region  Get Multiple scoring using csv file - ZS endpoint
        [HttpGet("multiple")]
        public async Task<IActionResult> GetMultipleScoringAsync([FromQuery] string dataId, [FromQuery] string modelId)
        {
            await Task.FromResult(0);

            string modelName = "";
            string filePath = "";
            string zsResponse = "";
            //create blank file
            string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
            string newFile = $"MultipleScoring_{dataId}.json";
            string newFilePath = Path.Combine(dirFullpath, newFile);
            try
            {
                #region get modelname and json data
                // get filepath of the data selected
                if (responseData.Count > 0)
                {
                    foreach (var item in responseData)
                    {
                        if (item.Id == dataId)
                        {
                            filePath = item.FilePath;
                        }
                    }
                }
                // get modelname of the selected model 
                if (modelResponseData.Count > 0)
                {
                    foreach (var item in modelResponseData)
                    {
                        if (item.Id == modelId)
                        {
                            modelName = item.ModelName;
                        }
                    }
                }

                #endregion
                string zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                zsResponse = await zsClient.MultipleScoring(modelName, filePath, zmodId);
                zsResponse = zsResponse.Replace("\n", "");
                JObject jo = JObject.Parse(zsResponse.Replace("\"", "'"));
                System.IO.File.WriteAllText(newFilePath, zsResponse);
                FileInfo f = new FileInfo(newFilePath);
                long size = f.Length;
                //
                List<Property> _props = new List<Property>();
                JsonTextReader jreader = new JsonTextReader(new StringReader(zsResponse));
                int objCtr = 0;
                while (jreader.Read())
                {
                    if (jreader.TokenType == JsonToken.EndObject)
                    {
                        objCtr++;
                    }
                }
                _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });
                DataResponse _response = new DataResponse()
                {
                    Created_on = DateTime.Now.ToString(),
                    Edited_on = DateTime.Now.ToString(),
                    Extension = "json",
                    FilePath = dirFullpath + newFile,
                    Id = newFile.Replace($".json", ""),
                    MimeType = "application/json",
                    Name = newFile,
                    Properties = _props,
                    Size = size,
                    Type = "JSON",
                    Url = DirectoryHelper.GetDataUrl(newFile),
                    User = CURRENT_USER,
                    DateCreated = DateTime.Now
                };
                DataPayload.Create(_response);
                return Json(_response);

            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.StackTrace);
                return BadRequest(new { message = ex.Message, errorCode = 404, exception = ex.StackTrace });
            }
        }
        #endregion

        #region preview data
        [HttpGet("preview/{fileName}")]
        public async Task<IActionResult> GetPreviewAsync(string fileName)
        {
            string filePath = "";
            string type = "";
            string _contentType = "";

            try
            {
                foreach (var item in responseData)
                {
                    if (item.Name == fileName)
                    {
                        filePath = item.FilePath;
                        type = item.Type;
                        _contentType = item.MimeType;
                    }
                }
                //
                var memory = new MemoryStream();
                using (var stream = new FileStream(filePath, FileMode.Open))
                {
                    await stream.CopyToAsync(memory);
                }
                memory.Position = 0;
                await Task.FromResult(0);
                return File(memory, _contentType);
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.Message);
                return BadRequest(ex.Message);
            }
        }
        #endregion

        #region modify data filename
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
                //if same name exist - BadRequest
                foreach (var record in responseData)
                {
                    if (record.Id.ToLower() == newFileName.ToLower())
                    {
                        return BadRequest(new { message = "File with same name already exists." });
                    }
                }
                //
                if (!string.IsNullOrEmpty(newFileName))
                {
                    //rename the file and/or folder
                    foreach (var record in responseData)
                    {
                        if (record.Id.ToString() == id)
                        {
                            var newfilePath = record.FilePath.Replace($"{id}.{record.Extension}", $"{newFileName}.{record.Extension}");
                            FileFolderHelper.RenameFile(record.FilePath, newfilePath);
                            var newRecord = new DataResponse()
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
                                User = record.User,
                                DateCreated = record.DateCreated
                            };
                            DataPayload.Create(newRecord);
                            DataPayload.RemoveOnlyFromDataPayload(id);
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

        #region generate baseimage for welding
        #region preview data
        [HttpGet("preview/BaseImage/{fileName}")]
        public async Task<IActionResult> GetPreviewBaseImageAsync(string fileName)
        {
            string dirFullpath = $"{DirectoryHelper.GetDataDirectoryPath()}BaseImage/{fileName}";
            string _contentType = $"image/{Path.GetExtension(fileName).Remove(0, 1)}";
            try
            {
                //
                var memory = new MemoryStream();
                using (var stream = new FileStream(dirFullpath, FileMode.Open))
                {
                    await stream.CopyToAsync(memory);
                }
                memory.Position = 0;
                await Task.FromResult(0);
                return File(memory, _contentType);
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.Message);
                return BadRequest(ex.Message);
            }
        }
        #endregion

        #region [GET] /baseImage
        [HttpGet("baseImage")]
        public async Task<IActionResult> GetBaseImageAsync()
        {
            //variable
            string response = "";
            string fileName = "";
            string dirFullpath = "";
            byte[] data = null;
            JObject jObjUrl = new JObject();
            JObject jObjData = new JObject();
            //
            try
            {
                //call to baseImage
                response = await baseImageClient.GetBaseImage();
                //
                if (!string.IsNullOrEmpty(response) && (response != "Failed"))
                {
                    jObjData = JObject.Parse(response);
                    //save image in /ZMOD/data/BaseImage folder 
                    dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                    if (!string.IsNullOrEmpty(jObjData["filePath"].ToString()))
                    {
                        fileName = Path.GetFileName(jObjData["filePath"].ToString());
                        data = await _client.DownloadFile(jObjData["filePath"].ToString(), fileName);
                    }

                    string _url = DirectoryHelper.GetDataUrl($"BaseImage/{fileName}");
                    jObjUrl.Add("url", _url);
                    jObjData.Merge(jObjUrl, new JsonMergeSettings
                    {
                        // union array values together to avoid duplicates
                        MergeArrayHandling = MergeArrayHandling.Union
                    });
                }
                return Json(jObjData);
            }
            catch (Exception ex)
            {
                return BadRequest(ex.StackTrace);
            }
        }

        #endregion

        #region [POST] /baseImage
        [HttpPost("baseImage")]
        public async Task<IActionResult> PostBaseImageAsync()
        {
            //variable
            string reqBody = "";
            string response = "";
            string fileName = "";
            string dirFullpath = "";
            byte[] data = null;
            JObject jObjUrl = new JObject();
            JObject jObjData = new JObject();
            if (Request.Body != null)
            {
                try
                {
                    using (var reader = new StreamReader(Request.Body))
                    {
                        var body = reader.ReadToEnd();
                        reqBody = body.ToString();
                    }
                    response = await baseImageClient.PostBaseImage(reqBody);
                    jObjData = JObject.Parse(response);
                    //
                    dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                    if (!string.IsNullOrEmpty(jObjData["filePath"].ToString()))
                    {
                        fileName = Path.GetFileName(jObjData["filePath"].ToString());
                        data = await _client.DownloadFile(jObjData["filePath"].ToString(), fileName);
                    }

                    string _url = DirectoryHelper.GetDataUrl($"BaseImage/{fileName}");
                    jObjUrl.Add("url", _url + "?t=" + DateTime.Now);
                    jObjData.Merge(jObjUrl, new JsonMergeSettings
                    {
                        // union array values together to avoid duplicates
                        MergeArrayHandling = MergeArrayHandling.Union
                    });

                    return Json(jObjData);
                }
                catch (Exception ex)
                {
                    string err = ex.StackTrace;
                    return BadRequest(new { message = "Base image generation failed." });
                }
            }
            else
            {
                return NotFound();
            }
        }

        #endregion

        #region [POST] /generateImages 
        [HttpPost("generateImages")]
        public async Task<IActionResult> PostBaseImageGenerationAsync()
        {
            //variable
            string reqBody = "";
            string response = "";
            string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
            string imgFolderPath = "";
            string folderName = "";
            JObject jObjUrl = new JObject();
            JObject jObjData = new JObject();
            JObject jObjReq = new JObject();
            List<Property> _props = new List<Property>();
            //
            if (Request.Body != null)
            {
                try
                {
                    using (var reader = new StreamReader(Request.Body))
                    {
                        var body = reader.ReadToEnd();
                        reqBody = body.ToString();
                    }
                    //
                    jObjReq = JObject.Parse(reqBody);
                    folderName = jObjReq["folderName"].ToString();
                    imgFolderPath = $"{dirFullpath}{folderName}";
                    jObjReq.TryAdd("folderPath", imgFolderPath);
                    //create dir and delete if already exists
                    if (Directory.Exists(imgFolderPath)) Directory.Delete(imgFolderPath, true);
                    Directory.CreateDirectory(imgFolderPath);
                    //
                    response = await baseImageClient.PostGenerateBaseImage(jObjReq.ToString());
                    jObjData = JObject.Parse(response);
                    //
                    //add properties
                    _props.Add(new Property
                    {
                        key = "Subdirectories",
                        value = DirectoryHelper.CountDirectories(imgFolderPath).ToString()
                    });
                    _props.Add(new Property
                    {
                        key = "Files",
                        value = DirectoryHelper.CountFiles(imgFolderPath).ToString()
                    });
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = DateTime.Now.ToString(),
                        Edited_on = DateTime.Now.ToString(),
                        Extension = "",
                        Type = "FOLDER",
                        FilePath = imgFolderPath,
                        Id = folderName,
                        MimeType = "",
                        Name = folderName,
                        Properties = _props,
                        DateCreated = DateTime.Now
                    };
                    //
                    DataPayload.Create(newRecord);
                    return Json(jObjReq);
                }
                catch (Exception ex)
                {
                    string err = ex.StackTrace;
                    return BadRequest(new { message = "Base image generation failed." });
                }
            }
            else
            {
                return NotFound();
            }
        }

        #endregion

        #endregion

        #region automl - anamoly
        [HttpPost]
        [Route("{id}/anamoly")]
        public async Task<IActionResult> AutoMLAnamoly(string id)
        {
            string response = string.Empty;
            string reqBody = string.Empty;
            if (Request.Body != null)
            {
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEnd();
                    reqBody = body.ToString();
                }
                try
                {
                    response = await _client.AnamolyModel(reqBody);
                }
                catch (Exception ex)
                {
                    //TO DO: ILogger
                    string _ex = ex.Message;
                }

                if (!string.IsNullOrEmpty(response))
                {
                    var jo = JsonConvert.DeserializeObject<AutoMLResponse>(response);
                    jo.executedAt = DateTime.Now;
                    List<AutoMLResponse> tresp = new List<AutoMLResponse>();
                    tresp.Add(jo);
                    //
                    //add to scheduler payload 
                    //add history
                    JArray jHist = new JArray();
                    foreach (var r in tresp)
                    {
                        jHist.Add(new JObject(){
                        {"idforData", r.idforData},
                        {"status", r.status},
                        {"executedAt",r.executedAt}
                    });
                    }
                    SchedulerResponse schJob = new SchedulerResponse()
                    {
                        CreatedOn = DateTime.Now.ToString(),
                        CronExpression = "",
                        DateCreated = DateTime.Now,
                        EditedOn = DateTime.Now.ToString(),
                        FilePath = "",
                        Id = id,
                        Name = id,
                        Type = "ANAMOLY",
                        Url = "",
                        Recurrence = "ONE_TIME",
                        StartDate = "",
                        StartTimeH = "",
                        StartTimeM = "",
                        ZMKResponse = tresp.ToList<object>(),
                        Status = "COMPLETED",
                        History = jHist.ToList<object>()
                    };
                    SchedulerPayload.Create(schJob);

                    //
                    JObject jsonObj = JObject.Parse(response);
                    return Json(jsonObj);
                }
                else
                {
                    return NoContent();
                }
            }
            else
            {
                return NoContent();
            }
        }
        #endregion
    }
}