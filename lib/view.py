import serial, time, datetime
from serial.tools import list_ports

import win32api

from . import model

class SendUARTData:
    def check_serial(self):
        return [info.device for info in list_ports.comports()]
    
    def __init__(self, port = "COM4", baudrate = 115200, timeout = 0.1, setdtr = 1, encoding = "UTF-8", dispCOMPort = False):
        if dispCOMPort:
            print(f"USEABLE : {self.check_serial()}")

        self.serialPort = serial.Serial(
            port = port, 
            baudrate = baudrate,
            timeout = timeout,
        )
        self.encoding = encoding
        self.setdtr = setdtr
        if self.setdtr == 0:
            self.serialPort.dtr=False
        
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.serialPort.close()
        
    def tx_uart_data(self, data:str):
        self.serialPort.write(f"{data}\n".encode(self.encoding))
    
    def rx_uart_dataln(self):
        ans = self.serialPort.read().decode(self.encoding, "ignore")
        while ans != "":
            if (ans.count("\n") > 0 or 
                ans.count("\r") > 0):
                ans = ans.replace("\r", "\n").replace(chr(0x00), "").split("\n")
                for a in ans:
                    model.data.rxData += f"{a}\n"
                return model.data.rxData
        
            elif ans == "\b":
                if len(model.data.rxData) > 0:
                    model.data.rxData = model.data.rxData[:-1]
                else:
                    model.data.rxData = ""
            else:
                model.data.rxData += ans
            
            ans = self.serialPort.read().decode(self.encoding, "ignore")
        return ""
    
    def reset_dtr(self):
        if self.setdtr == 0:
            self.serialPort.dtr=True
            time.sleep(1)
            self.serialPort.dtr=False

class SatelliteDataRead(SendUARTData):
    def __init__(self):
        super().__init__(
            port = model.data.config["port"],
            baudrate = 115200, 
            timeout = 0.1, 
            setdtr = 1,
            encoding = "UTF-8",
            dispCOMPort = False
        )

    def rx_data_read(self):
        rxData = ""
        while model.data.endFlag == 0:
            rxData = self.rx_uart_dataln()
            model.data.rxData = ""
            if rxData.count("\n") >0:
                for d in rxData.split("\n"):
                    if d.count(",") > 0:
                        gpsData = d.split(",")
                        #print(d)
                        if gpsData[0] == "$GPGGA" and gpsData[1] != "":
                            # 時刻情報
                            utcTimeData = list(gpsData[1])
                            model.data.utcTime = f"{utcTimeData[0]}{utcTimeData[1]}:{utcTimeData[2]}{utcTimeData[3]}:{utcTimeData[4]}{"".join(utcTimeData[5:])}"
                            self.UTCTime = datetime.datetime.strptime(f"{model.data.UTCdate} {model.data.utcTime}", '%Y/%m/%d %H:%M:%S.%f')
                            try:
                                # Windows 時刻合わせ(UTCで設定) ※管理者権限必須
                                win32api.SetSystemTime( 
                                    self.UTCTime.year,
                                    self.UTCTime.month,
                                    self.UTCTime.weekday(),
                                    self.UTCTime.day,
                                    self.UTCTime.hour,
                                    self.UTCTime.minute,
                                    self.UTCTime.second,
                                    self.UTCTime.microsecond//1000
                                )
                            except:
                                print("管理者権限で実行してください")
                            
                            model.data.JPN = self.UTCTime + datetime.timedelta(hours = model.data.timeDiff)
                            #位置情報
                            try:
                                latitude = f"{int(float(gpsData[2]) // 100)}°{(float(gpsData[2]) % 100)}'"
                                model.data.latitude = f"{latitude} {gpsData[3]}"
                                longitude = f"{int(float(gpsData[4]) // 100)}°{(float(gpsData[4]) % 100)}'"
                                model.data.longitude = f"{longitude} {gpsData[5]}"
                                model.data.geoid = f"{gpsData[11]}{gpsData[12].lower()}"
                                model.data.altitude = f"{gpsData[9]}{gpsData[10].lower()}"
                            except:
                                pass
                        elif gpsData[0] == "$GPRMC":
                            UTCdate = list(str(gpsData[9]))
                            model.data.UTCdate = f"20{UTCdate[4]}{UTCdate[5]}/{UTCdate[2]}{UTCdate[3]}/{UTCdate[0]}{UTCdate[1]}"
                            if gpsData[8] != "":
                                model.data.direction = float(gpsData[8])
                        elif gpsData[0] == "$GPVTG":
                            if gpsData[1] != "":
                                model.data.direction = float(gpsData[1])
                            """
                            if gpsData[3] != "":
                                model.data.direction = float(gpsData[3])
                            """
                        elif gpsData[0] == "$GPGSV":
                            try:
                                for it in range(4, len(gpsData)):
                                    i = (it - 4) % 4
                                    if gpsData[it].count("*"):
                                        gpsData[it] = gpsData[it].split("*")[0]
                                    if i == 3:
                                        model.data.satellite[gpsData[it - 3]] = {}
                                        model.data.satellite[gpsData[it - 3]]["eAngle"] = gpsData[it - 2] # 仰角[°]
                                        model.data.satellite[gpsData[it - 3]]["azimuth"] = gpsData[it - 1] # 方位角[°]
                                        model.data.satellite[gpsData[it - 3]]["antennaStrength"] = gpsData[it] # アンテナ強度[dB]
                            except Exception as e:
                                print(e)
        
            time.sleep(0.0001)

# if __name__ == "__main__":
#     with SendUARTData(setdtr = 0) as serial:
#         time.sleep(2)
#         serial.tx_uart_data("pi color 0")
#         while True:
#             rxData = serial.rx_uart_data()
#             if rxData != "":
#                 print(rxData, end = "")