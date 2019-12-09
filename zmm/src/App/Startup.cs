using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OAuth;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Features;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Extensions.Primitives;
using Newtonsoft.Json.Linq;
using ZMM.App.PyServicesClient;
using ZMM.App.ZSServiceClient;
using ZMM.Authorizations.Claims;
using ZMM.Helpers.ZMMDirectory;
using System.IO;
using Microsoft.AspNetCore.SpaServices.AngularCli;
using Microsoft.OpenApi.Models;
using Quartz;
using System.Collections.Specialized;
using Quartz.Impl;
using Microsoft.AspNetCore.Server.Kestrel.Core;

namespace ZMM.App
{
    public class Startup
    {

        private readonly ILogger Logger;
        public IConfiguration Configuration { get; }
        public IWebHostEnvironment Environment { get; }

        private bool IsDevelopment { get; set; } = false;

        private string ContentDir = string.Empty;

        private const string XForwardedPathBase = "X-Forwarded-PathBase";
        private const string XForwardedProto = "X-Forwarded-Proto";

        public Startup(IConfiguration configuration, IWebHostEnvironment environment,ILogger<Startup> logger)
        {
            Configuration = configuration;
            Environment = environment;
            Logger = logger;
            IsDevelopment = environment.EnvironmentName.ToString() == "Development";
            Logger.LogInformation("Initializing " + Configuration["Type"]);
            InitContentDir(ref ContentDir);
        }        


        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {

            #region Allow Synchronous IO to read stream in model and code
            services.Configure<KestrelServerOptions>(options =>
            {
                options.AllowSynchronousIO = true;
            });
            #endregion
            
            #region Added Controller and Razor Page for Login
            services.AddControllersWithViews().AddNewtonsoftJson();
            services.AddRazorPages().AddNewtonsoftJson();
            #endregion

            #region Profile works on Client UI /wwwroot with dotnet 3.0 inbuilt configuration
            string ClientUIDirectory = IsDevelopment ? Configuration["WebApp:SourcePath"] : Configuration["WebApp:BuildPath"];
            if(ClientUIDirectory.Equals(string.Empty) || ClientUIDirectory == null) throw new Exception("Error : If you are running production environment then make sure you have configure wwwroot folder and if you are in development environment then configure WebApp:SourcePath ClientApp folder in respective appsettings*.json file"); 
            if(!System.IO.Directory.Exists(ClientUIDirectory)) throw new Exception("Error : It seems Client UI folder : " + ClientUIDirectory + " is not present; To resolve this, You need to publish solution once with command : dotnet publish ZMM.sln from ZMM folder.");
            services.AddSpaStaticFiles(configuration =>
            {
                configuration.RootPath =  ClientUIDirectory;
            }); 
            #endregion

            
            #region Identity Provider (KeyCloak) Integration
            services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                options.DefaultSignInScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;               
            })
            .AddCookie("Cookies")

            .AddOpenIdConnect(options =>
            {   
                SetOIDCConfiguration(ref options, bool.Parse(Configuration["Authentication:OIDC:IsSecuredHTTP"])); 
            });             

            services.AddAuthorization(options =>
            {
                options.AddPolicy("Administrator", policy => policy.RequireClaim("role", "Administrator"));
                options.AddPolicy("User", policy => policy.RequireClaim("role", "User"));  
                options.AddPolicy("CanUploadResourceInCode", policy => policy.RequireClaim("role", "User" , "Administrator"));        
            });        
            #endregion
            
            #region Register the Swagger generator
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "ZMOD", Version = "v1" });
            });
            #endregion            
            
            #region Initialize clients in singleton service
            var pySrvLocation = Configuration["PyServiceLocation:srvurl"];
            var zadSrvLocation = Configuration["ZS:srvurl"];
            string ToolHostURL = Configuration["Tool:Host"];
            services.AddSingleton<IConfiguration>(Configuration);
            services.AddSingleton<IPyNNServiceClient>(new PyNNServiceClient(Configuration));
            services.AddSingleton<IPyAutoMLServiceClient>(new PyAutoMLServiceClient(Configuration));
            services.AddSingleton<IBaseImageForWielding>(new BaseImageForWielding(Configuration));
            services.AddSingleton<IPyJupyterServiceClient>(new PyJupyterServiceClient(ToolHostURL));
            services.AddSingleton<IPyZMEServiceClient>(new PyZMEServiceClient(Configuration));
            services.AddSingleton<IZSModelPredictionClient>(new ZSModelPredictionClient(Configuration));      
            services.AddSingleton<IPyTensorServiceClient>(new PyTensorServiceClient(ToolHostURL,ContentDir));
            services.AddSingleton<IPyCompile>(new PyCompile(Configuration));  
            services.AddSingleton(provider => GetScheduler());
            #endregion

            #region Add Proxy to services
            services.AddProxy();
            #endregion
            
            Console.WriteLine("*****************************************");
            Console.WriteLine($"ZMM " + (IsDevelopment ? "Development" : "Production") + " initiated...");
            Console.WriteLine($"ZMK =====>>> {pySrvLocation}");
            Console.WriteLine($"ZAD =====>>> {zadSrvLocation}");
        }

        #region Setup User Identity Provider (KeyCloak) configuration
        public void SetOIDCConfiguration(ref OpenIdConnectOptions options, bool NeedSecuredHttp = true)
        {
            
                options.Authority = Configuration["Authentication:OIDC:AuthorizationEndpoint"];
                options.ClientId = Configuration["Authentication:OIDC:ClientId"];
                options.RequireHttpsMetadata = NeedSecuredHttp;
                options.SaveTokens = false;
                options.ClientSecret = Configuration["Authentication:OIDC:ClientSecret"];
                options.GetClaimsFromUserInfoEndpoint = true;
                options.SignedOutRedirectUri = Configuration["Authentication:OIDC:SignOutRedirectURL"];
                options.ResponseType = Configuration["Authentication:OIDC:ResponseType"];
                options.ClaimActions.Add(new CustomClaimAction("role", "role", "user_roles", "User"));              	
                options.Events = new OpenIdConnectEvents
                {                   	
                    
                  	OnRedirectToIdentityProvider = redirectContext=>
                    {
                        if(NeedSecuredHttp) redirectContext.ProtocolMessage.RedirectUri = redirectContext.ProtocolMessage.RedirectUri.Replace("http://", "https://", StringComparison.OrdinalIgnoreCase);
                        return Task.FromResult(0);
                    },
                    OnRemoteFailure = context =>
                    {
                        context.HandleResponse();
                        context.Response.Redirect("/Account/Error?message=" + context.Failure.StackTrace);                           
                        return Task.FromResult(0);
                    }                   
                };
        }
        #endregion

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, ILoggerFactory loggerFactory)
        {          
            #region Enable HSTS option for AWS production system for https 
            if(IsEnvironmentOtherThanDevelopmentAndProduction()) app.UseHsts();
            #endregion

            #region Add Log Factory -> You can update its behaviour from appsettings*.json configuration
            AddLogger(ref loggerFactory);     
            #endregion

          	          

            // below is the fix for angular app reload redirections          
            app.Use(async (context, next) =>
            {                
                await next.Invoke();
                if (context.User.Identity.IsAuthenticated && context.Response.StatusCode == 404 && !context.Request.Path.Value.Contains("/api"))
                {
                    
                    context.Request.Path = new PathString("/index.html");
                    await next.Invoke();
                }
                else 
                {                    
                    context.Request.Path = new PathString("/");                    
                }                
            }); 
            
            if(IsDevelopment) app.UseDeveloperExceptionPage();

            app.UseForwardedHeaders(new ForwardedHeadersOptions
            {
                ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto
            });              

            #region swagger middleware
            app.UseSwagger();

            // Enable middleware to serve swagger-ui (HTML, JS, CSS, etc.),
            // specifying the Swagger JSON endpoint.
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "ZMOD v1");
            });      

            #endregion                   


            app.UseStaticFiles();

            app.UseRouting();
           
            app.UseAuthentication();

            app.UseAuthorization();

            app.UseProxy();

            app.UseEndpoints(routes =>
            {
                routes.MapRazorPages();

                routes.MapControllers();

                routes.MapControllerRoute(
                    name: "default",
                    pattern: "{controller}/{action}/{id?}");

                routes.MapControllerRoute(
                    name: "train",
                    pattern: "{controller}/{action}");               

            });

            #region To start ng serve without building client ui
            string ClientUIDirectory = Configuration["WebApp:SourcePath"];
            if(ClientUIDirectory.Equals(string.Empty) || ClientUIDirectory == null) throw new Exception("Error : Please, configure WebApp:SourcePath in appsettings.Development.json"); 
            if(IsDevelopment && !System.IO.Directory.Exists(ClientUIDirectory)) throw new Exception("Error : It seems that Client (Angular UI) Source folder is not present; To resolve this issue, Please, checkout this folder from repository /src/App/ClientApp");
            app.UseSpa(spa =>
            {
                spa.Options.SourcePath = ClientUIDirectory;
                if (IsDevelopment)
                {
                    spa.UseAngularCliServer(npmScript: "start");
                }
            });
            #endregion

        }
        private void AddLogger(ref ILoggerFactory loggerFactory)
        {
            var LogFileName = "Logs" + System.IO.Path.DirectorySeparatorChar + "ZMM-{Date}-" + Guid.NewGuid().ToString() + ".log";
            loggerFactory.AddFile(LogFileName);
        }
        private void InitContentDir(ref string DirPath)
        {       
            try
            {   
                DirPath = Directory.GetCurrentDirectory();
                if(DirPath.Contains("src")) 
                {
                    int startIdx = Directory.GetCurrentDirectory().IndexOf("src");
                    DirPath = Directory.GetCurrentDirectory().Substring(0, startIdx - 1);
                    DirPath = $"{Directory.GetParent(DirPath)}/ZMOD";
                }
                else
                {
                    DirPath = Directory.GetParent(DirPath).ToString() +"/ZMOD";
                }                
                
                System.Console.WriteLine(Directory.GetCurrentDirectory());
                if (!Directory.Exists(DirPath))
                {
                    Directory.CreateDirectory(DirPath);
                }
                if (string.IsNullOrEmpty(DirectoryHelper.fileUploadDirectoryPath))
                {
                    DirectoryHelper.fileUploadDirectoryPath = DirPath.Replace(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                }
                DirectoryCreator.CreateFolders(DirPath);
                Logger.Log(LogLevel.Information, "Initialize content directory : " + DirPath);
            }
            catch(Exception ex)
            {
                Logger.LogCritical("Initializing ZMOD directory " + ex.StackTrace);
            }
        }

        private IScheduler GetScheduler()
        {
            var properties = new NameValueCollection
            {
                ["quartz.scheduler.instanceName"] = "ZMM_JobScheduler",
                ["quartz.threadPool.type"] = "ZMM.App.ThreadPool, ZMMPool",
                ["quartz.threadPool.threadCount"] = "10",
                ["quartz.jobStore.type"] = "ZMM.App.JobStore, ZMMJobStore",
            };
            var schedulerFactory = new StdSchedulerFactory();
            var scheduler = schedulerFactory.GetScheduler().Result;
            scheduler.Start();
            return scheduler;
        }

        private bool IsEnvironmentOtherThanDevelopmentAndProduction()
        {
            return IsDevelopment && !this.Environment.EnvironmentName.Equals("Production");
        }
    }
}
