import os, json, datetime
class Data:
    def __init__(self, path):
        self.rxData     = ""
        self.endFlag    = 0
        self.utcTime    = "0:0:0"
        self.UTCdate    = "2024/01/01"
        self.JPN        = datetime.datetime.strptime("2024/01/01 0:0:0.0", '%Y/%m/%d %H:%M:%S.%f')
        self.latitude   = ""
        self.longitude  = ""
        self.yobi       = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        self.month      = ["Jan.(睦月)" ,"Feb.(如月)" ,"Mar.(弥生)","Apr.(卯月)","May.(皐月)","Jun.(水無月)","Jul.(文月)","Aug.(葉月)","Sep.(長月)","Oct.(神無月)", "Nov.(霜月)", "Dec.(師走)"]
        self.satellite  = {}
        self.geoid      = ""
        self.altitude   = ""
        self.direction  = 0
        self.timeDiff   = 9
        self.directory  = os.path.dirname(path)
        self.clock      = None

        with open(f"{self.directory}\\config\\config.json", "r", encoding="UTF-8") as configFile:
            self.config = json.loads(configFile.read())

        # os.path.dirname(os.path.abspath(__file__))    : このファイルのフォルダ
        # os.getcwd()                                   : メインファイルのフォルダ

data = Data(os.path.dirname(os.path.abspath(__file__)))
