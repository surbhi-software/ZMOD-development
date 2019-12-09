using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using System;
using ZMM.Helpers.Common;

namespace ZMM.App.PyServicesClient
{
    public class PyNNServiceClient : IPyNNServiceClient
    {
        public IConfiguration Configuration { get; }
        public PyNNServiceClient(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }
        #region getAllModelList
        /// <summary>
        /// <description>get list of model already loaded in Zementis GET</description>
        /// <requesturl>/api/v1/getListofModels</requesturl>
        /// </summary>
        public async Task<string> GetAllModelList()
        {
            string jsonResult = string.Empty;
            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync("models");
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    }
                    else
                    {
                        jsonResult = "{'message': 'Conversion failed', 'error':'"+ ZMMConstants.ErrorFailed +"'}";
                    }
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "', 'error':'"+ ZMMConstants.ErrorFailed +"'}";
                }
                //
                               
            }

            return jsonResult;
        }
        #endregion

        #region predict image - predicttestdata
        public async Task<string> GetPredictionForImage(string modelname, string filePath)
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        // new KeyValuePair<string, string>("modelName", modelname),
                        new KeyValuePair<string, string>("filePath", filePath)
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync($"models/{modelname}/score",content);

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion

        #region load model...
        public async Task<string> PostLoadModel(string filePath)
        {
            string jsonResult = string.Empty;
            using (var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        new KeyValuePair<string, string>("filePath", filePath)
                    }
                );
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync("models", content);

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    }
                    else
                    {
                        jsonResult = "{'message': 'Conversion failed', 'error':'"+ ZMMConstants.ErrorFailed +"'}";
                    }
                }
                catch (HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "', 'error':'"+ ZMMConstants.ErrorFailed +"'}";
                }
            }

            return jsonResult;
        }
        #endregion

        #region unload model- /api/v1/unloadModel
        public async Task<string> PostUnloadModel(string modelName)
        {
            string jsonResult = string.Empty;

            using (var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        new KeyValuePair<string, string>("modelname", modelName)
                    }
                );

                try
                {
                    HttpResponseMessage response = await httpClient.DeleteAsync($"models/{modelName}");

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    }
                    else
                    {
                        jsonResult = "fail";
                    }
                }
                catch (HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }
            }

            return jsonResult;
        }
        #endregion

        #region delete model
        public Task<string> DeleteLoadedModel(string param)
        {
            throw new System.NotImplementedException();
        }

        #endregion

        #region Train model...
        public async Task<string> TrainModel(string requestBody)
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                //
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));               
                HttpContent _httpContent = new StringContent(requestBody);
                // HttpContent _httpContent = new StringContent("");
                string _contentType = "application/json";
                 _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType);                
                //
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync($"trainNNModel", _httpContent);
                    // HttpResponseMessage response = await httpClient.GetAsync($"trainNNModel/{requestBody}");
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'";
                }
                //
                               
            }

            return jsonResult;
        }
        #endregion

        #region Get running tasks...

        #region Get All tasks
        public async Task<string> GetAllRunningTask()
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        //empty
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync("runningTasks");
                    Console.WriteLine(httpClient.BaseAddress);
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion
        
        #region get running tasks by id
        public async Task<string> GetRunningTaskByTaskName(string taskName)
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        //empty
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"runningTasks/{taskName}");
                    Console.WriteLine(httpClient.BaseAddress);
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion
        
        #region get running task details by id
        public async Task<string> GetRunningTaskByTaskNameAndId(string taskName, string idforData)
        {            
            string jsonResult = string.Empty;
            using(var httpClient = new HttpClient())
            {                
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        //empty
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"runningTasks/{taskName}/{idforData}");
                    Console.WriteLine(httpClient.BaseAddress);
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult;

        }

        #endregion 
        #endregion
    
        #region Edit NN pmml file...
        public async Task<string> PostEditPmml(string projectId, string filePath)
        {
            string jsonResult = string.Empty;
            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        // new KeyValuePair<string, string>("projectID", projectId),
                        new KeyValuePair<string, string>("filePath", filePath)
                    }
                );        

                //
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync($"pmml/{projectId}", content);
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'";
                }
                //
                               
            }

            return jsonResult;
        }


        #endregion
    
        #region Get Pmml file properties...
        public async Task<string> GetPmmlProperties(string filePath)
        {
            string jsonResult = string.Empty;
            
            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                //request params
                // string body = "{\"filePath\": \""+ filePath +"\"}";               
                // HttpContent _httpContent = new StringContent(body);
                // string _contentType = "application/json";
                //  _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType); 
                
                
                /*var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {                      
                        new KeyValuePair<string, string>("filePath", filePath)
                    }
                );*/
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"pmml?filePath={filePath}");
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    }
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult; 
        }
        #endregion
    
        #region Delete running task
        public async Task<string> DeleteRunningTask(string id)
        {
            string jsonResult = string.Empty;
            using(var httpClient = new HttpClient())
            {                
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();                
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                       new KeyValuePair<string, string>("idforData", id)
                    }
                );
                
                try
                {
                    // HttpResponseMessage response = await httpClient.DeleteAsync($"deleteTaskfromMemory?idforData={ id }");     
                    HttpResponseMessage response = await httpClient.DeleteAsync($"runningTasks/{id}");               
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    //TODO: ILogger
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion
    }
}