using System.Data;
using System.IO;
using System.Linq;
using System.Text;

namespace ZMM.Helpers.Common
{
    public static class CsvHelper
    {
        public static int[] GetCsvRowColumnCount(string csvFilePath)
        {
            int[] rowColCount = new int[2] { 0, 0 };

            if (Path.GetExtension(csvFilePath).ToLower().Contains("csv"))
            {
                var lines = File.ReadAllLines(csvFilePath);
                rowColCount[0] = lines.Count();//includes header
                rowColCount[1] = lines[0].Split(',').Count();
            }

            return rowColCount;
        }

        public static string ToCSV(this DataTable table, string delimator)
        {
            var result = new StringBuilder();
            for (int i = 0; i < table.Columns.Count; i++)
            {
                result.Append(table.Columns[i].ColumnName);
                result.Append(i == table.Columns.Count - 1 ? "\n" : delimator);
            }
            foreach (DataRow row in table.Rows)
            {
                for (int i = 0; i < table.Columns.Count; i++)
                {
                    result.Append(row[i].ToString());
                    result.Append(i == table.Columns.Count - 1 ? "\n" : delimator);
                }
            }
            return result.ToString().TrimEnd(new char[] { '\r', '\n' });           
        }
    }
}
