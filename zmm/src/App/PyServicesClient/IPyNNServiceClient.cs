using System.Threading.Tasks;

namespace ZMM.App.PyServicesClient
{
    public interface IPyNNServiceClient
    {
        Task<string> GetAllModelList();
        Task<string> PostLoadModel(string filePath);
        Task<string> PostUnloadModel(string modelname);
        Task<string> DeleteLoadedModel(string param);
        Task<string> GetPredictionForImage(string modelname, string filePath);
        Task<string> TrainModel(string requestBody); 
        Task<string> GetAllRunningTask();
        Task<string> GetRunningTaskByTaskName(string taskName);
        Task<string> GetRunningTaskByTaskNameAndId(string taskName, string idforData);
        Task<string> PostEditPmml(string projectId, string filePath);
        Task<string> GetPmmlProperties(string filePath);
        Task<string> DeleteRunningTask(string id);
    }
}