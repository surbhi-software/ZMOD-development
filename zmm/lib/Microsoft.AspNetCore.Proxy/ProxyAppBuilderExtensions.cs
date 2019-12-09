using System;
using Microsoft.AspNetCore.Proxy;
using Newtonsoft.Json.Linq;

namespace Microsoft.AspNetCore.Builder
{
    //
    // Summary:
    //     Extension methods to add proxy capabilities in Middleware
    public static class ProxyAppBuilderExtensions
    {
        //
        // Summary:
        //     Adds the Microsoft.AspNetCore.Proxy to the specified
        //     Microsoft.AspNetCore.Builder.IApplicationBuilder, which enables proxy capabilities.
        //
        // Parameters:
        //   app:
        //     The Microsoft.AspNetCore.Builder.IApplicationBuilder to add the middleware to.
        //
        // Returns:
        //     A reference to this instance after the operation has completed.
        public static IApplicationBuilder UseProxy(this IApplicationBuilder app)
        {
            Maps.Do(ref app);
            return app;
        }
    }
}