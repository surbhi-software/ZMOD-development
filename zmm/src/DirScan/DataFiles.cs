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
    public class JsonFileInfo : ZmodFileInfo
    {
        public JsonFileInfo(string path)
        : base(path)
        {
        }
    }
    public class CsvFileInfo : ZmodFileInfo
    {
        public CsvFileInfo(string path)
        : base(path)
        {
        }
    }
    public class ImageDirInfo : ZmodFileInfo
    {
        public ImageDirInfo(string path)
        : base(path)
        {
        }
    }

    public class VideoFileInfo : ZmodFileInfo
    {
        public VideoFileInfo(string path)
        : base(path)
        {
        }
    }

    public class TextFileInfo : ZmodFileInfo
    {
        public TextFileInfo(string path)
        : base(path)
        {
        }
    }
}