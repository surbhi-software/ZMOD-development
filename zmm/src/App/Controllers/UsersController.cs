using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace ZMM.App.Controllers
{
    [Authorize]
    [Route("api/[controller]")]
    public class UsersController : Controller
    {
        // readonly ILogger<UsersController>  Logger;
        // GET api/users
        [HttpGet]
        public IActionResult Get()
        {
            string uObj = "This is a secured content";
            return Json(uObj);
        }

        // GET api/users/5
        [HttpGet("{id}")]      
        public IActionResult Get(int id)
        {
            string uObj = "{'input id is ':'" + id + "' }";
            return Json(uObj);
        } 

        // POST api/users
        [HttpPost]
        public void Post([FromBody]string value)
        {
        }

        // PUT api/users/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody]string value)
        {
        }

        // DELETE api/users/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {
        }
    }

}