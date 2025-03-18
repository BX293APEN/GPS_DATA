from ctypes import windll
import os
def runas(path):
    windll.shell32.ShellExecuteW(
        None,
        "runas",
        "pythonw", # コンソール出したくないならpythonw
        path, # 実行したいスクリプト
        None,
        0
    )

if __name__ == "__main__":
    runas(f"{os.path.dirname(os.path.abspath(__file__))}\\GPS.pyw")