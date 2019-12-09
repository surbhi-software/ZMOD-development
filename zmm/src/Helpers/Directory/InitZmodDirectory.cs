using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using Newtonsoft.Json;
using ZMM.DS;
using ZMM.Helpers.Common;
using ZMM.Models.Payloads;
using ZMM.Models.ResponseMessages;

namespace ZMM.Helpers.ZMMDirectory
{
    public static class InitZmodDirectory
    {
        public static bool ScanDirectoryToSeed()
        {
            bool result = false;
            string fileName, _url, _fullName, fileContent, fileExt = "";
            Console.WriteLine("Dir Loc=" + DirectoryHelper.fileUploadDirectoryPath);
            var zmodDir = new ZmodDirectory(DirectoryHelper.fileUploadDirectoryPath);

            //seed data - subdir, csv, img and json
            #region DATA - SUBDIR
            foreach (var subdir in Directory.GetDirectories(DirectoryHelper.GetDataDirectoryPath()))
            {
                string folderName = Path.GetFileName(subdir);
                string _createdOn = Directory.GetCreationTime(subdir).ToString();
                List<Property> _props = new List<Property>();
                _props.Add(new Property { key = "Subdirectories", value = DirectoryHelper.CountDirectories(subdir).ToString() });
                _props.Add(new Property { key = "Files", value = DirectoryHelper.CountFiles(subdir).ToString() });

                DataResponse newRecord = new DataResponse()
                {
                    Created_on = Directory.GetCreationTime(subdir).ToString(),
                    Edited_on = Directory.GetLastWriteTime(subdir).ToString(),
                    Extension = "",
                    Type = "FOLDER",
                    FilePath = subdir,
                    Id = folderName,
                    MimeType = "",
                    Name = folderName,
                    Properties = _props,
                    DateCreated = Directory.GetCreationTime(subdir)
                };
                //
                DataPayload.Create(newRecord);
            }
            #endregion
            #region DATA - CSV
            foreach (var item in zmodDir.CsvFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = "csv";
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);

                //get properties row and column count
                int[] csvProps = CsvHelper.GetCsvRowColumnCount(item.Value.info.FullName);
                _props.Add(new Property { key = "Number of Rows", value = csvProps[0].ToString() });
                _props.Add(new Property { key = "Number of Columns", value = csvProps[1].ToString() });
                //
                DataResponse newRecord = new DataResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    MimeType = "text/csv",
                    Name = fileName,
                    Properties = _props,
                    Size = item.Value.info.Length,
                    Type = "CSV",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                //
                DataPayload.Create(newRecord);
            }
            #endregion

            #region DATA - IMAGES
            foreach (var item in zmodDir.ImageFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = item.Value.info.Extension.Remove(0, 1);
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName).Replace("\\", "/");

                //get properties
                try
                {
                    // using (var image = new Bitmap(System.Drawing.Image.FromFile(item.Value.info.FullName)))
                    using (var image = new Bitmap(item.Value.info.FullName))
                    {
                        _props.Add(new Property { key = "Width", value = image.Width.ToString() + " px" });
                        _props.Add(new Property { key = "Height", value = image.Height.ToString() + " px" });
                        image.Dispose();
                    }
                    //
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = item.Value.info.CreationTime.ToString(),
                        Edited_on = item.Value.info.LastWriteTime.ToString(),
                        Extension = fileExt,
                        FilePath = item.Value.info.FullName,
                        Id = fileName.Replace($".{fileExt}", ""),
                        MimeType = $"image/{fileExt}",
                        Name = fileName,
                        Properties = _props,
                        Size = item.Value.info.Length,
                        Type = "IMAGE",
                        Url = _url,
                        User = "",
                        DateCreated = item.Value.info.CreationTime
                    };
                    //
                    DataPayload.Create(newRecord);

                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.StackTrace);
                }
            }

            #endregion

            #region DATA - JSON

            foreach (var item in zmodDir.JsonFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = "json";
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);
                fileContent = "";
                //read json file from filestream
                if (!string.IsNullOrEmpty(fileName))
                {
                    using (StreamReader reader = new StreamReader(item.Value.info.FullName))
                    {
                        fileContent = reader.ReadToEnd();
                    }
                }

                //parse
                try
                {
                    if (!string.IsNullOrEmpty(fileContent))
                    {
                        JsonTextReader reader = new JsonTextReader(new StringReader(fileContent));
                        int objCtr = 0;
                        while (reader.Read())
                        {
                            if (reader.TokenType == JsonToken.EndObject) objCtr++;
                        }
                        _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });

                        //
                        DataResponse newRecord = new DataResponse()
                        {
                            Created_on = item.Value.info.CreationTime.ToString(),
                            Edited_on = item.Value.info.LastWriteTime.ToString(),
                            Extension = fileExt,
                            FilePath = item.Value.info.FullName,
                            Id = fileName.Replace($".{fileExt}", ""),
                            MimeType = "application/json",
                            Name = fileName,
                            Properties = _props,
                            Size = item.Value.info.Length,
                            Type = "JSON",
                            Url = _url,
                            User = "",
                            DateCreated = item.Value.info.CreationTime
                        };
                        //
                        DataPayload.Create(newRecord);
                    }
                }
                catch (Exception ex)
                {
                    //TODO: logger
                    string err = ex.StackTrace;
                }

            }

            #endregion

            #region DATA - MP4
            foreach (var item in zmodDir.VideoFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = item.Value.info.Extension.Remove(0, 1);
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);

                //get properties
                try
                {
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = item.Value.info.CreationTime.ToString(),
                        Edited_on = item.Value.info.LastWriteTime.ToString(),
                        Extension = fileExt,
                        FilePath = item.Value.info.FullName,
                        Id = fileName.Replace($".{fileExt}", ""),
                        MimeType = $"video/{fileExt}",
                        Name = fileName,
                        Properties = _props,
                        Size = item.Value.info.Length,
                        Type = "VIDEO",
                        Url = _url,
                        User = "",
                        DateCreated = item.Value.info.CreationTime
                    };
                    //
                    DataPayload.Create(newRecord);
                }
                catch (Exception ex)
                {
                    //TODO: logger
                    string err = ex.StackTrace;
                }

            }
            #endregion

            #region  DATA - TEXT
            foreach (var item in zmodDir.TextFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = item.Value.info.Extension.Remove(0, 1);
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);

                //get properties
                try
                {
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = item.Value.info.CreationTime.ToString(),
                        Edited_on = item.Value.info.LastWriteTime.ToString(),
                        Extension = fileExt,
                        FilePath = item.Value.info.FullName,
                        Id = fileName.Replace($".{fileExt}", ""),
                        MimeType = $"text/plain",
                        Name = fileName,
                        Properties = _props,
                        Size = item.Value.info.Length,
                        Type = "TEXT",
                        Url = _url,
                        User = "",
                        DateCreated = item.Value.info.CreationTime
                    };
                    //
                    DataPayload.Create(newRecord);
                }
                catch (Exception ex)
                {
                    Debug.WriteLine(ex.StackTrace);
                }

            }
            #endregion
            //seed code - py and ipynb
            #region  CODE - PY

            foreach (var item in zmodDir.PyFiles)
            {
                fileName = item.Value.info.Name;
                fileExt = "py";
                _url = DirectoryHelper.GetCodeUrl(item.Value.info.Name);
                CodeResponse newRecord = new CodeResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "PYTHON",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                CodePayload.Create(newRecord);
            }



            #endregion

            #region  CODE - IPYNB
            foreach (var item in zmodDir.IpynbFiles)
            {
                fileName = item.Value.info.Name;
                fileExt = Path.GetExtension(fileName).Remove(0, 1);
                _url = DirectoryHelper.GetCodeUrl(item.Value.info.Name);

                CodeResponse newRecord = new CodeResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "JUPYTER_NOTEBOOK",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                CodePayload.Create(newRecord);
            }
            #endregion

            #region  DATA - R
            foreach (var item in zmodDir.RFiles)
            {
                fileName = item.Value.info.Name;
                fileExt = "r";
                _url = DirectoryHelper.GetCodeUrl(item.Value.info.Name);
                CodeResponse newRecord = new CodeResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = Path.GetFileNameWithoutExtension(fileName),
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "R",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                CodePayload.Create(newRecord);
            }
            #endregion

            //loop of model
            #region  CODE - PMML
            foreach (var item in zmodDir.PmmlFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = "pmml";
                _url = DirectoryHelper.GetModelUrl(item.Value.info.Name);
                //
                ModelResponse newRecord = new ModelResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Deployed = false,
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    Loaded = false,
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "PMML",
                    Url = _url,
                    User = "",
                    Properties = _props,
                    DateCreated = item.Value.info.CreationTime
                };
                ModelPayload.Create(newRecord);
            }



            #endregion

            return result;
        }

        #region scan Data
        public static bool ScanDataDirectory()
        {
            bool result = false;
            string fileName, _url, _fullName, fileContent, fileExt = "";
            Console.WriteLine("Dir Loc=" + DirectoryHelper.fileUploadDirectoryPath);
            var zmodDir = new ZmodDirectory(DirectoryHelper.fileUploadDirectoryPath);

            //seed data - subdir, csv, img and json
            #region DATA - SUBDIR
            foreach (var subdir in Directory.GetDirectories(DirectoryHelper.GetDataDirectoryPath()))
            {
                string folderName = Path.GetFileName(subdir);
                string _createdOn = Directory.GetCreationTime(subdir).ToString();
                List<Property> _props = new List<Property>();
                _props.Add(new Property { key = "Subdirectories", value = DirectoryHelper.CountDirectories(subdir).ToString() });
                _props.Add(new Property { key = "Files", value = DirectoryHelper.CountFiles(subdir).ToString() });

                DataResponse newRecord = new DataResponse()
                {
                    Created_on = Directory.GetCreationTime(subdir).ToString(),
                    Edited_on = Directory.GetLastWriteTime(subdir).ToString(),
                    Extension = "",
                    Type = "FOLDER",
                    FilePath = subdir,
                    Id = folderName,
                    MimeType = "",
                    Name = folderName,
                    Properties = _props,
                    DateCreated = Directory.GetCreationTime(subdir)
                };
                //
                DataPayload.Create(newRecord);
            }
            #endregion
            #region DATA - CSV
            foreach (var item in zmodDir.CsvFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = "csv";
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);

                //get properties row and column count
                int[] csvProps = CsvHelper.GetCsvRowColumnCount(item.Value.info.FullName);
                _props.Add(new Property { key = "Number of Rows", value = csvProps[0].ToString() });
                _props.Add(new Property { key = "Number of Columns", value = csvProps[1].ToString() });
                //
                DataResponse newRecord = new DataResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    MimeType = "text/csv",
                    Name = fileName,
                    Properties = _props,
                    Size = item.Value.info.Length,
                    Type = "CSV",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                //
                DataPayload.Create(newRecord);
            }
            #endregion
            #region DATA - IMAGES
            foreach (var item in zmodDir.ImageFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = item.Value.info.Extension.Remove(0, 1);
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName).Replace("\\", "/");

                //get properties
                try
                {
                    // using (var image = new Bitmap(System.Drawing.Image.FromFile(item.Value.info.FullName)))
                    using (var image = new Bitmap(item.Value.info.FullName))
                    {
                        _props.Add(new Property { key = "Width", value = image.Width.ToString() + " px" });
                        _props.Add(new Property { key = "Height", value = image.Height.ToString() + " px" });
                        image.Dispose();
                    }
                    //
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = item.Value.info.CreationTime.ToString(),
                        Edited_on = item.Value.info.LastWriteTime.ToString(),
                        Extension = fileExt,
                        FilePath = item.Value.info.FullName,
                        Id = fileName.Replace($".{fileExt}", ""),
                        MimeType = $"image/{fileExt}",
                        Name = fileName,
                        Properties = _props,
                        Size = item.Value.info.Length,
                        Type = "IMAGE",
                        Url = _url,
                        User = "",
                        DateCreated = item.Value.info.CreationTime
                    };
                    //
                    DataPayload.Create(newRecord);

                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.StackTrace);
                }
            }

            #endregion
            #region DATA - JSON

            foreach (var item in zmodDir.JsonFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = "json";
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);
                fileContent = "";
                //read json file from filestream
                if (!string.IsNullOrEmpty(fileName))
                {
                    using (StreamReader reader = new StreamReader(item.Value.info.FullName))
                    {
                        fileContent = reader.ReadToEnd();
                    }
                }

                //parse
                try
                {
                    if (!string.IsNullOrEmpty(fileContent))
                    {
                        JsonTextReader reader = new JsonTextReader(new StringReader(fileContent));
                        int objCtr = 0;
                        while (reader.Read())
                        {
                            if (reader.TokenType == JsonToken.EndObject) objCtr++;
                        }
                        _props.Add(new Property { key = "Number of Objects", value = objCtr.ToString() });

                        //
                        DataResponse newRecord = new DataResponse()
                        {
                            Created_on = item.Value.info.CreationTime.ToString(),
                            Edited_on = item.Value.info.LastWriteTime.ToString(),
                            Extension = fileExt,
                            FilePath = item.Value.info.FullName,
                            Id = fileName.Replace($".{fileExt}", ""),
                            MimeType = "application/json",
                            Name = fileName,
                            Properties = _props,
                            Size = item.Value.info.Length,
                            Type = "JSON",
                            Url = _url,
                            User = "",
                            DateCreated = item.Value.info.CreationTime
                        };
                        //
                        DataPayload.Create(newRecord);
                    }
                }
                catch (Exception ex)
                {
                    //TODO: logger
                    string err = ex.StackTrace;
                }

            }

            #endregion
            #region DATA - MP4
            foreach (var item in zmodDir.VideoFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = item.Value.info.Extension.Remove(0, 1);
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);

                //get properties
                try
                {
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = item.Value.info.CreationTime.ToString(),
                        Edited_on = item.Value.info.LastWriteTime.ToString(),
                        Extension = fileExt,
                        FilePath = item.Value.info.FullName,
                        Id = fileName.Replace($".{fileExt}", ""),
                        MimeType = $"video/{fileExt}",
                        Name = fileName,
                        Properties = _props,
                        Size = item.Value.info.Length,
                        Type = "VIDEO",
                        Url = _url,
                        User = "",
                        DateCreated = item.Value.info.CreationTime
                    };
                    //
                    DataPayload.Create(newRecord);
                }
                catch (Exception ex)
                {
                    //TODO: logger
                    string err = ex.StackTrace;
                }

            }
            #endregion
            #region  DATA - TEXT
            foreach (var item in zmodDir.TextFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = item.Value.info.Extension.Remove(0, 1);
                _fullName = item.Value.info.FullName;
                _fullName = _fullName.Substring(_fullName.IndexOf("Data")).Remove(0, 5);
                _url = DirectoryHelper.GetDataUrl(_fullName);

                //get properties
                try
                {
                    DataResponse newRecord = new DataResponse()
                    {
                        Created_on = item.Value.info.CreationTime.ToString(),
                        Edited_on = item.Value.info.LastWriteTime.ToString(),
                        Extension = fileExt,
                        FilePath = item.Value.info.FullName,
                        Id = fileName.Replace($".{fileExt}", ""),
                        MimeType = $"text/plain",
                        Name = fileName,
                        Properties = _props,
                        Size = item.Value.info.Length,
                        Type = "TEXT",
                        Url = _url,
                        User = "",
                        DateCreated = item.Value.info.CreationTime
                    };
                    //
                    DataPayload.Create(newRecord);
                }
                catch (Exception ex)
                {
                    Debug.WriteLine(ex.StackTrace);
                }

            }
            #endregion
            return result;
        }
        #endregion

        #region scan Code
        public static bool ScanCodeDirectory()
        {
            bool result = false;
            string fileName, _url, fileExt = "";
            Console.WriteLine("Dir Loc=" + DirectoryHelper.fileUploadDirectoryPath);
            var zmodDir = new ZmodDirectory(DirectoryHelper.fileUploadDirectoryPath);

            //seed code - py and ipynb
            #region  CODE - PY

            foreach (var item in zmodDir.PyFiles)
            {
                fileName = item.Value.info.Name;
                fileExt = "py";
                _url = DirectoryHelper.GetCodeUrl(item.Value.info.Name);
                CodeResponse newRecord = new CodeResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "PYTHON",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                CodePayload.Create(newRecord);
            }



            #endregion
            #region  CODE - IPYNB
            foreach (var item in zmodDir.IpynbFiles)
            {
                fileName = item.Value.info.Name;
                fileExt = Path.GetExtension(fileName).Remove(0, 1);
                _url = DirectoryHelper.GetCodeUrl(item.Value.info.Name);

                CodeResponse newRecord = new CodeResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "JUPYTER_NOTEBOOK",
                    Url = _url,
                    User = "",
                    DateCreated = item.Value.info.CreationTime
                };
                CodePayload.Create(newRecord);
            }
            #endregion

            return result;
        }
        #endregion

        #region scan Models
        public static bool ScanModelsDirectory()
        {
            bool result = false;
            string fileName, _url, fileExt = "";
            Console.WriteLine("Dir Loc=" + DirectoryHelper.fileUploadDirectoryPath);
            var zmodDir = new ZmodDirectory(DirectoryHelper.fileUploadDirectoryPath);

            //loop of model
            #region  CODE - PMML
            foreach (var item in zmodDir.PmmlFiles)
            {
                List<Property> _props = new List<Property>();
                fileName = item.Value.info.Name;
                fileExt = "pmml";
                _url = DirectoryHelper.GetModelUrl(item.Value.info.Name);
                //
                ModelResponse newRecord = new ModelResponse()
                {
                    Created_on = item.Value.info.CreationTime.ToString(),
                    Deployed = false,
                    Edited_on = item.Value.info.LastWriteTime.ToString(),
                    Extension = fileExt,
                    FilePath = item.Value.info.FullName,
                    Id = fileName.Replace($".{fileExt}", ""),
                    Loaded = false,
                    MimeType = "application/octet-stream",
                    Name = fileName,
                    Size = item.Value.info.Length,
                    Type = "PMML",
                    Url = _url,
                    User = "",
                    Properties = _props,
                    DateCreated = item.Value.info.CreationTime
                };
                ModelPayload.Create(newRecord);
            }



            #endregion

            return result;
        }
        #endregion
    }
}