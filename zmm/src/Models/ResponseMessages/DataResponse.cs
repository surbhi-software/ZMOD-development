using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ZMM.Models.ResponseMessages
{
    public class DataResponse : BaseResponse
    {        
        public DateTime DateCreated{get; set;}
    }
}