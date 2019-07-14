'''XML Fetcher'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring

import re
import subprocess
import shutil as files
from os import path, walk, listdir, mkdir
from os.path import isfile, join
from typing import Tuple, List

from src.globals import data
from src.domain.key import Key
from src.domain.usersetting import Usersetting
from src.domain.mod import Mod
from src.util.util import normalizePath

XMLPATTERN = re.compile(r"<Var.+\/>", re.UNICODE)
INPUTPATTERN = re.compile(r"(\[.*\]\s*(IK_.+=\(Action=.+\)\s*)+\s*)+", re.UNICODE)
USERPATTERN = re.compile(r"(\[.*\]\s*(.*=(?!.*(\(|\))).*\s*)+)+", re.UNICODE)
INPUT_XML_PATTERN = r'id="PCInput".+<!--\s*\[BASE_CharacterMovement\]\s*-->'


def fetchMod(modPath: str) -> Tuple[Mod, List[str], List[str]]:
    if isArchive(modPath):
        modPath = extractArchive(modPath)
    if isValidModFolder(modPath):
        return fetchModFromDirectory(modPath)
    raise IOError("not a valid mod")

# tested
def isValidModFolder(modPath: str) -> bool:
    for current_dir, _, _ in walk(modPath):
        if isDataFolder(path.split(current_dir)[1]) \
        and containContentFolder(current_dir):
            return True
    return False

def fetchModFromDirectory(modPath: str) -> Tuple[Mod, List[str], List[str]]:
    mod = Mod(path.split(modPath)[1])
    mod_dirs: List[str] = []
    mod_xmls: List[str] = []
    for current_dir, _, _ in walk(modPath):
        if fetchDataIfRelevantFolder(current_dir, mod):
            mod_dirs.append(normalizePath(current_dir))
        mod_xmls += fetchDataFromRelevantFiles(current_dir, mod)
    return mod, mod_dirs, mod_xmls

# tested
def isDataFolder(directory: str) -> bool:
    return bool(re.match("^mod.*", directory, re.IGNORECASE))

# tested
def containContentFolder(directory: str) -> bool:
    return "content" in (dr.lower() for dr in getAllFoldersFromDirectory(directory))

# tested
def getAllFoldersFromDirectory(directory: str) -> List[str]:
    return [f for f in listdir(directory) if path.isdir(join(directory, f))]

# tested
def getAllFilesFromDirectory(directory: str) -> List[str]:
    return [f for f in listdir(directory) if isfile(join(directory, f))]

# tested
def fetchDataIfRelevantFolder(current_dir: str, mod: Mod) -> bool:
    dirName = path.split(current_dir)[1]
    if containContentFolder(current_dir):
        if isDataFolder(dirName):
            mod.files.append(dirName)
        else:
            mod.dlcs.append(dirName)
        return True
    return False

def fetchDataFromRelevantFiles(current_dir: str, mod: Mod) -> List[str]:
    mod_xmls: List[str] = []
    for file in getAllFilesFromDirectory(current_dir):
        if isMenuXmlFile(file):
            mod.menus.append(file)
            mod_xmls.append(normalizePath(current_dir + "/" + file))
        elif isTxtOrInputXmlFile(file):
            with open(current_dir + "/" + file, 'rb') as file_:
                file_contents = file_.read()
                try:
                    text = file_contents.decode("utf-8")
                except UnicodeError:
                    text = file_contents.decode("utf-16")
                if file == "input.xml":
                    text = fetchRelevantDataFromInputXml(text, mod)
                fetchAllXmlKeys(file, text, mod)
                temp = fetchInputSettings(text)
                if temp:
                    mod.inputsettings += temp
                temp = fetchUserSettings(text)
                if temp:
                    mod.usersettings += temp
    return mod_xmls

# tested
def isMenuXmlFile(file: str) -> bool:
    return bool(re.match(r".+\.xml$", file) and not re.match(r"^input\.xml$", file))

# tested
def isTxtOrInputXmlFile(file: str) -> bool:
    return bool(re.match(r"(.+\.txt)|(input\.xml)$", file))

def fetchRelevantDataFromInputXml(filetext: str, mod: Mod) -> str:
    getHiddenKeysIfExistFromInputXml(filetext, mod)
    searchResult = re.search(INPUT_XML_PATTERN, filetext, re.DOTALL)
    if searchResult:
        return removeXmlComments(searchResult.group(0))
    else:
        return ""

def getHiddenKeysIfExistFromInputXml(filetext: str, mod: Mod) -> None:
    temp = re.search('id="Hidden".+id="PCInput"', filetext, re.DOTALL)
    if (temp):
        hiddentext = temp.group(0)
        hiddentext = removeXmlComments(hiddentext)
        xmlkeys = XMLPATTERN.findall(hiddentext)
        for key in xmlkeys:
            key = removeMultiWhiteSpace(key)
            mod.hidden.append(key)

# tested
def removeXmlComments(filetext: str) -> str:
    filetext = re.sub('<!--.*?-->', '', filetext)
    filetext = re.sub('<!--.*?-->', '', filetext, 0, re.DOTALL)
    return filetext

def fetchAllXmlKeys(file: str, filetext: str, mod: Mod) -> None:
    xmlKeys = fetchXmlKeys(filetext)
    if "hidden" in file and xmlKeys:
        mod.hidden += xmlKeys
    else:
        mod.xmlkeys += xmlKeys

def fetchInputSettings(filetext: str) -> List[Key]:
    found = []
    inputsettings = INPUTPATTERN.search(filetext)
    if (inputsettings):
        res = re.sub(r"(\r\n+)|(\n+)", "\n", inputsettings.group(0))
        arr = filter(lambda s: s != '', str(res).split('\n'))
        context = ''
        for line in arr:
            if line[0] == "[":
                context = line
            else:
                found.append(Key(context, line))
    return found

def fetchUserSettings(filetext: str) -> List[Usersetting]:
    found = []
    usersettings = USERPATTERN.search(filetext)
    if (usersettings):
        res = re.sub(r"(\r\n+)|(\n+)", "\n", usersettings.group(0))
        arr = filter(lambda s: s != '', str(res).split('\n'))
        context = ''
        for line in arr:
            if line[0] == "[":
                context = line
            else:
                found.append(Usersetting(context, line))
    return found

def fetchXmlKeys(filetext: str) -> List[str]:
    found = []
    xmlkeys = XMLPATTERN.findall(filetext)
    for key in xmlkeys:
        key = removeMultiWhiteSpace(key)
        found.append(key)
    return found

# tested
def removeMultiWhiteSpace(key: str) -> str:
    key = re.sub(r"\s+", " ", key)
    return key

# tested
def isArchive(modPath: str) -> bool:
    return bool(re.match(r".+\.(zip|rar|7z)$", path.basename(modPath)))

def extractArchive(modPath: str) -> str:
    extractedDir = data.config.extracted
    if (path.exists(extractedDir)):
        files.rmtree(extractedDir)
    mkdir(extractedDir)
    subprocess.call(r'tools\\7zip\\7z x "' + modPath + '" -o' + '"' + extractedDir + '"')
    return extractedDir
