'''Generate language source file'''
import os

if os.path.exists("English.ts"):
    os.remove("English.ts")

os.system("pyside6-lupdate ts.pro");
