'''XML Fetcher'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring

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


def fetchMod(modPath):
    if isArchive(modPath):
        modPath = extractArchive(modPath)

    if isValidModFolder(modPath):
        return fetchModFromDirectory(modPath)
    else:
        return Mod()

# tested
def isValidModFolder(modPath):
    for current_dir, _, _ in walk(modPath):
        if isDataFolder(path.split(current_dir)[1]) \
        and containContentFolder(current_dir):
            return True
    return False

def fetchModFromDirectory(modPath):
    mod = Mod(path.split(modPath)[1])
    for current_dir, _, _ in walk(modPath):
        fetchDataIfRelevantFolder(current_dir, mod)
        fetchDataFromRelevantFiles(current_dir, mod)
    return mod

# tested
def isDataFolder(directory):
    return bool(re.match("^mod.*", directory, re.IGNORECASE))

# tested
def containContentFolder(directory):
    return "content" in (dr.lower() for dr in getAllFolersFromDirectory(directory))

# tested
def getAllFolersFromDirectory(directory):
    return [f for f in listdir(directory) if path.isdir(join(directory, f))]

# tested
def getAllFilesFromDirectory(directory):
    return [f for f in listdir(directory) if isfile(join(directory, f))]

# tested
def fetchDataIfRelevantFolder(current_dir, mod):
    dirName = path.split(current_dir)[1]
    if containContentFolder(current_dir):
        if isDataFolder(dirName):
            mod.files.append(dirName)
        else:
            mod.dlcs.append(dirName)

def fetchDataFromRelevantFiles(current_dir, mod):
    for file in getAllFilesFromDirectory(current_dir):
        if isMenuXmlFile(file):
            mod.menus.append(file)
        elif isTxtOrInputXmlFile(file):
            with open(current_dir + "/" + file, 'r') as myfile:
                text = myfile.read()
                if file == "input.xml":
                    text = fetchRelevantDataFromInputXml(text, mod)
                fetchAllXmlKeys(file, text, mod)
                mod.inputsettings.append(fetchInputSettings(text))
                mod.usersettings.append(fetchUserSettings(text))

# tested
def isMenuXmlFile(file):
    return re.match(r".+\.xml$", file) and not re.match(r"^input\.xml$", file)

# tested
def isTxtOrInputXmlFile(file):
    return re.match(r"(.+\.txt)|(input\.xml)$", file)

def fetchRelevantDataFromInputXml(filetext, mod):
    getHiddenKeysIfExistFromInputXml(filetext, mod)
    searchResult = re.search(INPUT_XML_PATTERN, filetext, re.DOTALL)
    return removeXmlComments(searchResult.group(0))

def getHiddenKeysIfExistFromInputXml(filetext, mod):
    temp = re.search('id="Hidden".+id="PCInput"', filetext, re.DOTALL)
    if (temp):
        hiddentext = temp.group(0)
        hiddentext = removeXmlComments(hiddentext)
        xmlkeys = XMLPATTERN.findall(hiddentext)
        for key in xmlkeys:
            key = removeMultiWhiteSpace(key)
            mod.hidden += key

# tested
def removeXmlComments(filetext):
    filetext = re.sub('<!--.*?-->', '', filetext)
    filetext = re.sub('<!--.*?-->', '', filetext, 0, re.DOTALL)
    return filetext

def fetchAllXmlKeys(file, filetext, mod):
    xmlKeys = fetchXmlKeys(filetext)
    if "hidden" in file and xmlKeys:
        mod.hiddenkeys += xmlKeys
    else:
        mod.xmlkeys += xmlKeys

def fetchInputSettings(filetext):
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
def fetchUserSettings(filetext):
    usersettings = USERPATTERN.search(filetext)
    if (usersettings):
        res = re.sub(r"\n+", "\n", usersettings.group(0))
        return str(res)

def fetchXmlKeys(filetext):
    found = []
    xmlkeys = XMLPATTERN.findall(filetext)
    for key in xmlkeys:
        key = removeMultiWhiteSpace(key)
        found += key
    return found

# tested
def removeMultiWhiteSpace(key):
    key = re.sub(r"\s+", " ", key)
    return key

# tested
def isArchive(modPath):
    return re.match(r".+\.(zip|rar|7z)$", path.basename(modPath))

def extractArchive(modPath):
    extractedDir = data.config.extracted
    if (path.exists(extractedDir)):
        files.rmtree(extractedDir)
    mkdir(extractedDir)
    subprocess.call(r'tools\7zip\7z x "' + modPath + '" -o' + '"' + extractedDir + '"')
    return extractedDir
