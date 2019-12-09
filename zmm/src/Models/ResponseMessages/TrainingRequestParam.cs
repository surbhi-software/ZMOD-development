using System;
using System.Collections.Generic;

public class TrainingRequestParam
{
    public int batchSize { get; set; }
    public int epoch { get; set; }
    public int stepPerEpoch { get; set; }
    public double learningRate { get; set; }
    public string loss { get; set; }
    public List<string> metrics { get; set; }
    public string optimizer { get; set; }
    public double testSize { get; set; }
    public string scriptOutput { get; set; }
    public string recurrence { get; set; }
    public string cronExpression { get; set; }
    public DateTime startDate { get; set; }
    public int startTimeH { get; set; }
    public int startTimeM { get; set; }
    public string problemType { get; set; }
    public string filePath { get; set; }
}