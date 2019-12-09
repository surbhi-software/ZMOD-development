using System;
using System.IO;
using System.IO.Compression;
using System.Threading.Tasks;

namespace ZMM.Helpers.Zipper
{
    /// <summary>
    /// This class is used for unzip the .zip or .7z
    /// </summary>
    public class ZipHelper
    {       
        string zipOr7zPath = string.Empty;
        string extractPath = string.Empty;

        #region Constructor
        public ZipHelper()
        {

        }
        #endregion

        #region Extract archive file
        public static async Task<bool> ExtractAsync(string zipOr7zPath, string extractPath)
        {
            bool result = false;            
            try
            {
                if ((!string.IsNullOrEmpty(zipOr7zPath)) && (!string.IsNullOrEmpty(extractPath)))
                {
                    if(Path.GetExtension(zipOr7zPath).Contains("7z"))
                    {
                        //format not supported
                        return false;
                    }
                    ZipFile.ExtractToDirectory(zipOr7zPath, extractPath);
                    await Task.FromResult(0);
                    result = true;
                }
            }
            catch(Exception ex)
            {
                //TODO: ILogger
                string err = ex.Message;
            }
            return result;
        }
        #endregion
    }
}