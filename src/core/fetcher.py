'''XML Fetcher'''
#pylint: disable=invalid-name,superfluous-parens

import re
import subprocess
import shutil as files
from os import path, walk, listdir, mkdir
from os.path import isfile, join

from src.globals import data
from src.domain.key import Key
from src.domain.mod import Mod

XMLPATTERN = re.compile(r"<Var.+\/>", re.UNICODE)
INPUTPATTERN = re.compile(r"(\[.*\]\s*(IK_.+=\(Action=.+\)\s*)+\s*)+", re.UNICODE)
USERPATTERN = re.compile(r"(\[.*\]\s*(.*=(?!.*(\(|\))).*\s*)+)+", re.UNICODE)
INPUT_XML_PATTERN = r'id="PCInput".+<!--\s*\[BASE_CharacterMovement\]\s*-->'


class Fetcher:

    def fetch(self, modPath):
        if self.isArchive(modPath):
            modPath = self.extract(modPath)

        if self.isValidModFolder(modPath):
            return self.fetchModFromDirectory(modPath)
        else:
            return Mod()

    # tested
    def isValidModFolder(self, modPath):
        for current_dir, _, _ in walk(modPath):
            if self.isDataFolder(path.split(current_dir)[1]) \
            and self.containContentFolder(current_dir):
                return True
        return False

    def fetchModFromDirectory(self, modPath):
        mod = Mod(path.split(modPath)[1])
        for current_dir, _, _ in walk(modPath):
            self.fetchDataIfRelevantFolder(current_dir, mod)
            self.fetchDataFromRelevantFiles(current_dir, mod)
        return mod

    # tested
    def isDataFolder(self, directory):
        return bool(re.match("^mod.*", directory, re.IGNORECASE))

    # tested
    def containContentFolder(self, directory):
        return "content" in (dr.lower() for dr in self.getAllFolersFromDirectory(directory))

    # tested
    def getAllFolersFromDirectory(self, directory):
        return [f for f in listdir(directory) if path.isdir(join(directory, f))]

    # tested
    def getAllFilesFromDirectory(self, directory):
        return [f for f in listdir(directory) if isfile(join(directory, f))]

    # tested
    def fetchDataIfRelevantFolder(self, current_dir, mod):
        dirName = path.split(current_dir)[1]
        if self.containContentFolder(current_dir):
            if self.isDataFolder(dirName):
                mod.files.append(dirName)
            else:
                mod.dlcs.append(dirName)

    def fetchDataFromRelevantFiles(self, current_dir, mod):
        for file in self.getAllFilesFromDirectory(current_dir):
            if self.isMenuXmlFile(file):
                mod.menus.append(file)
            elif self.isTxtOrInputXmlFile(file):
                with open(current_dir + "/" + file, 'r') as myfile:
                    text = myfile.read()
                    if file == "input.xml":
                        text = self.fetchRelevantDataFromInputXml(text, mod)
                    self.fetchAllXmlKeys(file, text, mod)
                    mod.inputsettings.append(self.fetchInputSettings(text))
                    mod.usersettings.append(self.fetchUserSettings(text))

    # tested
    def isMenuXmlFile(self, file):
        return re.match(r".+\.xml$", file) and not re.match(r"^input\.xml$", file)

    # tested
    def isTxtOrInputXmlFile(self, file):
        return re.match(r"(.+\.txt)|(input\.xml)$", file)

    def fetchRelevantDataFromInputXml(self, filetext, mod):
        self.getHiddenKeysIfExistFromInputXml(filetext, mod)
        searchResult = re.search(INPUT_XML_PATTERN, filetext, re.DOTALL)
        return self.removeXmlComments(searchResult.group(0))

    def getHiddenKeysIfExistFromInputXml(self, filetext, mod):
        temp = re.search('id="Hidden".+id="PCInput"', filetext, re.DOTALL)
        if (temp):
            hiddentext = temp.group(0)
            hiddentext = self.removeXmlComments(hiddentext)
            xmlkeys = XMLPATTERN.findall(hiddentext)
            for key in xmlkeys:
                key = self.removeMultiWhiteSpace(key)
                mod.hidden += key

    # tested
    def removeXmlComments(self, filetext):
        filetext = re.sub('<!--.*?-->', '', filetext)
        filetext = re.sub('<!--.*?-->', '', filetext, 0, re.DOTALL)
        return filetext

    def fetchAllXmlKeys(self, file, filetext, mod):
        xmlKeys = self.fetchXmlKeys(filetext)
        if "hidden" in file and xmlKeys:
            mod.hiddenkeys += xmlKeys
        else:
            mod.xmlkeys += xmlKeys

    def fetchInputSettings(self, filetext):
        found = []
        inputsettings = INPUTPATTERN.search(filetext)
        if (inputsettings):
            res = re.sub(r"\n+", "\n", inputsettings.group(0))
            arr = str(res).split('\n')
            if '' in arr:
                arr.remove('')
            context = ''
            for key in arr:
                if key[0] == "[":
                    context = key
                else:
                    newkey = Key(context, key)
                    found += newkey
        return found

    # tested
    def fetchUserSettings(self, filetext):
        usersettings = USERPATTERN.search(filetext)
        if (usersettings):
            res = re.sub(r"\n+", "\n", usersettings.group(0))
            return str(res)

    def fetchXmlKeys(self, filetext):
        found = []
        xmlkeys = XMLPATTERN.findall(filetext)
        for key in xmlkeys:
            key = self.removeMultiWhiteSpace(key)
            found += key
        return found

    # tested
    def removeMultiWhiteSpace(self, key):
        key = re.sub(r"\s+", " ", key)
        return key

    # tested
    def isArchive(self, modPath):
        return re.match(r".+\.(zip|rar|7z)$", path.basename(modPath))

    def extract(self, modPath):
        extractedDir = data.config.extracted
        if (path.exists(extractedDir)):
            files.rmtree(extractedDir)
        mkdir(extractedDir)
        subprocess.call(r'tools\7zip\7z x "' + modPath + '" -o' + '"' + extractedDir + '"')
        return extractedDir
