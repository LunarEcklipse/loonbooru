import psutil
import platform
import os

def GetMachineProcessor() -> str:
    return platform.processor()

def GetMachineArchitecture() -> str:
    return str(platform.architecture()[0])

def GetCPUUsagePercent() -> str:
    return f"{str(psutil.cpu_percent())}%"

def GetPythonVersion() -> str:
    pybuild = platform.python_build()
    return f"{platform.python_version()} (Build: {pybuild[0]}, Built on {pybuild[1]})"

def GetMachineOS() -> str:
    return platform.platform()

def GetProcessMemoryUsageMegabytes() -> float:
    process = psutil.Process(os.getpid())
    return round((process.memory_info().rss / 1024 ** 2), 1)
