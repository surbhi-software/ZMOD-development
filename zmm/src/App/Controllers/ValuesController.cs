using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using ZMM.App.PyServicesClient;
using ZMM.Helpers.ZMMDirectory;
using ZMM.Models.Payloads;
using ZMM.Tasks;
using ZMM.Tools.JNB;

namespace ZMM.App.Controllers
{
    [Route("[controller]/[action]")]
    public class ValuesController : Controller
    {

        private readonly IPyJupyterServiceClient jupyterClient;
        readonly ILogger<ValuesController> Logger;

        private readonly IConfiguration configuration;

        public ValuesController(IConfiguration configuration, ILogger<ValuesController> log, IPyJupyterServiceClient _jupyterClient)
        {
            this.jupyterClient = _jupyterClient;
            this.Logger = log;
            this.configuration = configuration;
        }
        IConfiguration Configuration { get; }

        [HttpGet]
        public IActionResult Get()
        {
            return Json(SchedulerPayload.Get());
        }

        // POST api/values
        [HttpPost]
        public IActionResult Post([FromBody]string value)
        {
            if (!String.IsNullOrEmpty(value))
                return Json(value);
            else
               return new EmptyResult();
        }

        // PUT api/values/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody]string value)
        {
        }

        // DELETE api/values/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {
        }

        //Job scheduler
        [HttpPost("myjob")]
        public IActionResult ScheduleJob()
        {
            string reqBody = "";
            using (var reader = new StreamReader(Request.Body))
            {
                var body = reader.ReadToEnd();
                reqBody = body.ToString();
            }
            return Ok(new { status = "Job Added to scheduler.", bodydata = reqBody });
        }

    }
}

