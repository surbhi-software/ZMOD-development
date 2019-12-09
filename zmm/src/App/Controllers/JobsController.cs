using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ZMM.App.PyServicesClient;
using Microsoft.Extensions.Logging;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Payloads;
using ZMM.Helpers.ZMMDirectory;
using ZMM.Helpers.Common;
using ZMM.Tools.JNB;
using ZMM.Tasks;
using System.Text.RegularExpressions;
using Quartz;
using Quartz.Impl;
using Quartz.Impl.Matchers;
using Task = System.Threading.Tasks.Task;

namespace ZMM.App.Controllers
{
    // [Authorize]
    [Route("api/[controller]")]
    public class JobsController : Controller
    {
        #region Variables... 
        private readonly IWebHostEnvironment _environment;
        readonly ILogger<CodeController> Logger;
        public IConfiguration Configuration { get; }
        private List<SchedulerResponse> jobsResponse;
        private readonly IScheduler _scheduler;

        #endregion

        #region Constructor...
        public JobsController(IWebHostEnvironment environment, IConfiguration configuration, ILogger<CodeController> log, IScheduler factory)
        {
            //update 
            _environment = environment ?? throw new ArgumentNullException(nameof(environment));
            this.Configuration = configuration;
            this.Logger = log;
            _scheduler = factory;
            try
            {
                InitZmodDirectory.ScanModelsDirectory();
                jobsResponse = SchedulerPayload.Get();
            }
            catch (Exception ex)
            {
                Logger.LogCritical(ex, ex.StackTrace);
            }
        }
        #endregion

        #region GET

        #region get scheduled jobs
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            List<object> jobs = new List<object>();
            ISchedulerFactory schfack = new StdSchedulerFactory();
            IScheduler scheduler = await schfack.GetScheduler();
            var jobGroups = await scheduler.GetJobGroupNames();

            foreach (string group in jobGroups)
            {
                var groupMatcher = GroupMatcher<JobKey>.GroupContains(group);
                var jobKeys = await scheduler.GetJobKeys(groupMatcher);
                foreach (var jobKey in jobKeys)
                {
                    var detail = await scheduler.GetJobDetail(jobKey);
                    var triggers = await scheduler.GetTriggersOfJob(jobKey);
                    foreach (ITrigger trigger in triggers)
                    {
                        var sj = new
                        {
                            id = Path.GetFileNameWithoutExtension(jobKey.Name),
                            group = group,
                            jobKeyName = jobKey.Name,
                            description = detail.Description,
                            triggerKeyName = trigger.Key.Name,
                            triggerKeyGroup = trigger.Key.Group,
                            triggerTypeName = trigger.GetType().Name,
                            triggerState = await scheduler.GetTriggerState(trigger.Key),
                            previousFireTime = trigger.GetPreviousFireTimeUtc(),
                            nextFireTime = trigger.GetNextFireTimeUtc()
                        };
                        jobs.Add(sj);
                    }
                }
            }
            return Json(jobs);
        }
        #endregion

        #region  get job by id
        [HttpGet("{id}")]
        public IActionResult Get(string id)
        {
            return Json(SchedulerPayload.Get().Where(s => s.Id == id).First());
        }
        #endregion

        #region get running jobs
        [HttpGet("running")]
        public IActionResult GetRunningJobs(string id)
        {
            if (!string.IsNullOrEmpty(id))
            {
                return Json(SchedulerPayload.Get().Where(j => j.Id == id));
            }
            else
            {
                return Json(SchedulerPayload.Get());
            }

        }
        #endregion

        #endregion

        #region CREATE

        #region create job for training model
        [HttpPost("{id}/train")]
        public async Task<IActionResult> CreateTrainingJobAsync(string id, [FromBody]TrainingRequestParam jsonbody)
        {
            string filePath = "";
            var json = JsonConvert.SerializeObject(jsonbody);
            JObject jo = JObject.Parse(json);

            /* TODO: validation for req body */
            JObject cronjson = JObject.Parse(jo.ToString());
            filePath = cronjson["filePath"].ToString();

            /*request json for zmk */
            JObject req = JObject.Parse(jo.ToString());
            req.Remove("recurrence");
            req.Remove("cronExpression");
            req.Remove("startDate");
            req.Remove("startTimeH");
            req.Remove("startTimeM");

            /* validate if model exists in the ZMOD directory and loaded. */
            if (ModelPayload.Get().Where(m => m.Id == id).Count() == 1)
            {

                List<TrainingResponse> tresp = new List<TrainingResponse>();

                #region schedule training

                /* check if same job is scheduled */
                ISchedulerFactory schfack = new StdSchedulerFactory();
                IScheduler scheduler = await schfack.GetScheduler();
                var jobKey = new JobKey(filePath);
                if (await scheduler.CheckExists(jobKey))
                {
                    await scheduler.ResumeJob(jobKey);
                }
                else
                {
                    try
                    {
                        #region create quartz job for training model
                        ITrigger trigger = TriggerBuilder.Create()
                        .WithIdentity($"Training Model Job-{DateTime.Now}")
                        .WithCronSchedule(cronjson["cronExpression"].ToString())
                        .WithPriority(1)
                        .Build();

                        IJobDetail job = JobBuilder.Create<TrainModelJob>()
                        .WithIdentity(filePath)
                        .Build();

                        job.JobDataMap["id"] = id;
                        job.JobDataMap["filePath"] = filePath;
                        job.JobDataMap["reqBody"] = req.ToString();
                        job.JobDataMap["baseurl"] = Configuration["PyServiceLocation:srvurl"];

                        await _scheduler.ScheduleJob(job, trigger);
                        //add to scheduler payload                            
                        SchedulerResponse schJob = new SchedulerResponse()
                        {
                            CreatedOn = DateTime.Now.ToString(),
                            CronExpression = cronjson["cronExpression"].ToString(),
                            DateCreated = DateTime.Now,
                            EditedOn = DateTime.Now.ToString(),
                            FilePath = filePath,
                            Id = id,
                            Name = id,
                            Type = "NN",
                            Url = "",
                            Recurrence = cronjson["recurrence"].ToString(),
                            StartDate = cronjson["startDate"].ToString(),
                            StartTimeH = (cronjson["startTimeH"].ToString() == null) ? "" : cronjson["startTimeH"].ToString(),
                            StartTimeM = (cronjson["startTimeM"].ToString() == null) ? "" : cronjson["startTimeM"].ToString(),
                            ZMKResponse = tresp.ToList<object>(),
                            Status = "Scheduled"
                        };
                        SchedulerPayload.Create(schJob);
                        #endregion

                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.StackTrace);
                    }
                }
                #endregion

                return Ok(new { modelId = id, modelState = "model valid", message = "training job scheduled successfully!" });
            }
            else
            {
                return BadRequest(new { modelId = id, modelState = "model not found", message = "model does not exists!" });
            }
        }

        #endregion

        #region create job for scoring
        [HttpPost("{id}/score")]
        public async Task<IActionResult> CreateScoringJobAsync(string id, [FromBody]TrainingRequestParam jsonbody)
        {
            string filePath = "";
            var json = JsonConvert.SerializeObject(jsonbody);
            JObject jo = JObject.Parse(json);

            /* TODO: validation for req body */
            JObject cronjson = JObject.Parse(jo.ToString());
            filePath = cronjson["filePath"].ToString();

            /*request json for zmk */
            JObject req = JObject.Parse(jo.ToString());
            req.Remove("recurrence");
            req.Remove("cronExpression");
            req.Remove("startDate");
            req.Remove("startTimeH");
            req.Remove("startTimeM");

            /* validate if model exists in the ZMOD directory and loaded. */
            if (ModelPayload.Get().Where(m => m.Id == id).Count() == 1)
            {

                List<TrainingResponse> tresp = new List<TrainingResponse>();

                #region schedule scoring

                /* check if same job is scheduled */
                ISchedulerFactory schfack = new StdSchedulerFactory();
                IScheduler scheduler = await schfack.GetScheduler();
                var jobKey = new JobKey(filePath);
                if (await scheduler.CheckExists(jobKey))
                {
                    await scheduler.ResumeJob(jobKey);
                }
                else
                {
                    try
                    {
                        #region create quartz job for training model
                        ITrigger trigger = TriggerBuilder.Create()
                        .WithIdentity($"Training Model Job-{DateTime.Now}")
                        .WithCronSchedule(cronjson["cronExpression"].ToString())
                        .WithPriority(1)
                        .Build();

                        IJobDetail job = JobBuilder.Create<TrainModelJob>()
                        .WithIdentity(filePath)
                        .Build();

                        job.JobDataMap["id"] = id;
                        job.JobDataMap["filePath"] = filePath;
                        job.JobDataMap["reqBody"] = req.ToString();
                        job.JobDataMap["baseurl"] = Configuration["PyServiceLocation:srvurl"];

                        await _scheduler.ScheduleJob(job, trigger);
                        //add to scheduler payload                            
                        SchedulerResponse schJob = new SchedulerResponse()
                        {
                            CreatedOn = DateTime.Now.ToString(),
                            CronExpression = cronjson["cronExpression"].ToString(),
                            DateCreated = DateTime.Now,
                            EditedOn = DateTime.Now.ToString(),
                            FilePath = filePath,
                            Id = id,
                            Name = id,
                            Type = "PMML",
                            Url = "",
                            Recurrence = cronjson["recurrence"].ToString(),
                            StartDate = cronjson["startDate"].ToString(),
                            StartTimeH = (cronjson["startTimeH"].ToString() == null) ? "" : cronjson["startTimeH"].ToString(),
                            StartTimeM = (cronjson["startTimeM"].ToString() == null) ? "" : cronjson["startTimeM"].ToString(),
                            ZMKResponse = tresp.ToList<object>()
                        };
                        SchedulerPayload.Create(schJob);
                        #endregion

                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.StackTrace);
                    }
                }
                #endregion

                return Ok(new { modelId = id, modelState = "model valid", message = "training job scheduled successfully!" });
            }
            else
            {
                return BadRequest(new { modelId = id, modelState = "model not found", message = "model does not exists!" });
            }
        }
        #endregion

        #endregion

        #region DELETE
        [HttpDelete("{id}")]
        public async Task<IActionResult> StopJobAsync(string id)
        {
            if (!String.IsNullOrEmpty(id))
            {
                var filePath = SchedulerPayload.Get().Where(s => s.Id == id).Select(s => s.FilePath).FirstOrDefault();
                ISchedulerFactory schfack = new StdSchedulerFactory();
                IScheduler scheduler = await schfack.GetScheduler();
                await scheduler.PauseJob(new JobKey(filePath));

                var resp = new
                {
                    id = id,
                    status = "STOPPED",
                    message = "Scheduled Job is stopped."
                };

                return Json(resp);
            }
            else
            {
                return NotFound();
            }
        }
        #endregion

    }
}