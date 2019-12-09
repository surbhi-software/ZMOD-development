using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using ZMM.Helpers.Common;

namespace ZMM.App.Controllers
{
    [Route("[controller]/[action]")]
    public class AccountController : Controller
    {
        readonly ILogger<AccountController>  Logger;
        IConfiguration Configuration { get; }
        public AccountController(IConfiguration configuration, ILogger<AccountController> log)
        {
            this.Configuration = configuration;
            this.Logger = log;
        }

        [HttpGet]
        public IActionResult Index()
        {
            return View();
        } 

        [HttpGet]
        public IActionResult Home()
        {
            return View();
        }

        [HttpGet]
        public IActionResult Login(string returnUrl = "/")
        {
            return Challenge(new AuthenticationProperties() { RedirectUri = returnUrl });
        }

        [Authorize]
        [NonAction]
        public JsonResult GetUserInfo()
        {
            Dictionary<string,string> Result = new Dictionary<string, string>();            
            foreach(System.Security.Claims.Claim Cl in HttpContext.User.Claims)
            {
                if(Cl.Type.Equals("name")) Result["name"] = Cl.Value;
                else if(Cl.Type.Equals("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")) Result["email"] = Cl.Value;
                else if(Cl.Type.Equals("role")) Result["role"] = Cl.Value;
            }
            return new JsonResult(Result);
        }
        
        [Authorize]
        [HttpGet("~/api/account/logout")]  
        public async Task<IActionResult> LogoutAsync()  
        {              
            //HttpContext.Authentication.SignOutAsync("Cookies");
            Console.WriteLine("Logging out...");
            // await Microsoft.AspNetCore.Authentication.AuthenticationHttpContextExtensions.SignOutAsync(this.HttpContext,"Cookies");            
            string url = "/";            
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return SignOut(new AuthenticationProperties { RedirectUri = url }, CookieAuthenticationDefaults.AuthenticationScheme, OpenIdConnectDefaults.AuthenticationScheme); 
        } 
       
        
        [HttpGet("~/api/account/userInfo")]   
        public async Task<IActionResult> GetGravatarImage()
        {
            await Task.FromResult(0);
            string gravatarUrl="";
            string userEmail = this.GetUserEmail() ;
            using (MD5 md5Hash = MD5.Create())
            {
                string hash = MD5Helper.GetMd5Hash(md5Hash, userEmail);
                if (MD5Helper.VerifyMd5Hash(md5Hash, userEmail, hash))
                {                   
                    gravatarUrl = "{'gravtarUrl': 'https://gravatar.com/avatar/" + hash +"?d=404'}";
                    JObject jObj = JObject.Parse(gravatarUrl);
                    return Json(jObj);
                } 
                else
                {
                    return BadRequest();
                }               
            }
        }

        [NonAction]
        public string GetUserEmail()
        {            
            Dictionary<string,string> Result = new Dictionary<string, string>();            
            foreach(System.Security.Claims.Claim Cl in HttpContext.User.Claims)
            {
                if(Cl.Type.Equals("name")) Result["name"] = Cl.Value;
                else if(Cl.Type.Equals("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")) Result["email"] = Cl.Value;
                else if(Cl.Type.Equals("role")) Result["role"] = Cl.Value;
            }
            return Result["email"];
        }
    }
}