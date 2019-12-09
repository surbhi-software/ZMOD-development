using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;

namespace ZMM.App.PyServicesClient
{
    public class BaseImageForWielding : IBaseImageForWielding
    {
        public IConfiguration Configuration { get; }

        #region constructor
        public BaseImageForWielding(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }
        #endregion

        #region Get baseImage from ZMK
        public async Task<string> GetBaseImage()
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
                    HttpResponseMessage response = await httpClient.GetAsync($"data/baseImage");                   
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                    else
                    {
                        //do nothing
                        jsonResult = "Failed";
                    }
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.StackTrace + "'";
                }            
            }

            return jsonResult;
        }
        #endregion

        #region Post baseImage to ZMK
        public async Task<string> PostBaseImage(string configInfo)
        {
            string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
               
                HttpContent _httpContent = new StringContent(configInfo); 
                
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync($"data/baseImage",_httpContent);

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                    else
                    {
                        //do nothing
                        jsonResult = "Failed";
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
    
        #region Post generate baseImage to ZMK
        public async Task<string> PostGenerateBaseImage(string configInfo)
        {
           string jsonResult = string.Empty;

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
               
                HttpContent _httpContent = new StringContent(configInfo); 
                
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync($"data/generateImage",_httpContent);

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                    else
                    {
                        //do nothing
                        jsonResult = "Failed";
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