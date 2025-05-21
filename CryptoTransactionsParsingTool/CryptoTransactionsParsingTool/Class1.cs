using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;

namespace CryptoTransactionsParsingTool
{
    class CryptoAsset
    {
        public DateTime Timestamp { get; private set; }
        public string Description { get; private set; }
        public string Asset { get; private set; }
        public float Amount { get; private set; }
        public string NativeCurrency { get; private set; }

        //Mapping from internal property to CSV column name in this file
        private Dictionary<string, string> _columnMap;

        public CryptoAsset(Dictionary<string,string> columnMap, IDictionary<string, string> csvRow)
        {
            _columnMap = columnMap;

            Timestamp = ParseDateTime(GetField(csvRow, "Timestamp"));
            Description = GetField(csvRow, "Description");
            Asset = GetField(csvRow, "Asset");
            Amount = ParseFloat(GetField(csvRow, "Amount"));
            NativeCurrency = GetField(csvRow, "Native Currency");
            
        }
        private string GetField(IDictionary<string,string> row, string properyName)
        {
            if(_columnMap.TryGetValue(properyName,out var columnName) && row.TryGetValue(columnName, out var value))
            {
                return value;
            }
            return null;
        }
        private DateTime ParseDateTime(string s)
        {
            DateTime.TryParse(s, out var dt);
            return dt;
        }

        private float ParseFloat(string s)
        {
            float.TryParse(s, out var f);
            return f;
        }
    }
}
