import subprocess, os, datetime, tkinter, math

from pystray import (
    Icon, 
    Menu, 
    MenuItem
)

from PIL import (
    Image
)

from . import model

class TaskTray():
    def __init__(self):
        self.directory = model.data.directory
        image = Image.open(f"{self.directory.replace(os.path.sep, "/")}/icon/gps.ico")
        menu = Menu(
            MenuItem("表示", model.data.clock.deiconify, default=True),
            MenuItem("ファイルの場所を表示", lambda:subprocess.run(f"explorer {self.directory}",shell = True)), 
            Menu.SEPARATOR, 
            MenuItem("再起動", lambda:self.quit(1)),
            MenuItem("終了", lambda:self.quit(0))
        )
        self.trayIcon=Icon(
            name = "GPS", 
            icon = image, 
            title = "GPS",
            menu =menu
        )
        self.trayIcon.run()
        
    def quit(self, rebootFlag):
        model.data.endFlag = 1
        model.data.rebootFlag = rebootFlag
        self.trayIcon.stop()

class GUI():
    def __init__(self):
        self.directory = model.data.directory
        self.JPTime = datetime.datetime.strptime(f"{model.data.JPDate} {model.data.jpTime}", '%Y/%m/%d %H:%M:%S')

        self.font = "HGP創英角ﾎﾟｯﾌﾟ体"
        model.data.clock = tkinter.Tk()
        model.data.clock.title(u"GPS") # Windowタイトル
        model.data.clock.geometry("1200x600") # Windowサイズ
        model.data.clock.resizable(0,0) # リサイズ禁止
        model.data.clock.iconbitmap(f"{self.directory.replace(os.path.sep, "/")}/icon/gps.ico")
        model.data.clock.withdraw()
        # 図形設定
        size = 600
        self.paint = tkinter.Canvas(model.data.clock, width = size, height = size, background = "black")
        self.paint.place(x=0, y=0)
        self.satelliteData = tkinter.Canvas(model.data.clock, width = size, height = size, background = "black")
        self.satelliteData.place(x=600, y=0)
    
        self.paint.create_oval(5, 5, size - 5, size-5, width = 2,outline = "white")  #フレーム
        self.paint.create_oval(size / 2 - 7, size / 2 - 7, size / 2 + 7, size / 2 + 7, fill="white")  #針の軸

        fontSize = 30
        self.center = size / 2
        self.pdateX = (7.5/5)*self.center
        r = self.center - fontSize - 10
    
        self.paint.create_rectangle(self.pdateX-25 , (6/5)*self.center-20, self.pdateX + 25, (6/5)*self.center + 20, outline = "white" ,width = "3")
        # 文字盤の設定
        for i in range(1, 61): # 1 ～ 60まで
            Θ = (i * ( math.pi / 30 )) - (math.pi / 2) # 中心角
            # 数字の位置
            x = r * math.cos(Θ) + self.center
            y = r * math.sin(Θ) + self.center
        
            # 目盛りの位置
            minX = (self.center-12) * math.cos(Θ) + self.center
            minXStartPoint = (self.center-18) * math.cos(Θ) + self.center
            maxX = (self.center-5) * math.cos(Θ) + self.center
            minY = (self.center-12) * math.sin(Θ) + self.center
            minYStartPoint = (self.center-18) * math.sin(Θ) + self.center
            maxY = (self.center-5) * math.sin(Θ) + self.center
        
            if i % 5 == 0:
                j = i / 5
                self.paint.create_text(x, y, text = str(int(j)), font = (self.font, fontSize),fill = "white" )
                self.paint.create_line(minXStartPoint, minYStartPoint, maxX, maxY, width = 5,fill="white")
            else:
                self.paint.create_line(minX, minY, maxX, maxY, width = 3,fill="white")
        model.data.clock.protocol("WM_DELETE_WINDOW", model.data.clock.withdraw)
        #バックグラウンド処理
        model.data.clock.after(1000, self.disp_time_update)
        model.data.clock.after(1000, self.disp_satellite_update)
        model.data.clock.mainloop() # ずっと表示させる
    
    def disp_satellite_update(self):
        if model.data.endFlag == 0:
            data = ""
            snum = 0
            try:
                self.satelliteData.delete("sData")
                for s, d in model.data.satellite.items():
                    if d["antennaStrength"] != "":
                        data += f"衛星 : {s} | 仰角 : {d["eAngle"]}° 方位角 : {d["azimuth"]}° アンテナ強度 : {d["antennaStrength"]}dB\n\n"
                        snum += 1
            finally:
                fontSize = int(18 - snum / 2)
                self.satelliteData.create_text((3.5/4)*self.center + 2 * fontSize, (4/4)*self.center + 20, text = data, tag="sData",fill="white", font = (self.font, fontSize))
                model.data.clock.after(100, self.disp_satellite_update)
    
    def disp_time_update(self):
        if model.data.endFlag == 0:
            try:
                md = model.data.month[self.JPTime.month - 1]
                weekd = model.data.yobi[self.JPTime.weekday()]
                if self.JPTime.hour > 12:
                    hour = self.JPTime.hour - 12
                    meridiem = "P.M. "
                else:
                    hour = self.JPTime.hour
                    meridiem = "A.M. "
        
                timeText = f"{meridiem}{hour:02}:{self.JPTime.minute:02}:{self.JPTime.second:02}"
        
                secondHandLine = 300 - 15
                secondHandMove = self.JPTime.second * ( math.pi / 30 ) - (math.pi / 2)
                secondHandX =  math.cos(secondHandMove) * secondHandLine
                secondHandY =  math.sin(secondHandMove) * secondHandLine
                minuteHandMove = (self.JPTime.minute + (self.JPTime.second / 60)) * ( math.pi / 30 ) - (math.pi / 2)
                minuteHandX =  math.cos(minuteHandMove) * (secondHandLine * 0.9)
                minuteHandY =  math.sin(minuteHandMove) * (secondHandLine * 0.9)
                hourHandMove = (hour + ((self.JPTime.minute + (self.JPTime.second / 60)) / 60)) * ( math.pi / 6 ) - (math.pi / 2)
                hourHandX =  math.cos(hourHandMove) * (secondHandLine * 0.6)
                hourHandY =  math.sin(hourHandMove) * (secondHandLine * 0.6)

                directionLine = 30

                directionMove = ((math.pi /180) * model.data.direction) - (math.pi / 2)

                directionX = math.cos(directionMove) * (directionLine)
                directionY = math.sin(directionMove) * (directionLine)

                place = f"緯度 : {model.data.latitude}\n経度 : {model.data.longitude}"

                try:
                    self.paint.delete("clock")  #針とカレンダーを消去
                    self.paint.delete("digitalClock")
                    self.paint.delete("Month")
                    self.paint.delete("WD")
                    self.paint.delete("D")
                    self.paint.delete("Y")
                    self.paint.delete("P")
                    self.paint.delete("G")
                    self.paint.delete("A")
                    self.paint.delete("td")
                    self.paint.delete("direc")
                finally:
                    self.paint.create_line( #時針
                        self.center, 
                        self.center, 
                        self.center + hourHandX,
                        self.center + hourHandY, 
                        width = 10, 
                        tag="clock",
                        fill="#33FFCC",
                        arrow=tkinter.LAST,
                        arrowshape=(
                            20, 
                            math.sqrt(20**2 + 10**2), 
                            10
                        )
                    ) 

                    self.paint.create_line( #分針
                        self.center, 
                        self.center, 
                        self.center + 
                        minuteHandX,
                        self.center + minuteHandY, 
                        width = 7, 
                        tag="clock",
                        fill="yellow",
                        arrow=tkinter.LAST,
                        arrowshape=(
                            14, 
                            math.sqrt(14**2 + 7**2), 
                            7
                        )
                    ) 

                    self.paint.create_line( #秒針
                        self.center, 
                        self.center, 
                        self.center + secondHandX,
                        self.center + secondHandY, 
                        width = 5, 
                        tag="clock",
                        fill="red",
                        arrow=tkinter.LAST,
                        arrowshape=(
                            10, 
                            math.sqrt(10**2 + 5**2) , 
                            5
                        )
                    ) 
                    

                    self.paint.create_text( # デジタル時計
                        self.center ,
                        (16/10)*self.center, 
                        text = timeText, 
                        tag="digitalClock",
                        fill="white", 
                        font = (
                            self.font, 
                            22
                        )
                    )

                    self.paint.create_text( # 日にち
                        self.pdateX , 
                        (6/5)*self.center, 
                        text = f"{self.JPTime.day:02}", 
                        tag="D",
                        fill="white", 
                        font = (
                            self.font, 
                            25
                        )
                    ) 

                    self.paint.create_text(
                        (6.5/5)*self.center , 
                        (7/5)*self.center, 
                        text = weekd, 
                        tag="WD",
                        fill="white", 
                        font = (
                            self.font, 
                            25
                        )
                    )

                    self.paint.create_text(
                        (5/5)*self.center , 
                        (6/5)*self.center, 
                        text = md, 
                        tag="Month",
                        fill="white", 
                        font = (
                            self.font, 
                            30
                        )
                    )
                    
                    self.paint.create_text(
                        (4/4)*self.center, 
                        (3/4)*self.center, 
                        text = f"{self.JPTime.year}年", 
                        tag="Y",fill="white", 
                        font = (
                            self.font, 
                            20
                        )
                    )
                    
                    self.paint.create_text(
                        (4/4)*self.center , 
                        (1/4)*self.center + 65, 
                        text = place, 
                        tag="P",
                        fill="white", 
                        font = (
                            self.font, 
                            15
                        )
                    )
                    
                    self.paint.create_text(
                        (1/4)*self.center + 15 , 
                        (0/4)*self.center + 15, 
                        text = f"ジオイド高 : {model.data.geoid}", 
                        tag="G",
                        fill="white", 
                        font = (
                            self.font, 
                            15
                        )
                    )
                    
                    self.paint.create_text(
                        (6/4)*self.center + 15 , 
                        (0/4)*self.center + 15, 
                        text = f"海抜 : {model.data.altitude}", 
                        tag="A",
                        fill="white", 
                        font = (
                            self.font, 
                            15
                        )
                    )
                    
                    self.paint.create_text(
                        (6.5/4)*self.center , 
                        (8/4)*self.center - 15, 
                        text = f"UTC + {model.data.timeDiff}h", 
                        tag="A",
                        fill="white", 
                        font = (
                            self.font, 
                            15
                        )
                    )


                    #方位磁石
                    self.paint.create_line(
                        directionLine*2, 
                        (8/4)*self.center- directionLine*2, 
                        directionLine*2 - directionX, 
                        (8/4)*self.center- directionLine*2 - directionY, 
                        width = 5, 
                        tag="direc",
                        fill="white",
                        arrow=tkinter.LAST,
                        arrowshape=(
                            directionLine, 
                            math.sqrt(directionLine**2 + 7**2) , 
                            7
                        )
                    )

                    self.paint.create_line(
                        directionLine*2, 
                        (8/4)*self.center- directionLine*2, 
                        directionLine*2 + directionX, 
                        (8/4)*self.center - directionLine*2 + directionY,
                        width = 5,
                        tag="direc",
                        fill="red",
                        arrow=tkinter.LAST,
                        arrowshape=(
                            directionLine, 
                            math.sqrt(directionLine**2 + 7**2) , 
                            7
                        )
                    ) 
            
            finally:
                model.data.clock.after(100, self.disp_time_update)
            
        else:
            model.data.clock.quit()