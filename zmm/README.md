# **ZMM App** - ASPNET Core 3.0.100 / Angular 7+ project development setup
[License](http://irepo.eur.ad.sag/projects/AIAN/repos/zmm/browse/LICENSE)

A startup **ASP.NET Core 3.0.100 / Angular 7** (Ubuntu 18.04) **project** with an end-to-end login (keycloak integration), data, models, code and tasks implementation.

## INTRODUCING ZMM App
*   Overview [iWiki](https://iwiki.eur.ad.sag/pages/viewpage.action?pageId=551011559)
*   Features logs or raise defect [iTrac] (https://itrac.eur.ad.sag/projects/ZENA/issues/ZENA-466?filter=allopenissues)
*   External identity server as [KeyCloak] (https://accounts.zmod.org)

[Live Demo - ZMM App on Test](https://lambda-quad)

## This application consists of:

*   Pages using Angular7.1.1 and TypeScript
*   RESTful API Backend using ASP.NET Core 3.0.100 MVC Web API
*   Authentication based on OpenID Connect/OAuth 2.0 using KeyCloak
*   API Documentation using Swagger
*   Angular CLI for managing client-side libraries



## Gettting started for Development

*   Clone the [iRepo](http://irepo.eur.ad.sag/projects/AIAN/repos/zmm/browse) on Ubuntu 18.04.
*   Install .Net Core 3.0.100 from [here](https://www.microsoft.com/net/download/dotnet-core)
*   Install your favorite IDE Visual Studio 2017 or Visual Studio Code.
*   If you are using Visual Studio Code then install extension like [C# extension](https://marketplace.visualstudio.com/items?itemName=jchannon.csharpextensions) and [C# Project Solution](https://marketplace.visualstudio.com/items?itemName=fernandoescolar.vscode-solution-explorer)
*   Open folder which has ZMM.sln file; If everything is setup well in system, You can see projects under **Solution Explorer**


## Build Project

*   Once ZMM project opens, please wait for all dependencies ("dotnet restore") to be restored.  
    When using VisualStudio this is automatic, check the output window or status bar to know that the package/dependencies restore process is complete before launching your program for the first time.
*   Configure your development system specific setting in appsettings.Development.json.
    For example, setting for ContentDir and JNB.
*   Open Terminal and go to main folder (which has ZMM.sln), Build all c# projects with command **dotnet build** 
*   Go to ClientApp folder in Terminal. Build ClientApp (Angular 7) with below commands
    1. yarn
    2. yarn build:prod
*   If you get any other errors, consider running manually the steps to build the project and note where the errors occur.  
    Open command prompt and do the below steps:  
    1. run 'dotnet restore' from the two project folders - Restore nuget packages  
    2. run 'npm install' from the project with "ClientApp\\package.json" - Restore npm packages  
    3. run 'npm install yarn -g' to install yarn package.
    
    *"run from the project folder" that means run the commands on the command line from those folders  
    If any step fails, post the error details on the [support forum] for the needed assistance.
*   For help and support post in the [support forum](?). For bug reports open an [issue on iTrac](https://itrac.eur.ad.sag/projects/ZENA/issues/ZENA-466?filter=allopenissues)

## Run Project
*   Once ZMM projects build successfully, You can run project in your system with below command.
    1. go to main folder in Terminal.
    2. run 'dotnet run watch --environment=Development --project=src/App', this will start ZMM app in development profile.
    2. open another terminal and go to directory '/src/App/ClientApp'
    3. run command 'ng serve'

## Test
*   Open Browser and go to "http://localhost:7007", If everything is set and up and running then you will see  login screen.
*   Get logged in with 
    User        : testuser
    Possword    : test
*   Once logged in successfully, It redirects to localhost:7007/data page. 


## Documentation

*   [Overview](https://iwiki.eur.ad.sag/pages/viewpage.action?pageId=551011559)
*   [Achitecute/Design](https://iwiki.eur.ad.sag/pages/viewpage.action?pageId=551011559)



## License

Released under the [License](http://irepo.eur.ad.sag/projects/AIAN/repos/zmm/browse/LICENSE).

[Give your feedback](mailto:generic.zmodsupport@softwareag.com) | [Follow us](?)
