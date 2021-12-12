# Reference: https://github.com/longld/peda

import os
import sys
import signal

# set path to aarvi.py
AARVIFILE = os.path.abspath(os.path.expanduser(__file__))
if os.path.islink(AARVIFILE):
    AARVIFILE = os.readlink(AARVIFILE)
sys.path.insert(0, os.path.dirname(AARVIFILE) + "/lib_aarvi/")

from audio import TTS

from utils import *
from audio import *

class AarviCmd(object):

    # aarvi commands intercating with GDB

    commands = []
    def __init__(self):
        # list of all available commands
        self.commands = [c for c in dir(self) if callable(getattr(self, c)) and not c.startswith("_")]

    def _execute(self, gdb_command):
        gdb.execute(gdb_command)
        return

    def _get_helptext(self, *arg):

        """
        Get the help text, for internal use by help command and other aliases
        """
        (cmd,) = argv_normalize(arg, 1)
        helptext = ""
        if cmd is None:
            helptext = get_color("AARVI", "red" ,"bold") + get_color(" - Python Exploit Development Assistance for GDB", "blue","bold") + "\n"
            helptext += "List of \"aarvi\" subcommands, type the subcommand to invoke it:\n"
            i = 0
            for cmd in self.commands:
                if cmd.startswith("_"): continue # skip internal use commands
                func = getattr(self, cmd)
                helptext += "%s -- %s\n" % (cmd, get_color(trim(func.__doc__.strip("\n").splitlines()[0]), "green"))
            helptext += "\nType \"help\" followed by subcommand for full documentation."
        else:
            if cmd in self.commands:
                func = getattr(self, cmd)
                lines = trim(func.__doc__).splitlines()
                helptext += get_color(lines[0],"green") + "\n"
                for line in lines[1:]:
                    if "Usage:" in line:
                        helptext += get_color(line,"blue") + "\n"
                    else:
                        helptext += line + "\n"
            else:
                for c in self.commands:
                    if not c.startswith("_") and cmd in c:
                        func = getattr(self, c)
                        helptext += "%s -- %s\n" % (c, get_color(trim(func.__doc__.strip("\n").splitlines()[0]),"green"))


        return helptext

    def help(self, *arg):
        """
        Aarvi commands usage
        Usage:
            MYNAME
            MYNAME command
        """
        helptext=self._get_helptext(*arg)
        print(helptext)

        tts = TTS()
        tts.play_audio(helptext)
        return
    help.options = commands


    def start(self, *arg):
        """
        execute gdb start with music playing in the background
        Usage:
            MYNAME
        """
        print("aarviCmd::start")
        tts = TTS()
        tts.bg_audio()
        self._execute("start")
        return


class aarviGDBCommand(gdb.Command):
    # aarvi command's wrapper class 
    def __init__(self, cmdname="aarvi"):
        self.cmdname = cmdname
        self.__doc__ = aarviCmd._get_helptext()
        super(aarviGDBCommand, self).__init__(self.cmdname, gdb.COMMAND_DATA)

    def invoke(self, arg_string, from_tty): # used by aarvi help
        print("aarvi GDB invoke func")
        self.dont_repeat()
        arg = arg_string.split(' ')
        print("arg", arg, arg_string)
        if len(arg) < 1:
            aarviCmd.help()
        else:
            cmd = arg[0] if len(arg)==1 else arg[1]
            if cmd in aarviCmd.commands:
                func = getattr(aarviCmd, cmd)
                func()
            else:
                print("Undefined command: %s. Try \"aarvi help\"" % cmd)
        return


class Overload(gdb.Command):
    """
    Overload the GDB start command
    """
    def __init__(self, alias, command, shorttext=1):
        (cmd, opt) = (command + " ").split(" ", 1)
        if cmd == "aarvi" or cmd == "aariv":
            cmd = opt.split(" ")[0]
        if not shorttext:
            self.__doc__ = aarviCmd._get_helptext(cmd)
        else:
            self.__doc__ = green("Alias for '%s'" % command)
        self._command = command
        self._alias = alias
        super(Overload, self).__init__(alias, gdb.COMMAND_NONE)

    def invoke(self, args, from_tty):
        self.dont_repeat()
        gdb.execute("%s %s" %(self._command, args))


# Driver code for AARVI
aarviCmd = AarviCmd()
aarviCmd.help.__func__.options = aarviCmd.commands # XXX HACK

aarviGDBCommand()
print("aarviGDBCommand started")

for cmd in aarviCmd.commands:
    func = getattr(aarviCmd, cmd)
    func.__func__.__doc__ = func.__doc__.replace("MYNAME", cmd)
    #if cmd not in ["help", "show", "set"]:
    #    Overload(cmd, "aarvi %s" % cmd, 0) ## to override start of GDB

# handle SIGINT / Ctrl-C
def sigint_handler(signal, frame):
    print("ctrl+c interupt recieved")
    warning_msg("SIGINT from keyboard recieved")
    gdb.execute("set logging off")
    raise KeyboardInterrupt
signal.signal(signal.SIGINT, sigint_handler)

# misc gdb settings
aarviCmd._execute("set prompt \001%s\002" % get_color("\002gdb-aarvi$\001", "green")) # custom prompt

