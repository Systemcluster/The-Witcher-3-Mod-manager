'''Generate language source file'''
import os

if os.path.exists("English.ts"):
    os.remove("English.ts")

os.system("pylupdate5 -translate-function TRANSLATE ts.pro");
