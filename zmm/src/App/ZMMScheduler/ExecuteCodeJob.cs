using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using Quartz;
using ZMM.App.PyServicesClient;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public class ExecuteCodeJob : IJob
{
    public Task Execute(IJobExecutionContext context)
    {
        JobDataMap dataMap = context.JobDetail.JobDataMap;
        Console.WriteLine($"Execute Code for {dataMap.GetString("filePath")} - {dataMap.GetString("id")} is now running at {DateTime.Now.ToString()} and a random number is : {new Random().Next(0, 99999)}");
        string filePath = dataMap.GetString("filePath");        
        string baseAddress = $"{dataMap.GetString("baseurl")}code";
        //
        try
        {
            WebRequest reqObj = WebRequest.Create(baseAddress);
            reqObj.Method = "POST";
            reqObj.ContentType = "application/json";
            filePath =  filePath.Replace("\\","\\\\");
            string requestBody = "{\"filePath\":\"" + filePath + "\",\"params\":\"" + string.Empty + "\"}";
            byte[] byteArray = Encoding.UTF8.GetBytes(requestBody);
            using (StreamWriter writer = new StreamWriter(reqObj.GetRequestStream()))
            {
                writer.Write(requestBody); 
                writer.Flush();
                writer.Close();               
                var response = (HttpWebResponse) reqObj.GetResponse();

                //using(StreamReader rdr = new StreamReader(response.GetResponseStream(),Encoding.Default))
                //{
                    string resp = JsonConvert.SerializeObject(response.GetResponseStream(), Formatting.None);
                   // string resp = rdr.ReadToEnd();

                    var jresp = JObject.Parse(resp);
                    jresp.Add("executedAt", DateTime.Now);
                    JobSchedulerHelper.AddZMKResponses(dataMap.GetString("id"),jresp.ToString(),"ExecuteCode");
               /// }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.StackTrace);
        }
        return Task.FromResult(0);
    }
}