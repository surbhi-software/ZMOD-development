using Microsoft.Extensions.Configuration;

namespace ZMM.Helpers.Extensions
{
    public static class StringExtensions
    {

        /// <summary>
        ///  convert the first letter of the string to Uppercase
        /// </summary>
        /// <param name="value"></param>
        /// <returns>string</returns>
        public static string FirstLetterToUppercase(this string value)
        {            
            if (value.Length > 0)
            {
                char[] array = value.ToCharArray();
                array[0] = char.ToUpper(array[0]);
                return new string(array);
            }
            return value;
        }
        public static string ToPrettyJsonString(this string value)
        {
            if(value.Length > 0)
            {
                //value = value.Replace(@"\","");
                value = value.Replace('\\',' ');                
            }

            return value;
        }

        public static string AddSlash(this string value)
        {
            if(value.Length > 0)
            {
                value = value.Replace("  ","\\");      
            }

            return value;
        }

        public static string ConvertToPath(this string value, string filepath, string BASEURL)
        {
            //replace http://localhost:5000 to full filepath           
            value = value.Replace(BASEURL, filepath);
            //value = value.Replace(@"/",@"\");
            return value;
        }        
    }
}