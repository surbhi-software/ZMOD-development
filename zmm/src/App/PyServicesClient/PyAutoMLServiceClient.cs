using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using ZMM.Helpers.ZMMDirectory;

namespace ZMM.App.PyServicesClient
{
    public class PyAutoMLServiceClient : IPyAutoMLServiceClient
    {
        public IConfiguration Configuration { get; }

        public PyAutoMLServiceClient(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }
     
        string _contentType = "application/json";
        public async Task<string> GetPreprocessingForm(string filePath)
        {
            string jsonResult = string.Empty;            
            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                // //
                // //request params
                // var content = new FormUrlEncodedContent(
                //     new List<KeyValuePair<string, string>>
                //     {
                //         new KeyValuePair<string, string>("filePath", filePath)
                //     }
                // );   
                try
                {
                    
                    HttpResponseMessage response = await httpClient.GetAsync($"trainAutoMLModel?filePath={filePath}");                   
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                    else
                    {
                        //jsonResult = "{'error_badrequest':'server error.'}";
                    }
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.StackTrace + "'";
                }            
            }

            return jsonResult;
        }

        public async Task<string> PostProcessingForm(string data)
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                /*
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        new KeyValuePair<string, string>("json", data)
                    }
                );   */

                HttpContent _httpContent = new StringContent(data);
                 _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType); 
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync("trainAutoMLModel",_httpContent);

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

        public async Task<string> GetSelectedTask(string idForData)  
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
                        new KeyValuePair<string, string>("idforData", idForData)
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"runningTasks/{idForData}");

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

        public async Task<string> SaveBestPmml(string filePath) 
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
                        new KeyValuePair<string, string>("filePath", filePath)
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"downloadFile?filePath={filePath}");

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
    
        public async Task<Byte[]> DownloadFile(string filePath, string fileName) 
        {  
            byte[] result = null; 
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
                        new KeyValuePair<string, string>("filePath", filePath)
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"downloadFile?filePath={filePath}");

                    if (response.IsSuccessStatusCode)
                    {   
                        Byte[] byteArray = await response.Content.ReadAsByteArrayAsync(); 
                        string dirFullpath = DirectoryHelper.GetDataDirectoryPath();
                        if(fileName.Contains("png")) 
                        {
                            Image img = ByteArrayToImage(byteArray);                            
                            string newFilePath = $"{dirFullpath}BaseImage";
                            if (!Directory.Exists(newFilePath))
                            {
                                Directory.CreateDirectory(newFilePath);
                            }
                            if(System.IO.File.Exists($"{newFilePath}/{fileName}"))
                            {
                                System.IO.File.Delete($"{newFilePath}/{fileName}");
                            }

                            img.Save($"{newFilePath}/{fileName}");
                        }     
                        else if(fileName.Contains("mp4"))
                        {
                            File.WriteAllBytes($"{dirFullpath}{fileName}",byteArray);
                            result = byteArray;
                        }        
                        
                    } 
                }
                catch(HttpRequestException ex)
                {
                    string jsonResult = "{'message': '" + ex.Message + "'}";
                }            
            }
            return result;
        }
    
         //convert bytearray to image
        public Image ByteArrayToImage(byte[] byteArrayIn)
        {
            using (MemoryStream mStream = new MemoryStream(byteArrayIn))
            {               
                return Image.FromStream(mStream);
            }
            
        }

        #region automl - anamoly
        public async Task<string> AnamolyModel(string data)
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                /*
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        new KeyValuePair<string, string>("json", data)
                    }
                );   */

                HttpContent _httpContent = new StringContent(data);
                 _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType); 
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync("trainAnomalyModel",_httpContent);

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
    }
}