"""
ansible-role-manager help command
"""
from __future__ import print_function

import os
import sys
import argparse
from . import Command
from arm.util import find_subclasses

# ----------------------------------------------------------------------

class help(Command):

    help = "an alias for calling `-h` on any subcommand"

    def __init__(self, parser):
        parser.description = self.help
        parser.add_argument('command', default=None, nargs='?')

    def run(self, argv):
        commands_dir = os.path.dirname(__file__)
        parser = argparse.ArgumentParser(prog=sys.argv[0])
        subparsers = parser.add_subparsers()


        # import all the modules in the command directory
        for module in os.listdir(commands_dir):
            if module == '__init__.py' or module[-3:] != '.py':
                continue

            command_mod = __import__('arm.commands.%s' % module[:-3], locals(), globals(),['object'],-1)

            # add a subparser for each command
            # Assumes that each command defines a ``BaseCommand`` inheriting from ``arm.commands.Command``
            # search for all subclasses of ``arm.commands.Command``
            for command_name, command_class in find_subclasses(command_mod, Command):
                # attch the command
                command_parser = subparsers.add_parser(command_name, help=command_class.help)

                # instantiate the command and provide its ``run`` method as the callback
                command = command_class(command_parser)
                command_parser.set_defaults(func=command.run)

        if getattr(argv, 'command', None):
            args = parser.parse_args([argv.command, '-h'])
        args = parser.parse_args(['-h'])

