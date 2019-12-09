using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Payloads;
using Newtonsoft.Json;
using System.Text;

namespace ZMM.App.Controllers
{
    [Authorize]
    [Route("[controller]/[action]")]
    public class SettingController : Controller
    {
        #region Variables... 
        private readonly IWebHostEnvironment _environment;
        readonly ILogger<CodeController> Logger;
        public IConfiguration Configuration { get; }
        private List<ZSSettingResponse> settingsResponse;

        public static string ZmodId;

        #endregion

        #region Constructor...
        public SettingController(IWebHostEnvironment environment, IConfiguration configuration, ILogger<CodeController> log)
        {
            //update 
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));
            this.Configuration = configuration;
            this.Logger = log;
        }
        #endregion

        #region Add settings
        [HttpPost("~/api/setting")]
        public async Task<IActionResult> AddSettingAsync()
        {
            string jsonBody = "", zmodId = "";
            //read from body
            if (Request.Body != null)
            {
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = await reader.ReadToEndAsync();
                    jsonBody = body.ToString();
                }
                zmodId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
                //parse
                JObject jObj = JObject.Parse(jsonBody);
                JArray jArr = (JArray)jObj["settings"];
                var setList = jArr.ToObject<List<SettingProperty>>();
                //add to payload
                var newRecord = new ZSSettingResponse()
                {
                    ZmodId = zmodId,
                    Settings = setList
                };
                ZSSettingPayload.CreateOrUpdate(newRecord);
                return Json(JObject.Parse(jsonBody));
            }
            else
                return new EmptyResult();
        }
        #endregion

        #region GET Settings
        [HttpGet("~/api/setting")]
        public async Task<IActionResult> GetSettingsAsync(string type)
        {
            //get the zmodId
            string UserEmailId = ZSSettingPayload.GetUserNameOrEmail(HttpContext);
            JObject jObj = new JObject();
            await Task.FromResult(0);
            var settings = ZSSettingPayload.GetSettingsByUser(UserEmailId);
            List<SettingProperty> settingProperties;
            if (string.IsNullOrEmpty(type))
            {
                settingProperties = settings.SelectMany(b => b.Settings).ToList<SettingProperty>();
            }
            else
            {
                settingProperties = settings.SelectMany(b => b.Settings).ToList<SettingProperty>();
                settingProperties = settingProperties.Where(c => c.type == $"{type}").ToList<SettingProperty>();
            }
            // var selectedType = settingProperties.Where(c=>c.type == $"{type}").ToList<SettingProperty>();
            //
            if (settings.Count == 0)
            {
                var template = new ZSSettingResponse
                {
                    ZmodId = UserEmailId,
                    Settings = new List<SettingProperty> {
                        new SettingProperty{ name="Cumulocity",type="C8Y",tenantID="ai", username="vran",password="Testing@123",url="https://ai.eu-latest.cumulocity.com",selected=true },
                        new SettingProperty{ name="Cumulocity",type="C8Y",tenantID="ai", username="vran",password="Testing@123",url="https://ai.cumulocity.com",selected=false },
                        new SettingProperty{ name="Zementis Server",type="ZS",tenantID="zserver", username="vran",password="Testing@123",url="https://ai.eu-latest.cumulocity.com/",selected=true },
                        new SettingProperty{ name="Zementis Server",type="ZS",tenantID="zserver", username="",password="",url="https://zserver.zmod.org/adapars/",selected=false },
                        new SettingProperty{ name="Nyoka Remote 1",type="NR",tenantID="dlexp", username="",password="",url="https://dlexp.zmod.org/",selected=false },
                        new SettingProperty{ name="Nyoka Remote 2",type="NR",tenantID="dlexp", username="",password="",url="https://hub.zmod.org/",selected=true }
                    }
                };
                jObj = JObject.Parse(JsonConvert.SerializeObject(template));
                ZSSettingPayload.CreateOrUpdate(template);
            }
            else
            {
                var template = new ZSSettingResponse
                {
                    ZmodId = UserEmailId,
                    Settings = settingProperties
                };

                jObj = JObject.Parse(JsonConvert.SerializeObject(template));
            }
            jObj.Remove("zmodId");
            return Json(jObj);
        }
        #endregion

    }
}