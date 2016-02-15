"""
    def process_manager(self):
        #prints a list of running processes and the number of running processes
        from win32com.client import GetObject
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        print len(processes)
        print [process.Properties_('Name').Value for process in processes]

    def memory_usege(self):
        #prints the memory usage of all processes
        import os
        from wmi import WMI
        w = WMI('.')
        result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
        print int(result[0].WorkingSet)
   """
import psutil
import os
import win32process
import win32api
from ctypes import *
from ctypes.wintypes import *
import ctypes
import time
global SLEEP_TIME_1_5
SLEEP_TIME_1_5=float(1.5)

sys=0
ALL_PROCESS_ACCESS = (0x000F0000L | 0x00100000L | 0xFFF)



class FILETIME(Structure):
    _fields_ = [
        ("dwLowDateTime", DWORD),
        ("dwHighDateTime", DWORD)]
 
    

def GetSystemTimes():
    """
    Uses the function GetSystemTimes() (win32) in order to get the user mode time, kernel mode time and idle mode time
    :return: user time, kernel time and idle time (Dictinary)
    """

    __GetSystemTimes = windll.kernel32.GetSystemTimes
    idleTime, kernelTime, userTime = FILETIME(), FILETIME(), FILETIME()

    success = __GetSystemTimes(

            byref(idleTime),
            byref(kernelTime),
            byref(userTime))

    assert success, ctypes.WinError(ctypes.GetLastError())[1]

    return {
        "idleTime": idleTime.dwLowDateTime,
        "kernelTime": kernelTime.dwLowDateTime,
        "userTime": userTime.dwLowDateTime}


def cpu_utilization():
        global sys
        """
        Returns the total cpu usage

        Source: http://www.codeproject.com/Articles/9113/Get-CPU-Usage-with-GetSystemTimes
        :return: CPU usage (int)
        """

        FirstSystemTimes = GetSystemTimes()
        time.sleep(SLEEP_TIME_1_5)
        SecSystemTimes = GetSystemTimes()

        """
         CPU usage is calculated by getting the total amount of time
         the system has operated since the last measurement
         made up of kernel + user) and the total
         amount of time the process has run (kernel + user).
        """

        usr = SecSystemTimes['userTime'] - FirstSystemTimes['userTime']
        ker = SecSystemTimes['kernelTime'] - FirstSystemTimes['kernelTime']
        idl = SecSystemTimes['idleTime'] - FirstSystemTimes['idleTime']

        sys = usr + ker
        
        return int((sys - idl) * 100 / sys)


def cpu_process_util(pid):
        global sys
        """
        Returns the process usage of CPU

        Source: http://www.philosophicalgeek.com/2009/01/03/determine-cpu-usage-of-current-process-c-and-c/
        :return: Process CPU usage (int)
        """
        try:
            # Creates a process handle
            proc = win32api.OpenProcess(ALL_PROCESS_ACCESS, False, pid )

            FirstProcessTimes = win32process.GetProcessTimes(proc)
            time.sleep(SLEEP_TIME_1_5)
            SecProcessTimes = win32process.GetProcessTimes(proc)

            """
             Process CPU usage is calculated by getting the total amount of time
             the system has operated since the last measurement
             made up of kernel + user) and the total
             amount of time the process has run (kernel + user).
            """

            proc_time_user_prev = FirstProcessTimes['UserTime']
            proc_time_kernel_prev = FirstProcessTimes['KernelTime']

            proc_time_user = SecProcessTimes['UserTime']
            proc_time_kernel = SecProcessTimes['KernelTime']

            proc_usr = proc_time_user - proc_time_user_prev
            proc_ker = proc_time_kernel - proc_time_kernel_prev

            proc_total_time = proc_usr + proc_ker

            return (100 * proc_total_time) /  sys
        except:
            print "Error "+ str(pid)
            return False
    
def proc_name_and_pid():
    #returns a dictionary {pid:name}
    proc_name_and_pid={}
    for proc in psutil.process_iter():
        proc=str(proc)
        a=proc.find("'")
        b=proc.find("=")
        c=proc.find(",")
        """dic_pid_name[proc[b+1:c]] +[ proc[a+1:-2]]"""
        proc_name_and_pid[proc[b+1:c]] =[]
        proc_name_and_pid[proc[b+1:c]] +=[ proc[a+1:-2]]
       # print "PID= "+proc[b+1:c] +" name= "+proc[a+1:-2]
    return proc_name_and_pid




# ---------- Definitions ----------
psapi = ctypes.windll.psapi
Kernel32 = ctypes.windll.Kernel32

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

# ---------- Class ----------
class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    # returns working set and private bytes of process using it's pid
    _fields_ = [("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
                ]


def Adds_ProcessMemUsage_to_dic(proc_name_and_pid):
     #updates the list with mem_struct.WorkingSetSize, mem_struct.PrivateUsage
    for pid in  proc_name_and_pid:
        mem_struct = PROCESS_MEMORY_COUNTERS_EX()
        handle = Kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, int(pid))
        b = psapi.GetProcessMemoryInfo(handle, ctypes.byref(mem_struct), ctypes.sizeof(mem_struct))
        
        proc_name_and_pid[pid]+=[mem_struct.WorkingSetSize]
        proc_name_and_pid[pid]+=[mem_struct.PrivateUsage]
    return proc_name_and_pid



def proc_to_send(proc_name_and_pid):
    #prints the dictionary of risky processes {pid:name,WorkingSetSize,PrivateUsage}
    proc_to_send={}
    for pid in proc_name_and_pid:
        if int(cpu_process_util(int(pid)))>20:
            proc_to_send[pid]=proc_name_and_pid[pid]
    print proc_to_send
def memory_usage_all():
        #returns the memory usage of all processes together
        import os
        from wmi import WMI
        w = WMI('.')
        result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
        return(result[0].WorkingSet)
              

print "the total usage of memory is "+ memory_usage_all()
cpu_utilization()
proc_to_send(Adds_ProcessMemUsage_to_dic(proc_name_and_pid()))
    
    
