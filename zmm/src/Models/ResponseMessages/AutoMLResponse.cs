using System;
using System.Collections.Generic;

namespace ZMM.Models.ResponseMessages
{

    public class ListOfModelAccuracy
    {
        public string modelDetail { get; set; }
        public string modelName { get; set; }
        public double score { get; set; }
        public int bestmodel { get; set; }
    }

    public class AutoMLResponse
    {
        public string pID { get; set; }
        public string status { get; set; }
        public string newPMMLFileName { get; set; }
        public string targetVar { get; set; }
        public string problem_type { get; set; }
        public string idforData { get; set; }
        public List<int> shape { get; set; }
        public string taskName { get; set; }
        public List<ListOfModelAccuracy> listOfModelAccuracy { get; set; }
        public string pmmlFilelocation { get; set; }
        public List<object> generationInfo { get; set; }
        public DateTime executedAt { get; set; }
    }
}