using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Configuration;
using ZMM.Helpers.Common;

namespace ZMM.App.PyServicesClient
{
    public class PyZMEServiceClient : IPyZMEServiceClient
    {   
        public IConfiguration Configuration { get; }
        public PyZMEServiceClient(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }     
       
        #region zmk/api/v1/listOfLayers
        public async Task<string> GetListOfLayers()
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
                        
                    }
                );   
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync("listOfLayers");

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': 'ZME Server Error."+ ex.Message + "baseurl:" + Configuration["PyServiceLocation:srvurl"] +"'}";
                }            
            }

            return jsonResult;
        }
        #endregion

        #region api/v1/updateLayer...
        public async Task<string> AddUpdateLayers(string id, string body)
        {
            string jsonResult = string.Empty;            

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
               
                string reqbody = "{\"projectID\": \""+ id +"\", \"layerToUpdate\":" + body +"}";
                
                HttpContent _httpContent = new StringContent(reqbody);
                string _contentType = "application/json";
                 _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType);                 
                

                try
                {
                    HttpResponseMessage response = await httpClient.PutAsync($"pmml/{id}/layer", _httpContent);

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': 'ZME Server Error.'" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion

        #region api/v1/deleteLayer
        public async Task<string> DeleteLayers(string id, string body)
        {
            
            string jsonResult = string.Empty;            

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
               
                string reqbody = "{\"projectID\": \""+ id +"\", \"layerDelete\":" + body +"}";
                
                HttpContent _httpContent = new StringContent(reqbody);
                string _contentType = "application/json";
                 _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType);

                 var req=new HttpRequestMessage(HttpMethod.Delete,$"pmml/{id}/layer");
                 req.Content=_httpContent;                 
                

                try
                {
                    //HttpResponseMessage response = await httpClient.PostAsync("deleteLayer", _httpContent);
                    HttpResponseMessage response = await httpClient.SendAsync(req); 

                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': 'ZME Server Error.'" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion
    
        #region api/v1/pmml/zmk/convert
        public async Task<string> PostConvertPmmlAsync(string oldFilePath, string newFilePath)
        {  
            string jsonResult = string.Empty;
            //
            using (var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));             
                //request params
                var content = new FormUrlEncodedContent(
                    new List<KeyValuePair<string, string>>
                    {
                        new KeyValuePair<string, string>("oldFilePath", oldFilePath),
                        new KeyValuePair<string, string>("newFilePath", newFilePath)
                    }
                );
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync("pmml/zmk/convert", content);

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
    }
}