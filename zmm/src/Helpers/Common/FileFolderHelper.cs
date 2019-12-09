using System.Data;
using System.IO;
using System.Linq;
using System.Text;

namespace ZMM.Helpers.Common
{
    public static class FileFolderHelper
    {
        #region RenameFile (uses fully qualified file-name)
        public static void RenameFile(string originalName, string newName)
        {            
            File.Move(originalName,newName);           
        }
        #endregion
    }
}