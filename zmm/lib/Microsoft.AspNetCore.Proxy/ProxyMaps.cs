using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

namespace Microsoft.AspNetCore.Proxy
{

    public class Map
    {
        public string Pattern { get; set;}

        public string ResolveHost { get; set;}

        public int ResolvePort { get; set;} = 0;

        public bool EnableAuthentication { get; set;} = false;

        public bool EnableWebSocket { get; set;} = false;

        public Dictionary<string,string> ReWritePathPatterns = new Dictionary<string, string>();

    }
    public static class Maps 
    {

        private static List<Map> ListOfMaps = new List<Map>();

        public static Dictionary<string, int> MappedURLPattern = new Dictionary<string, int>();
        private static void Init(ref IApplicationBuilder app)
        {
            try
            {
                ConfigurationBuilder configurationBuilder = new ConfigurationBuilder();                   
                var tempPath = "proxy.config.json";
                configurationBuilder.AddJsonFile(tempPath, false);
                var rootConfig = configurationBuilder.Build();
                string MapPatternKey = string.Empty;
                string MapPatternValue = string.Empty;
                bool MapEnableAuthenticationValue = false;
                bool MapEnableWebSocketValue = false;
                int MapResolvePortValue = 0;
                for(int i=0;;i++)
                {
                    MapPatternKey = "Maps:" + i + ":URLPattern";
                    MapPatternValue = rootConfig[MapPatternKey];
                    if(MapPatternValue == null) break;
                    else
                    {
                        Map TempMap = new Map();
                        TempMap.Pattern = MapPatternValue;
                        TempMap.ResolveHost = rootConfig["Maps:" + i + ":ResolveHost"];
                        if(int.TryParse(rootConfig["Maps:" + i + ":ResolvePort"], out MapResolvePortValue)) TempMap.ResolvePort = MapResolvePortValue;
                        if(bool.TryParse(rootConfig["Maps:" + i + ":EnableAuthentication"], out MapEnableAuthenticationValue)) TempMap.EnableAuthentication = MapEnableAuthenticationValue;
                        if(bool.TryParse(rootConfig["Maps:" + i + ":EnableWebSocket"], out MapEnableWebSocketValue)) TempMap.EnableWebSocket = MapEnableWebSocketValue;
                        PopulateReWritePathPatterns(rootConfig, i, ref TempMap.ReWritePathPatterns);
                        ListOfMaps.Add(TempMap);                        
                    }
                }
            }
            catch(Exception ex)
            {
                Console.Error.WriteLine("Error while initializing Proxy", ex);
            }
        }

        private static void PopulateReWritePathPatterns(IConfiguration RootConfig, int ItemIndex, ref Dictionary<string,string> ListOfReWritePathPatterns)
        {
            //Maps:i:ReWritePathPattern:0:In  -> Key
            //Maps:i:ReWritePathPattern:0:Out -> Value
            ListOfReWritePathPatterns = new Dictionary<string, string>();
            string MapReWritePathPatternItemKey = string.Empty;
            string MapReWritePathPatternItemValue = string.Empty;
            string MapReWritePathPatternItemKeyConfigurationPattern = string.Empty;
            for(int i=0;;i++)
            {
                MapReWritePathPatternItemKeyConfigurationPattern = "Maps:" + ItemIndex + ":ReWritePathPattern:" + i + ":In";
                MapReWritePathPatternItemKey = RootConfig[MapReWritePathPatternItemKeyConfigurationPattern];
                if(MapReWritePathPatternItemKey == null) break;
                else
                {
                    MapReWritePathPatternItemValue = RootConfig["Maps:" + ItemIndex + ":ReWritePathPattern:" + i + ":Out"];
                    if(MapReWritePathPatternItemValue != null)
                    {
                        ListOfReWritePathPatterns[MapReWritePathPatternItemKey] = MapReWritePathPatternItemValue;
                    }
                }
            }
        }

        private static void MappedHttpRequestBuilder(IApplicationBuilder app, int PatternIndex)
        {            
            app.RunProxy(new ProxyOptions
            {
                Scheme = "http"
            });
        }
        private static void ConfigureNewlyAddedMapForHttpAndWS(ref IApplicationBuilder app)
        {
            app.MapWhen(IsHttpRequestMatched, builder =>
            {
                builder.RunProxy(new ProxyOptions
                {
                    Scheme = "http",
                    Host = new HostString("localhost", 7007)
                });   
            });

            app.MapWhen(IsWsRequestMatched, builder => builder.UseWebSockets().RunProxy(new ProxyOptions
            {
                Scheme = "ws",
                Host = new HostString("localhost", 7007)
            }));
        }
        public static void Do(ref IApplicationBuilder app)
        {            
            app.UseWebSockets();
            Init(ref app);     
            ConfigureNewlyAddedMapForHttpAndWS(ref app);      
        }

        private static bool IsHttpRequestMatched(HttpContext httpContext)
        {
            bool Status = false;
            for(int i=0; i<ListOfMaps.Count; i++)
            {
                Map InterestedMap = ListOfMaps[i];
                Status = (IsHttpRequest(httpContext, InterestedMap.Pattern));
                if(Status && InterestedMap.EnableAuthentication)  Status = httpContext.User.Identity.IsAuthenticated;
                if(Status)  
                {
                    MappedURLPattern[httpContext.Request.Path.Value] = i;
                    break;
                }
            }
            return Status;
        }

        private static bool IsWsRequestMatched(HttpContext httpContext)
        {
            bool Status = false;
            for(int i=0; i<ListOfMaps.Count; i++)
            {
                Map InterestedMap = ListOfMaps[i];
                Status = (IsHttpRequest(httpContext, InterestedMap.Pattern));
                if(Status && InterestedMap.EnableAuthentication)
                {
                    Status =  httpContext.User.Identity.IsAuthenticated;
                    if(Status && InterestedMap.EnableWebSocket) Status =  httpContext.WebSockets.IsWebSocketRequest;
                }
                if(Status) 
                {
                    MappedURLPattern[httpContext.Request.Path.Value] = i;
                    break;
                }
            }
            //Not Authenticated User with WS Request need to implement
            return Status;
        }

        private static bool IsHttpRequest(HttpContext httpContext, string URLPattern)
        {
            bool Status = false;
            Status = (httpContext.Request.Path.Value.StartsWith(URLPattern, StringComparison.OrdinalIgnoreCase));
            return Status;
        }

        static Maps()
        {            
        }

        public static HostString ResolveProxyHostPortAndPath(string requestPath, ref PathString inputPath)
        {
            HostString Out;    
            if(MappedURLPattern.ContainsKey(requestPath))
            {        
                int PatternIndex = MappedURLPattern[requestPath];
                Map TempMap = ListOfMaps[PatternIndex];
                Out =  new HostString(TempMap.ResolveHost, TempMap.ResolvePort);
                if(TempMap.ReWritePathPatterns.Count > 0)
                {
                    foreach(KeyValuePair<string,string> keyValue in TempMap.ReWritePathPatterns)
                    {
                        inputPath = inputPath.ToString().StartsWith(keyValue.Key) ? new PathString(reWritePath(inputPath.ToString(), keyValue.Key, keyValue.Value)) : inputPath;
                    }
                }
                //Need to Manage MappedURLPattern by user session
                MappedURLPattern.Remove(requestPath);
            }
            else throw new Exception("Unable to resolve proxy map " + requestPath);
            return Out;
        }

        private static string reWritePath(string inputPath, string pathPattern, string pathOverWrite)
        {
            string outputPath = string.Empty;
            outputPath = inputPath.Replace(pathPattern, pathOverWrite);
            return outputPath;
        }
    }
}