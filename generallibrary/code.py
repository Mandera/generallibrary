
import pyperclip
import os
import inspect
import re
import pandas as pd

from generallibrary.diagram import TreeDiagram
from generallibrary.object import initBases


def clipboard_copy(s):
    """ Copy a string to clipboard.
        Rudely tries to installs xclip on linux if it fails. """
    def _call():
        return pyperclip.copy(s)

    try:
        _call()
    except pyperclip.PyperclipException:
        os.system("sudo apt-get install xclip")
        _call()


def clipboard_get():
    """ Get clipboard string. """
    return pyperclip.paste()


@initBases
class CodeLine(TreeDiagram):
    """ Tool to help with printing code line by line.
        Todo: Search for CodeGen and replace. """
    indent_str = " " * 4

    def __init__(self, code_str, space_before=0, space_after=0, parent=None):
        self.code_str = code_str
        self.space_before = space_before
        self.space_after = space_after

    def generate(self):
        """ Generate a list of formatted code lines by iterating stored _Line instances. """
        lines = ["# -------------------- GENERATED CODE --------------------"]
        for codeLine in self.get_all():
            lines.extend([""] * codeLine.space_before)
            lines.append(f"{self.indent_str * len(codeLine.all_parents())}{codeLine.code_str}")
            lines.extend([""] * codeLine.space_after)
        lines.append("# --------------------------------------------------------")
        return lines

    def print(self):
        """ Generate and print copyable code. """
        code = "\n".join(self.generate())
        print(code)
        return code

    def print_arrowed(self):
        """ . """


def debug(scope, *evals, printOut=True):
    """
    Easily call eval() on an arbitrary amount of evaluation strings.
    Useful for debugging.

    Example:
        debug(locals(), "value", "value + jumpValue", printOut=True)
        debug(locals())  # Prints all objects in scope

    :param dict scope: Just write locals()
    :param str evals: Variable names with or without operations
    :param printOut: Whether to print directly or not
    :return: A nicely formatted string
    """
    if not evals:
        evals = list(scope.keys())

    lines = []
    n = max([len(string) for string in evals])
    for evalStr in evals:
        lines.append(f"{evalStr:>{n}} = {eval(evalStr, scope)}")
    lines.append("")
    text = "\n".join(lines)
    if printOut:
        print(text)
    return text


# https://stackoverflow.com/questions/26300594/print-code-link-into-pycharms-console
def print_link(file=None, line=None):
    """ Print a link in PyCharm to a line in file.
        Defaults to line where this function was called. """
    if file is None:
        file = inspect.stack()[1].filename
    if line is None:
        line = inspect.stack()[1].lineno
    string = f'File "{file}", line {max(line, 1)}'.replace("\\", "/")
    print(string)
    return string


def print_link_to_obj(obj):
    """ Print a link in PyCharm to a module, function, class, method or property. """
    if isinstance(obj, property):
        obj = obj.fget
    file = inspect.getfile(obj)
    line = inspect.getsourcelines(obj)[1]
    return print_link(file=file, line=line)


def get_lines(obj):
    """ Return a list of source lines from an obj.
        Used to extract todos.
        Experimental. Works on modules, classes and functions available to `inspect`. """

    parent_objInfo = ObjInfo(obj)
    parent_objInfo.get_attrs()
    lines = []
    for objInfo in parent_objInfo.get_all():  # type: ObjInfo
        if objInfo.is_class() or objInfo.is_function():
            obj_lines = inspect.getsourcelines(objInfo.obj)[0]
            lines.extend([line for line in obj_lines if not re.match("^( *)?\\n$", line)])
    return lines


from generallibrary.object import ObjInfo








































