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

    public class CodeFileInfo : ZmodFileInfo
    {
        public CodeFileInfo(string path)
        : base(path)
        {
        }
        public CodeFileInfo()
        {

        }
    }
    public class CodeFile : TextFile
    {
        public CodeFile(string name)
            : base(name)
        {

        }
    }
    public class PyFileInfo : ZmodFileInfo
    {
        public PyFileInfo(string path)
        : base(path)
        {
        }
        public PyFileInfo()
        {
        }
    }
    public class PyFile : CodeFile
    {
        public PyFile(string name)
        : base(name)
        {
        }
    }
    public class IpynbFileInfo : ZmodFileInfo
    {
        public IpynbFileInfo(string path)
        : base(path)
        {
        }
        public IpynbFileInfo()
        {

        }
    }
    public class IpynbFile : CodeFile
    {
        public IpynbFile(string name)
        : base(name)
        {
        }
    }
    
    public class RFileInfo : ZmodFileInfo
    {
        public RFileInfo(string path)
        : base(path)
        {
        }
        public RFileInfo()
        {
        }
    }
}
