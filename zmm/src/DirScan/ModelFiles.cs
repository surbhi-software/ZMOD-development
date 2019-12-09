using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using JgenCy.OperatingSystemCore;
using System.Linq;
using System.Threading.Tasks;
using System;
using System.Diagnostics;
using System.IO;

namespace ZMM.DS
{
    public class PmmlFileInfo : ZmodFileInfo
    {
        public long Lines { get; set; } = 0;
        public List<string> ModelTags { get; set; } = new List<string>();
        public string OutputField { get; set; } = "";
        public string Segments { get; set; } = "";
        public string DeepNetwork { get; set; } = "";
        public string ModelData { get; set; } = "";
        public string Parse(string str, string symbols, bool justValues = false)
        {
            string result = "";
            var symList = symbols.Split(new char[] { ' ', ',' }, StringSplitOptions.RemoveEmptyEntries);
            var parameters = str.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var s in parameters)
            {
                var kvp = s.Split(new char[] { '=', '"' }, StringSplitOptions.RemoveEmptyEntries);
                if (symList.Contains(kvp[0]))
                {
                    if (justValues)
                        result = $"{result}{(result.Length > 0 ? ", " : "")}{kvp[1]}";
                    else
                        result = $"{result}{(result.Length > 0 ? ", " : "")}{kvp[0]}: {kvp[1]}";
                }
            }
            return result;
        }
        public PmmlFileInfo(string path)
        : base(path)
        {
            #region collect more meta data of PMML file
            var tf = new TextFile(path);
            Lines = tf.Lines.Count();
            var m = from _ in tf.Lines
                    where _.Contains("<MiningModel modelName")
                    select Parse(_, "modelName, algorithmName, functionName");
            if (m.Count() > 0)
                ModelTags = m.ToList();
            var o = from _ in tf.Lines
                    where _.Contains("<OutputField")
                    select Parse(_, "name");
            if (o.Count() > 0)
                OutputField = string.Join(", ", o);
            var s = from _ in tf.Lines
                    where _.Contains("<Segment")
                    select Parse(_, "id", justValues: true);
            if (s.Count() > 0)
            {
                s = from _ in s
                    where !string.IsNullOrEmpty(_)
                    select _;
                Segments = string.Join(", ", s);
            }
            var n = from _ in tf.Lines
                    where _.Contains("<DeepNetwork") || _.Contains("<NeuralNetwork")
                    select Parse(_, "modelName, functionName, numberOfLayers, activationFunction");
            if (n.Count() > 0)
                DeepNetwork = string.Join("; ", n);
            var d = from _ in tf.Lines
                    where _.Contains("<Extension") && Parse(_, "data, modelName").Contains("data")
                    select Parse(_, "data, modelName");
            if (d.Count() > 0)
                ModelData = string.Join("; ", d);
            #endregion
        }
    }
}