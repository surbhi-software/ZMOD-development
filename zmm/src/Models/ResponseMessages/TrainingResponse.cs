using System;
using System.Collections.Generic;

namespace ZMM.Models.ResponseMessages
{
    public class TrainingResponse
    {
        public string pmmlFile { get; set; }
        public string dataFolder { get; set; }
        public string fileName { get; set; }
        public string tensorboardLogFolder { get; set; }
        public string tensorboardUrl { get; set; }
        public string lossType { get; set; }
        public IList<string> listOfMetrics { get; set; }
        public int batchSize { get; set; }
        public int epoch { get; set; }
        public int stepsPerEpoch { get; set; }
        public string problemType { get; set; }
        public double testSize { get; set; }
        public string scriptOutput { get; set; }
        public string optimizerName { get; set; }
        public double learningRate { get; set; }
        public string idforData { get; set; }
        public string status { get; set; }
        public string taskName { get; set; }
        public string pID { get; set; }
        public DateTime executedAt {get;set;}
    }
}