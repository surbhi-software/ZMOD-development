using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;
using ZMM.Helpers.Common;
using ZMM.Models.Payloads;

namespace ZMM.App.ZSServiceClient
{
    public class ZSModelPredictionClient : IZSModelPredictionClient
    {
        public IConfiguration configuration { get; }
        public ZSModelPredictionClient(IConfiguration _configuration)
        {
            this.configuration = _configuration;
        }

        #region GetModels - [GET] http://dcindgo01:8083/adapars/models
        public async Task<string> GetModels(string zmodId)
        {
            string jsonResult = string.Empty;            
            var tuple = ZSSettingPayload.GetUserInfo(zmodId);
            var auth = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(Encoding.UTF8.GetBytes($"{tuple.Item2}:{tuple.Item3}")));

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(tuple.Item1);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                httpClient.DefaultRequestHeaders.Authorization = auth; 
               
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync("service/zementis/models");
                    
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                    else
                        return ZMMConstants.ErrorFailed;
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.Message + "', 'error':'"+ ZMMConstants.ErrorFailed +"'}";
                }            
            }

            return jsonResult;
        }
        #endregion
    
        #region Delete Pmml [DELETE] http://dcindgo01:8083/adapars/models/{modelName}
        public async Task<string> DeletePmml(string modelName, string zmodId)
        {
            string jsonResult = string.Empty;
            var tuple = ZSSettingPayload.GetUserInfo(zmodId);
            var auth = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(Encoding.UTF8.GetBytes($"{tuple.Item2}:{tuple.Item3}")));

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(tuple.Item1);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                httpClient.DefaultRequestHeaders.Authorization = auth;    
                //
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        //nothing
                    }
                );  
                //
                try
                {
                    HttpResponseMessage response = await httpClient.DeleteAsync("service/zementis/model/" + modelName);
                    
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

        #region Upload Pmml [POST]
        public async Task<string> UploadPmml(string filePath,string zmodId)
        {
            string jsonResult = string.Empty;
            var tuple = ZSSettingPayload.GetUserInfo(zmodId);
            var auth = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(Encoding.UTF8.GetBytes($"{tuple.Item2}:{tuple.Item3}")));
            try
            {
                using (var httpClient = new HttpClient())
                {
                    httpClient.BaseAddress = new System.Uri(tuple.Item1);
                    httpClient.DefaultRequestHeaders.Accept.Clear();
                    httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                    httpClient.DefaultRequestHeaders.Authorization = auth;
                    httpClient.Timeout=TimeSpan.FromMinutes(30);

                    using (var content = new MultipartFormDataContent("Upload--" + DateTime.Now.ToString(CultureInfo.InvariantCulture)))
                    {
                        var memory = new MemoryStream();
                        using (var stream = new FileStream(filePath, FileMode.Open))
                        {
                            await stream.CopyToAsync(memory);
                        }
                        memory.Position = 0;
                        content.Add(new StreamContent(memory), "file", filePath);
                        HttpResponseMessage response = await httpClient.PostAsync("service/zementis/model", content);
                        if (response.IsSuccessStatusCode)
                        {
                            jsonResult = await response.Content.ReadAsStringAsync();
                        }
                        else if(response.StatusCode.ToString() == "402")
                        {
                            return "FileExists";
                        }
                        else
                        {
                            return "Fail";
                        }

                    }
                }
            }
            catch(Exception ex)
            {
                string _ex=ex.Message;
                return "fail";
            }
            

            return jsonResult;
        }
        #endregion
    
        #region single scoring [GET] /apply/SVM_Model?record={}
        //http://dcindgo01:8083/adapars/apply/SVM_Model?record={"sepal length (cm)":5,"sepal width (cm)":3,"petal length (cm)":1,"petal width (cm)":0}
        public async Task<string> SingleScoring(string modelName, string record, string zmodId)
        {
            string jsonResult = string.Empty;
            var tuple = ZSSettingPayload.GetUserInfo(zmodId);
            var auth = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(Encoding.UTF8.GetBytes($"{tuple.Item2}:{tuple.Item3}")));

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(tuple.Item1);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                httpClient.DefaultRequestHeaders.Authorization = auth;    
                //                                
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"service/zementis/apply/{modelName}?record={record}");
                    
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();                        
                    } 
                }
                catch(HttpRequestException ex)
                {
                    //add log                    
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion

        #region multiple score
        public async Task<string> MultipleScoring(string modelName, string filePath, string zmodId)
        {
            string jsonResult = string.Empty;
            var tuple = ZSSettingPayload.GetUserInfo(zmodId);
            var auth = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(Encoding.UTF8.GetBytes($"{tuple.Item2}:{tuple.Item3}")));

            using (var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(tuple.Item1);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                httpClient.DefaultRequestHeaders.Authorization = auth;
                //                                
                try
                {
                    using (var content = new MultipartFormDataContent())
                    {
                        var memory = new MemoryStream();
                        using (var stream = new FileStream(filePath, FileMode.Open))
                        {
                            await stream.CopyToAsync(memory);
                        }
                        memory.Position = 0;
                        content.Add(new StreamContent(memory), "file", filePath);
                        HttpResponseMessage response = await httpClient.PostAsync($"service/zementis/apply/{modelName}", content);
                        if (response.IsSuccessStatusCode)
                        {
                            jsonResult = await response.Content.ReadAsStringAsync();
                        }
                    }

                }
                catch (HttpRequestException ex)
                {
                    //add log                    
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }
            }

            return jsonResult;
        }
        #endregion

        #region Image score
        public async Task<string> ImageScoring(string modelName,string filePath, string zmodId)
        {
            string jsonResult = string.Empty;
            var tuple = ZSSettingPayload.GetUserInfo(zmodId);
            var auth = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(Encoding.UTF8.GetBytes($"{tuple.Item2}:{tuple.Item3}")));

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(tuple.Item1);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                httpClient.DefaultRequestHeaders.Authorization = auth;
                // httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("eddie.soong@softwareag.com", "softwareag");   
                //                                
                try
                {
                    using (var content = new MultipartFormDataContent())
                    {
                        var memory = new MemoryStream();
                        using (var stream = new FileStream(filePath, FileMode.Open))
                        {
                            await stream.CopyToAsync(memory);
                        }
                        memory.Position = 0;
                        content.Add(new StreamContent(memory), "file", filePath);
                        HttpResponseMessage response = await httpClient.PostAsync($"service/zementis/apply/{modelName}", content);
                        if (response.IsSuccessStatusCode)
                        {
                            jsonResult = await response.Content.ReadAsStringAsync();
                        }
                    }

                }
                catch(HttpRequestException ex)
                {
                    //add log                    
                    jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }
            return jsonResult;
        }
        #endregion
    }
}