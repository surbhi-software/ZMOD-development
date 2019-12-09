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

    public class ZmodFileInfo
    {
        public FileInfo info { get; set; }        

        public ZmodFileInfo(string path)
        {
            info = new FileInfo(path);  // on thousands of files, this takes forever
        }
        public ZmodFileInfo()
        {
        }
    }
}
