using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.OAuth.Claims;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;
using System.Text.Json.Serialization;


namespace ZMM.Authorizations.Claims
{
    public class CustomClaimAction: Microsoft.AspNetCore.Authentication.OAuth.Claims.ClaimAction
    {
        /// <summary>
        /// Creates a new CustomClaimAction.
        /// </summary>
        /// <param name="claimType">The value to use for Claim.Type when creating a Claim.</param>        
        /// <param name="valueType">The value to use for Claim.ValueType when creating a Claim.</param>
        /// <param name="jsonKey">The top level key to look for in the json user data.</param>
        /// <param name="jsonKeyDefaultValue">The default value to use if Key is not found.</param>
        public CustomClaimAction(string claimType, string valueType, string jsonKey, string defaultJsonKeyValue) : base(claimType, valueType)
        {
            //Console.WriteLine("Test");
            JsonKey = jsonKey;
            DefaultKeyValue = defaultJsonKeyValue;
        }

        /// <summary>
        /// The top level key to look for in the json user info data.
        /// </summary>
        public string JsonKey { get; }
        public string DefaultKeyValue { get; }
        

        public override void Run(JsonElement userData, ClaimsIdentity identity, string issuer)
        {
            try
            {
                JObject temp = new JObject(userData.ToString());
                var values = temp?[JsonKey];
                if (!(values is JArray)) return;

                foreach (var value in values)
                {
                    identity.AddClaim(new Claim(ClaimType, value.ToString(), ValueType, issuer));
                }
            }
            catch(Exception ex)
            {
                string err = ex.StackTrace;
               identity.AddClaim(new Claim(ClaimType, DefaultKeyValue, ValueType, issuer));
            }
        }
    }
}