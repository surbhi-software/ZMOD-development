using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.AspNetCore.Http;
using ZMM.Models.ResponseMessages;
using ZMM.Models.Storage;

namespace ZMM.Models.Payloads
{
    public static class ZSSettingPayload
    {
        #region CreateOrUpdate
        public static ZSSettingResponse CreateOrUpdate(ZSSettingResponse newRecord)
        {
            var existingSettings = GetSettingsByUser(newRecord.ZmodId);
            ZSSettingResponse response = new ZSSettingResponse();
            if (existingSettings.Count > 0)
            {
                bool result = GlobalStorage.ZSSettingStorage.TryRemove(newRecord.ZmodId, out response);
                if (result) GlobalStorage.ZSSettingStorage.TryAdd(newRecord.ZmodId, newRecord);
            }
            else
            {
                //add new
                GlobalStorage.ZSSettingStorage.TryAdd(newRecord.ZmodId, newRecord);
            }

            return newRecord;
        }
        #endregion

        #region GetSettingsByUser
        public static List<ZSSettingResponse> GetSettingsByUser(string zmodId)
        {
            List<ZSSettingResponse> _settings = new List<ZSSettingResponse>();
            if (GlobalStorage.ZSSettingStorage != null)
            {
                foreach (var item in GlobalStorage.ZSSettingStorage)
                {
                    if (item.Key == zmodId)
                    {
                        _settings.Add(item.Value);
                        break;
                    }
                }
            }

            return _settings;
        }
        #endregion

        #region GetInfo - url,uname,pass
        public static Tuple<string, string, string> GetUserInfo(string zmodId)
        {
            string url = "", uname = "", pass = "";
            // var qry = GetSettingsByUser(zmodId)
            // .Where(i => i.Settings.Any(s => s.selected == true))
            // .SelectMany(col => col.Settings.Select(s => new { s.url, s.username, s.password }));

            foreach (var _ in GetSettingsByUser(zmodId))
            {
                foreach (var record in _.Settings)
                {
                    if ((record.selected == true) && (record.type == "ZS"))
                    {
                        url = record.url;
                        uname = record.username;
                        pass = record.password;
                        break;
                    }
                }
            }

            return new Tuple<string, string, string>(url, uname, pass);
        }
        #endregion

        #region Get user email
        public static string GetUserNameOrEmail(HttpContext context)
        {
            Dictionary<string, string> Result = new Dictionary<string, string>();
            foreach (System.Security.Claims.Claim Cl in context.User.Claims)
            {
                if (Cl.Type.Equals("name")) Result["name"] = Cl.Value;
                else if (Cl.Type.Equals("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")) Result["email"] = Cl.Value;
                else if (Cl.Type.Equals("role")) Result["role"] = Cl.Value;
            }
            return Result["email"];
        }
        #endregion


    }
}