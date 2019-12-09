using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;


namespace ZMM.App
{
    public class IndexModel : PageModel
    {
        public string GitHubAvatar { get; set; }

        public string GitHubLogin { get; set; }

        public string GitHubName { get; set; }

        public string GitHubUrl { get; set; }

        public string Email {get; set;}

        public string Name {get; set;}

        public string GivenName {get; set;}

        public string Id { get; set;}

        public string UserRoles { get; set;}
        

        public async Task OnGetAsync()
        {
            if (User.Identity.IsAuthenticated)
            {
                await Task.FromResult(0);
                Name = User.FindFirst(c => c.Type == ClaimTypes.Name)?.Value;
                GivenName = User.FindFirst(c => c.Type == ClaimTypes.GivenName)?.Value;
                Email = User.FindFirst(c => c.Type == ClaimTypes.Email)?.Value;
                UserRoles = User.FindFirst(c => c.Type == ClaimTypes.Role)?.Value;
                //GitHubLogin = User.FindFirst(c => c.Type == "urn:github:login")?.Value;
                //GitHubUrl = User.FindFirst(c => c.Type == "urn:github:url")?.Value;
                //GitHubAvatar = User.FindFirst(c => c.Type == "urn:github:avatar")?.Value;

                //string accessToken = await HttpContext.GetTokenAsync("id_token");

                //var github = new GitHubClient(new ProductHeaderValue("AspNetCoreGitHubAuth"), new InMemoryCredentialStore(new Credentials(accessToken)));
                

            }
        }
    }
}
