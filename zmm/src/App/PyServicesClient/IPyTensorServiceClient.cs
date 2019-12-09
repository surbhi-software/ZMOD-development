using System;
using ZMM.Tools.TB;

namespace ZMM.App.PyServicesClient
{
    public interface IPyTensorServiceClient
    {
        TensorBoard GetTensorBoardTool();
    }
}
