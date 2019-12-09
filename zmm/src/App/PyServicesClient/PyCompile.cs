
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;

namespace ZMM.App.PyServicesClient
{

    public class PyCompile : IPyCompile
    {
        #region variables
        public IConfiguration Configuration { get; }
        #endregion

        #region constructor
        public PyCompile(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }
        #endregion

        #region interface implementation
        public async Task<string> CompilePy(string filePath)
        {
            string jsonResult = string.Empty;
            using (var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
                //
                try
                {
                    HttpResponseMessage response = await httpClient.GetAsync($"code?filePath={filePath}");
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    }
                    else
                    {
                        //do nothing
                    }
                }
                catch (HttpRequestException ex)
                {
                    jsonResult = "{'message': '" + ex.StackTrace + "'";
                }
            }

            return jsonResult;
        }

        public async Task<string> ExecutePy(string filePath, string _params)
        {
            string jsonResult = string.Empty;            

            using(var httpClient = new HttpClient())
            {
                httpClient.BaseAddress = new System.Uri(Configuration["PyServiceLocation:srvurl"]);
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));                              
                //
                JObject json = new JObject(new JProperty("filePath", filePath), new JProperty("params", _params)); 
                //          
                HttpContent _httpContent = new StringContent(json.ToString());
                string _contentType = "application/json";
                 _httpContent.Headers.ContentType = new MediaTypeHeaderValue(_contentType);                 
                //
                try
                {
                    HttpResponseMessage response = await httpClient.PostAsync($"code", _httpContent);
                    if (response.IsSuccessStatusCode)
                    {
                        jsonResult = await response.Content.ReadAsStringAsync();
                    } 
                }
                catch(HttpRequestException ex)
                {
                    jsonResult = "{'message': 'ZMK Server Error.'" + ex.Message + "'}";
                }            
            }

            return jsonResult;
        }
        #endregion
    }
}