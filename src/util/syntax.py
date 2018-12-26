'''XML helper functions'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring

import xml.etree.ElementTree as XML


def indent(elem: XML.ElementTree, level: int = 0):
    # pylint: disable=len-as-condition
    i = "\n" + level * "    "
    if len(elem):
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
