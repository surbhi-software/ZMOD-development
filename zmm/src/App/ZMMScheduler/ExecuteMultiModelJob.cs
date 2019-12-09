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

public class ExecuteMultiModelJob : IJob
{
    public Task Execute(IJobExecutionContext context)
    {
        JobDataMap dataMap = context.JobDetail.JobDataMap;
        Console.WriteLine($"Model training started: {dataMap.GetString("filePath")} - {dataMap.GetString("id")} is now running at {DateTime.Now.ToString()} and a random number is : {new Random().Next(0, 99999)}");
        string filePath = dataMap.GetString("filePath");
        string baseAddress = $"{dataMap.GetString("baseurl")}newtrainmodels/{dataMap.GetString("id")}";
        //
        try
        {
            WebRequest reqObj = WebRequest.Create(baseAddress);
            reqObj.Method = "Get";
            reqObj.ContentType = "application/json";
            var response = (HttpWebResponse)reqObj.GetResponse();

            using (StreamReader rdr = new StreamReader(response.GetResponseStream()))
            {
                string resp = rdr.ReadToEnd();
                var jresp = JObject.Parse(resp);
                jresp.Add("executedAt", DateTime.Now);
                JobSchedulerHelper.AddZMKResponses(dataMap.GetString("id"), jresp.ToString(), "Train");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.StackTrace);
        }
        return Task.FromResult(0);
    }
}