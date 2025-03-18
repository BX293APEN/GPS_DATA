from lib import model, template, view
import threading, subprocess, os

def main():
    with view.SatelliteDataRead() as s:
        s.rx_data_read()

if __name__ == "__main__":
    serialRead = threading.Thread(target=main)
    serialRead.start()
    trayThread = threading.Thread(target=template.TaskTray)
    trayThread.start()
    template.GUI()
    serialRead.join()
    trayThread.join()
    if model.data.rebootFlag == 1:
        subprocess.run(f"python {os.path.dirname(os.path.abspath(__file__))}\\exeGPS.pyw",shell = True)