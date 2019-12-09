using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Helpers.Extensions;
using ZMM.Models.Payloads;
using ZMM.Models.ResponseMessages;

namespace ZMM.Helpers.Common
{
    public static class ZMKDockerCmdHelper
    {       
        public static Dictionary<string,string> StartCommands = new Dictionary<string, string>()
            {
                {"zmk1", "docker run -d --net=global-zmod-net --ip=\"172.20.0.4\" -p 8000:8000 --name=zmk1 --volumes-from zmm store/softwareag/zementis-modeler-zmk:1.38.1"},
                {"zmk2", "docker run -d --net=global-zmod-net --ip=\"172.20.0.5\" -p 8001:8000 --name=zmk2 --volumes-from zmm store/softwareag/zementis-modeler-zmk:1.38.1"},
                {"zmk3", "docker run -d --net=global-zmod-net --ip=\"172.20.0.6\" -p 8002:8000 --name=zmk3 --volumes-from zmm store/softwareag/zementis-modeler-zmk:1.38.1"}
            }; 
        public static IList<InstanceResponse> GetAllRunningZMK()
        {
            string cmd = "docker ps | awk '{if (NR!=1) {print}}' | awk '{print $1, $2, $NF}' | grep 'store/softwareag/zementis-modeler-zmk'";
            string output ="";
            IList<InstanceResponse> runningZMK = new List<InstanceResponse>();
            //
            try
            {                
                output = cmd.Bash();
                var oArr = output.Split('\n');
                foreach(var line in oArr)
                {
                    if(!string.IsNullOrEmpty(line))
                    {
                        var lineArr = line.Split(' ');
                        List<InstanceProperty> _props = new List<InstanceProperty>();
                        _props.Add(new InstanceProperty { key = "Container Id", value = lineArr[0] });
                        _props.Add(new InstanceProperty { key = "Image", value = lineArr[1] });
                        InstanceResponse newRecord = new InstanceResponse()
                        {
                            Id = lineArr[0],
                            Name = lineArr[2],
                            Type="ZMK",
                            Processes="",
                            Properties = _props
                        };   

                        runningZMK.Add(newRecord);                                        
                    }
                }                
            }
            catch (Exception ex)
            {
                //do nothing
                string error = ex.StackTrace;           
            }

            return runningZMK.OrderBy(i => i.Name).ToList();
        }
    
        public static bool InitZMKInstances()
        {
            bool result=false;            
            try
            {            
               
                //clean up
                KillZMKInstances("zmk1");
                KillZMKInstances("zmk2");
                KillZMKInstances("zmk3");
                //
                StartCommands["zmk1"].Bash();
                Console.WriteLine(StartCommands["zmk1"]);                
            }
            catch(Exception ex)
            {
                //do nothing
                string error = ex.StackTrace; 
            }
            return result;
        }
        public static bool StartZMKInstance(string unassignedZMK)
        {            
            string output ="";
            try
            {
                StartCommands[unassignedZMK].Bash();
                output = $"docker start {unassignedZMK}".Bash();
                Console.WriteLine(output);
                return true;
            }
            catch(Exception ex)
            {
                string error = ex.StackTrace;
                return false;
            }
        }
        public static bool StopZMKInstance(string zmkId)
        {
            Console.WriteLine("stop zmk called");
            string output ="";  
            try
            {
                output = $"docker stop {zmkId}".Bash();                 
                return true;
            }
            catch(Exception ex)
            {
                string error = ex.StackTrace;
                return false;
            }
        }
        
        public static void KillZMKInstances(string id)
        {
            string output ="";            
            try
            {
                output = $"docker rm {id}".Bash(); 
            }
            catch(Exception ex)
            {
                string error = ex.StackTrace;
            }
        }
        public static string GetUnassignedZMKInstance()
        {      
            string[] ids = new string[] { "zmk1", "zmk2", "zmk3" };
            StringBuilder running = new StringBuilder();
            string unassigned = "";
            //
            IList<InstanceResponse> allInstances = GetAllRunningZMK();
            if(allInstances.Count == 0) return "zmk1";
            //
            foreach(var _i in allInstances) running.Append(_i.Name);    
            //
            foreach(var s in ids) 
            {
                if(!running.ToString().Contains(s)) 
                {
                    unassigned = s;
                    break;
                }
            }

            Console.WriteLine($"unassigned = {unassigned}");
            
            return unassigned;
        } 
    
        public static InstanceResponse GetNonDockerZMK()
        {
           
            InstanceResponse newRecord = new InstanceResponse()
            {
                Id = "zmk1",
                Name = "ZMK1",
                Type="ZMK",
                Processes=""
            }; 
            

            return newRecord;
        }
    
    }

}