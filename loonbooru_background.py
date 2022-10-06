import threading
import loonboorumysql
from time import sleep

def LaunchBackgroundTaskThread():
    bgtaskthread = threading.Thread(target=BackgroundTasksFunction, daemon=True, name="BGTaskMGR_Master")
    bgtaskthread.start()
    return

def BackgroundTasksFunction():
    while True:
        authcleanthread = threading.Thread(target=loonboorumysql.CleanExpiredAuthTokens, name="BGTaskMGR_DBAuthClean", daemon=True)
        authcleanthread.start()
        sleep(60)
        authcleanthread.join()
        