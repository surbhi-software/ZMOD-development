using Microsoft.AspNetCore.Http;
using System.IO;
using System;

namespace ZMM.Helpers.ZMMDirectory
{
    public static class DirectoryHelper
    {
        #region variables
        public static string fileUploadDirectoryPath; 
        // public static string fileUploadDirectoryPath = Directory.GetCurrentDirectory().Replace(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + "/wwwroot/uploads";
        public static string requestUrl { get; set; } = "";
        #endregion

        #region Directory
        public static int CountDirectories(string path)
        {
            int count = 0;            
            string[] subdirectories = Directory.GetDirectories(path);
            foreach (string subdirectory in subdirectories)
            {   
                count = CountSubDirectories(subdirectory, ref count);                
            }
            count += subdirectories.Length;    
            return count;
        }
        private static int CountSubDirectories(string path, ref int count)
        {            
            string[] subdirectories = Directory.GetDirectories(path);
            count += subdirectories.Length;
            foreach (string subdirectory in subdirectories)
            {                
                CountSubDirectories(subdirectory, ref count);
            }
            return count;
        }
        #endregion
        
        #region Count files
        public static int CountFiles(string path)
        {
            int count = 0;
            
            string[] files = Directory.GetFiles(path,"*.*" ,SearchOption.AllDirectories);

            count = files.Length;
                
            return count;
        }
        #endregion
        
        public static string GetDataDirectoryPath()
        {             
            return fileUploadDirectoryPath + "/Data/";
        }
        public static string GetModelDirectoryPath()
        {
            return fileUploadDirectoryPath + "/Models/";
        }
        public static string GetCodeDirectoryPath()
        {
            return fileUploadDirectoryPath + "/Code/";
        }
        public static string GetDataUrl(string filename)
        {
            string _path = string.Empty;
            _path = $"{GetRequestUrl()}/api/data/preview/{filename}";
            return _path;
        }
        public static string GetCodeUrl(string filename)
        {
            string _path = string.Empty;
            string fileExt = Path.GetExtension(filename).Remove(0,1);
            if(fileExt.ToLower() == "ipynb")
            {
                _path = $"{GetRequestUrl()}/code/{Path.GetFileNameWithoutExtension(filename)}/{filename}";
            }
            else
            {
               _path = $"{GetRequestUrl()}/code/{filename}";
            }            
            return _path;
        }
        public static string GetModelUrl(string filename)
        {
            string _path = string.Empty;
            _path = $"{GetRequestUrl()}/model/{filename}";
            return _path;
        }
        public static void SetRequestUrl(HttpRequest request)
        {
            if(request.IsHttps)
            {
                request.Scheme = "https";
            }
            requestUrl = $"{request.Scheme.ToString()}://{request.Host.ToString()}";
        }
        public static string GetRequestUrl()
        {           
            return requestUrl;
        }
    }
}