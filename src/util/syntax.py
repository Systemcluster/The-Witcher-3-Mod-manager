'''XML helper functions'''
#pylint: disable=invalid-name,superfluous-parens

import xml.etree.ElementTree as XML

from src.domain.key import Key


def writeAllModsToXMLFile(modlist, file):
    root = XML.Element('installed')
    for mod in modlist.values():
        root = mod.writeToXml(root)
    indent(root)
    tree = XML.ElementTree(root)
    tree.write(file)


def indent(elem, level=0):
    i = "\n" + level * "    "
    if not elem:
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def populateFromXml(mod, root):
    mod.date = root.get('date')
    enabled = root.get('enabled')
    if (enabled == 'True'):
        mod.enabled = True
    else:
        mod.enabled = False
    mod.name = root.get('name')
    prt = root.get('priority')
    if (not prt == 'Not Set'):
        mod.priority = prt
    for data in root.findall('data'):
        mod.files.append(data.text)
    for data in root.findall('dlc'):
        mod.dlcs.append(data.text)
    for data in root.findall('menu'):
        mod.menus.append(data.text)
    for data in root.findall('xmlkey'):
        mod.xmlkeys.append(data.text)
    for data in root.findall('hidden'):
        mod.hidden.append(data.text)
    for data in root.findall('key'):
        key = Key(data.get('context'), data.text)
        mod.inputsettings.append(key)
    for data in root.findall('settings'):
        mod.usersettings.append(data.text)
    mod.loadPriority()


def writeToXml(mod, root):
    xmlData = XML.SubElement(root, 'mod')
    xmlData.set('name', mod.name)
    xmlData.set('enabled', str(mod.enabled))
    xmlData.set('date', mod.date)
    xmlData.set('priority', mod.getPriority())
    if (mod.files):
        for file in mod.files:
            XML.SubElement(xmlData, 'data').text = file
    if (mod.dlcs):
        for dlc in mod.dlcs:
            XML.SubElement(xmlData, 'dlc').text = dlc
    if (mod.menus):
        for menu in mod.menus:
            XML.SubElement(xmlData, 'menu').text = menu
    if (mod.xmlkeys):
        for xml in mod.xmlkeys:
            XML.SubElement(xmlData, 'xmlkey').text = xml
    if (mod.hidden):
        for xml in mod.hidden:
            XML.SubElement(xmlData, 'hidden').text = xml
    if (mod.inputsettings):
        for key in mod.inputsettings:
            ky = XML.SubElement(xmlData, 'key')
            ky.text = str(key)
            ky.set('context', key.context)
    if (mod.usersettings):
        XML.SubElement(xmlData, 'settings').text = mod.usersettings[0]
        return root
