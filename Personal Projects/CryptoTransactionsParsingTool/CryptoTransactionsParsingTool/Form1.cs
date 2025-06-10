using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;

namespace CryptoTransactionsParsingTool
{
    public partial class Form1 : Form
    {
        Dictionary<string,string> sheet1Map = new Dictionary<string, string> {
            {"Timestamp", "Timestamp (UTC)"},
            {"Description", "Transaction Description"},
            {"Asset", "Currency"},
            {"Amount", "Amount"},
            {"NativeCurrency", "Native Currency"}
        };

        Dictionary<string,string> sheet2Map = new Dictionary<string, string> {
            {"Timestamp", "Date"},
            {"Description", "Type"},
            {"Asset", "Sent Currency"},
            {"Amount", "Sent Amount"},
            {"NativeCurrency", "Sent Currency"}
        };
        Dictionary<string, string> sheet3Map = new Dictionary<string, string> {
            {"Timestamp", "Acquired"},
            {"Description", "Transaction Type"},
            {"Asset", "Currency Name"},
            {"Amount", "Currency Amount"},
            {"NativeCurrency", "Gains (CAD)"}
        };
        Dictionary<string, string> sheet4Map = new Dictionary<string, string> {
            {"Timestamp", "Date"},
            {"Description", "Label"},
            {"Asset", "Asset"},
            {"Amount", "Amount"},
            {"NativeCurrency", "Value (CAD)"}
        };

        public Form1()
        {
            InitializeComponent();
            groupBox1.AllowDrop = true;
        }

        private void groupBox1_DragDrop(object sender, DragEventArgs e)
        {
            string filePath = "";
            try
            {
                if (e.Data.GetDataPresent(DataFormats.FileDrop))
                {
                    string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);

                    if (files.Length > 0)
                        filePath = files[0];

                    if(Path.GetExtension(filePath).ToLower() == ".csv")
                    {
                        var columnMap = DetectMapping(filePath);
                        ParseCSVFile(filePath, columnMap);
                    }
                }
                else
                {
                    MessageBox.Show("Please drop a CSV file.", "Invalid File Type", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }catch(Exception ex)
            {
                MessageBox.Show($"Error processing file: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void groupBox1_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
                e.Effect = DragDropEffects.Copy;
            else
                e.Effect = DragDropEffects.None;
            Console.WriteLine(e.Data.ToString());
        }
        private void ParseCSVFile(string filepath, Dictionary<string, string> columnMap)
        {
            var reader = new StreamReader(filepath);
            var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

            var records = csv.GetRecords<dynamic>().ToList();

            foreach (var record in records)
            {
                var dict = (IDictionary<string, object>)record;

                string timestampStr = dict.TryGetValue(columnMap["Timestamp"], out var ts) ? ts?.ToString() : null;
                string description = dict.TryGetValue(columnMap["Description"], out var desc) ? desc?.ToString() : null;
                string asset = dict.TryGetValue(columnMap["Asset"], out var a) ? a?.ToString() : null;
                string amountStr = dict.TryGetValue(columnMap["Amount"], out var amt) ? amt?.ToString() : null;
                string nativeCurrency = dict.TryGetValue(columnMap["NativeCurrency"], out var nc) ? nc?.ToString() : null;

                Console.WriteLine("Transaction");
                Console.WriteLine(timestampStr);
                Console.WriteLine(description);
                Console.WriteLine(asset);
                Console.WriteLine(amountStr);
                Console.WriteLine(nativeCurrency);
                Console.WriteLine("End");
            }
        }

        private Dictionary<string, string> DetectMapping(string filepath)
        {
            var reader = new StreamReader(filepath);
            var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

            csv.Read();
            csv.ReadHeader();
            var headers = csv.HeaderRecord;

            //Check for distinctive columns in each mapping
            if (headers.Contains("Timestamp (UTC)") && headers.Contains("Transaction Description"))
                return sheet1Map;
            if (headers.Contains("ID") && headers.Contains("Sent Amount"))
                return sheet2Map;
            if (headers.Contains("Currency Name") && headers.Contains("Acquired(DateTime)"))
                return sheet3Map;
            if (headers.Contains("Asset") && headers.Contains("Value (CAD)"))
                return sheet4Map;

            //Defualt or unknown format
            throw new ArgumentException("Unrecognized CSV format");
        }
    }
}
