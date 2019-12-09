using System;
using System.Collections.Generic;
using Xunit;
using ZMM.Models.Payloads;
using ZMM.Models.ResponseMessages;

namespace ZMM.Models.Tests
{
    public class ModelsTest
    {
        #region Test for Data
        [Fact]
        public void TestCreateDataPayload()
        {
            List<Property> _prop = new List<Property>();
            DataResponse newRecord = new DataResponse()
            {
                Id = "HelloData",
                Name = "Hello.png",
                User = "",
                Created_on = DateTime.Now.ToString(),
                Edited_on = DateTime.Now.ToString(),
                Extension = ".png",
                MimeType = "application/image",
                Size = 111,
                Type = "IMAGE",
                Url = "http://localhost/uploads/data/Hello.png",
                FilePath = "",
                Properties = _prop
            };

            DataResponse createdRecord = DataPayload.Create(newRecord);

            Assert.Equal(newRecord, createdRecord);
        }

        [Fact]
        public void TestReadDataPayload()
        {
            List<DataResponse> _data = new List<DataResponse>();
            _data = DataPayload.Get();
            //Console.WriteLine(_data);
            Assert.NotNull(_data);
        }

        [Fact]
        public void TestUpdateDataPayload()
        {
            List<Property> _prop = new List<Property>();
            List<DataResponse> _data = new List<DataResponse>();
            TestCreateDataPayload();
            _data = DataPayload.Get();
            _prop.Add(new Property { key = "width", value = "200px" });
            DataResponse updateRecord = new DataResponse()
            {
                Id = "Hello",
                Name = "Hello.png",
                User = "",
                Created_on = DateTime.Now.ToString(),
                Edited_on = DateTime.Now.ToString(),
                Extension = ".png",
                MimeType = "application/image",
                Size = 111,
                Type = "IMAGE",
                Url = "http://localhost/uploads/data/Hello.png",
                FilePath = "",
                Properties = _prop
            };
            
            DataResponse updated = DataPayload.Update(updateRecord);
            Assert.NotEqual(_data[0].Properties, updateRecord.Properties);

        }

        /*

        [Fact]
        public void TestDeleteDataPayload()
        {
             Need to resolve this
            List<DataResponse> _model = new List<DataResponse>();
            TestCreateDataPayload();
            _model = DataPayload.Get();
            Assert.NotNull(_model);
            //
            bool isDeleted = DataPayload.Delete("HelloData");
            Assert.True(isDeleted);
            //
            _model = DataPayload.Get();
            Assert.True(_model.Count == 0);
            

    }
    
    */
        #endregion

        #region Test for Code       
        [Fact]
        public void TestCreateCodePayload()
        {
            List<Property> _prop = new List<Property>();
            CodeResponse newRecord = new CodeResponse()
            {
                Id = "HelloCode",
                Name = "Hello.py",
                User = "",
                Created_on = DateTime.Now.ToString(),
                Edited_on = DateTime.Now.ToString(),
                Extension = ".py",
                MimeType = "application/image",
                Size = 111,
                Type = "PY",
                Url = "http://localhost/uploads/Code/Hello.png",
                FilePath = "some Path",
                Properties = _prop
            };

            CodeResponse createdRecord = CodePayload.Create(newRecord);

            Assert.Equal(newRecord, createdRecord);
        }

        [Fact]
        public void TestReadCodePayload()
        {
            List<CodeResponse> _Code = new List<CodeResponse>();
            _Code = CodePayload.Get();           
            Assert.NotNull(_Code);
        }

        [Fact]
        public void TestUpdateCodePayload()
        {
            List<Property> _prop = new List<Property>();
            List<CodeResponse> _Code = new List<CodeResponse>();
            TestCreateCodePayload();
            _Code = CodePayload.Get();
            _prop.Add(new Property { key = "new_prop", value = "200" });
            CodeResponse updateRecord = new CodeResponse()
            {
                Id = "HelloCode",
                Name = "HelloCode.py",
                User = "",
                Created_on = DateTime.Now.ToString(),
                Edited_on = DateTime.Now.ToString(),
                Extension = ".png",
                MimeType = "application/image",
                Size = 111,
                Type = "PY",
                Url = "http://localhost/uploads/Code/HelloCode.py",
                FilePath = "",
                Properties = _prop
            };

            CodeResponse updated = CodePayload.Update(updateRecord);
            Assert.NotEqual(_Code[0].Properties, updateRecord.Properties);

        }

        [Fact]
        public void TestDeleteCodePayload()
        {
            List<CodeResponse> _model = new List<CodeResponse>();
            TestCreateCodePayload();
            _model = CodePayload.Get();
            Assert.NotNull(_model);
            //
            bool isDeleted = CodePayload.Delete("HelloCode");
            Assert.True(isDeleted);
            //
            _model = CodePayload.Get();
            Assert.True(_model.Count == 0);
        }

        #endregion

        #region Test for Model
        [Fact]
        public void TestCreateModelpayload()
        {
            List<Property> _prop = new List<Property>();
            List<ModelResponse> _model = new List<ModelResponse>();
            _model = ModelPayload.Get();           
            ModelResponse newRecord = new ModelResponse()
            {
                Id = "HelloModel",
                Name = "Hello.pmml",
                User = "",
                Created_on = DateTime.Now.ToString(),
                Edited_on = DateTime.Now.ToString(),
                Extension = ".png",
                MimeType = "application/image",
                Size = 111,
                Type = "PMML",
                Url = "http://localhost/uploads/data/Hello.png",
                FilePath = "",
                Loaded = false,
                Deployed = false,
                Properties = _prop
            };

            ModelResponse createdRecord = ModelPayload.Create(newRecord);
            Assert.Equal(newRecord, createdRecord);
        }

        [Fact]
        public void TestReadModelPayload()
        {
            List<ModelResponse> _model = new List<ModelResponse>();
            TestCreateModelpayload();
            _model = ModelPayload.Get();            
            Assert.NotNull(_model);
        }


        [Fact]
        public void TestUpdateModelpayload()
        {
            List<Property> _prop = new List<Property>();
            List<ModelResponse> _model = new List<ModelResponse>();
            TestCreateModelpayload();
            _model = ModelPayload.Get();
            _prop.Add(new Property { key = "width", value = "200px" });
            ModelResponse updateRecord = new ModelResponse()
            {
                Id = "HelloModel",
                Name = "Hello.pmml",
                User = "",
                Created_on = DateTime.Now.ToString(),
                Edited_on = DateTime.Now.ToString(),
                Extension = ".png",
                MimeType = "application/image",
                Size = 111,
                Type = "IMAGE",
                Url = "http://localhost/uploads/data/Hello.png",
                FilePath = "",
                Loaded = false,
                Deployed = false,
                Properties = _prop
            };

            Console.WriteLine(_model[0].Properties);
            Console.WriteLine(updateRecord.Properties);
            ModelResponse updated = ModelPayload.Update(updateRecord);
            Assert.NotEqual(_model[0].Properties, updateRecord.Properties);
        }

        /* Need to Resolve this
        [Fact]
        public void TestDeleteModelPayload()
        {
            List<ModelResponse> _model = new List<ModelResponse>();
            TestCreateModelpayload();
            _model = ModelPayload.Get();
            Assert.NotNull(_model);
            //
            bool isDeleted = ModelPayload.Delete("HelloModel");
            Assert.True(isDeleted);
            //
            _model = ModelPayload.Get();
            Assert.True(_model.Count == 0);
        }

        
        */
        #endregion //models


    }
}
