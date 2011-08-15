# -*- coding: utf-8 -*-

# Copyright © 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

import os
import sys
import time
from gettext import gettext as _
from katello.client.i18n_optparse import OptionParser
from katello.client.i18n_optparse import OptionParser, OptionParserExitError
from M2Crypto import SSL
from socket import error as SocketError

from katello.client.config import Config
from katello.client.core.utils import system_exit, parse_tokens, Printer, SystemExitRequest
from katello.client.logutil import getLogger
from katello.client.server import ServerRequestError

Config()
_log = getLogger(__name__)

# base command class ----------------------------------------------------------
#
# NOTE: If you are adding or removing Commands and Actions you
# need to edit:
#
# katello/bin/kp-cmd
#
# They contain the mapping and lists of Commands and Actions for
# everything the CLI can do.

class Command(object):
    """
    Command class representing a katello cli command
    @ivar name: command's name
    @ivar parser: optparse.OptionParser instance
    @ivar username: username credential
    @ivar password: password credential
    @ivar cert_file: certificate file credential
    @ivar key_file: private key file credential
    """

    def __init__(self):
        """
        @type actions: None or tuple/list of str's
        @param actoins: list of actions to expose, uses _default_actions if None
        """
        self.cli = None
        self.name = None
        self._actions = {}
        self._action_order = []

    @property
    def usage(self):
        """
        Return a string showing the command's usage
        """
        lines = ['Usage: %s <options> %s <action> <options>' %
                 (self.cli.name, self.name),
                 'Supported Actions:']
        for name in self._action_order:
            action = self._actions[name]
            lines.append('\t%-14s %-25s' % (name, action.description))
        return '\n'.join(lines)

    @property
    def description(self):
        """
        Return a string showing the command's description
        """
        return _('no description available')

    def add_action(self, name, action):
        """
        Add an action to this command
        @note: actions are displayed in the order they are added
        @type name: str
        @param name: name to associate with the action
        @type action: L{Action} instance
        @param action: action to add
        """
        action.cmd = self
        action.name = name
        self._action_order.append(name)
        self._actions[name] = action

    def action_names(self):
        return self._actions.keys()

    def get_action(self, name):
        return self._actions.get(name, None)

    def process_options(self, args):

        self.parser = OptionParser()
        self.parser.disable_interspersed_args()
        self.parser.set_usage(self.usage)
        if not args:
            self.parser.error(_('no action given: please see --help'))

        self.parser.parse_args(args)

    def extract_action(self, args):
        action = self._actions.get(args[0], None)
        if action is None:
            self.parser.error(_('invalid action: please see --help'))
        return action

    def main(self, args):
        """
        Main execution of a katello cli command
        This method parses options sent to the command itself,
        looks up the corresponding action,
        and calls that action's main()
        @warning: this method should only be overridden with care
        @type args: list of str's
        @param args: command line arguments to parse
        """
        if type(args) == str:
            args = parse_tokens(args)

        try:
            self.process_options(args)

            action = self.extract_action(args)
            return action.main(args[1:])

        except OptionParserExitError, opee:
            return opee.args[0]

# base action class -----------------------------------------------------------

class Action(object):
    """
    Action class representing a single action for a cli command
    @ivar name: action's name
    @ivar parser: optparse.OptionParser instance
    @ivar opts: options returned from parsing command line
    @ivar args: arguments returned from parsing command line
    """

    def __init__(self):
        self.cmd = None
        self.name = None
        self.opts = None
        self.args = None
        self.optErrors = []
        self.printer = None

        self.parser = OptionParser()
        self.parser.add_option('-g', dest='grep',
                        action="store_true",
                        help=_("grep friendly output"))
        self.parser.add_option('-v', dest='verbose',
                        action="store_true",
                        help=_("verbose, more structured output"))
        self.parser.add_option('-d', dest='delimiter',
                        default="",
                        help=_("grep friendly output column delimiter"))
        self.setup_parser()

    @property
    def usage(self):
        """
        Return a string for this action's usage
        """
        if self.cmd:
            data = (self.cmd.cli.name, self.cmd.name, self.name)
        else:
            data = (os.path.basename(sys.argv[0]), self.name, "")

        return '%s <options> %s %s <options>' % data


    @property
    def description(self):
        """
        Return a string for this action's description
        """
        return _('no description available')


    def get_option(self, opt, default=None):
        """
        Get an option from opts or from the config file
        Options from opts take precedence.
        @type opt: str
        @param opt: name of option to get
        @return: value of the option or None if the option is no present
        """
        attr = getattr(self.opts, opt, default)
        if Config.parser.has_option('options', opt) and not attr:
            attr = Config.parser.get('options', opt)
        return attr


    def has_option(self, opt):
        """
        Check if option is present
        @type opt: str
        @param opt: name of option to check
        @return True if the option was set, otherwise False
        """
        return self.get_option(opt) != None


    def require_option(self, opt, flag=None):
        """
        Raise error if option is not present.
        @type opt: str
        @param opt: name of option to check
        @type flag: str
        @param flaf: flag for option, if None then --option_name is used
        """
        flag = flag or '--' + opt
        if (not self.option_specified(opt)):
            self.add_option_error(_('Option %s is required; please see --help') % flag)
        return

    def option_specified(self, opt):
        return self.has_option(opt) and self.get_option(opt) != ""

    def add_option_error(self, errorMsg):
        """
        Add option error to the error stack
        @type errorMsg: str
        @param errorMsg: error message
        """
        self.optErrors.append(errorMsg)


    def setup_parser(self):
        """
        Add custom options to the parser
        @note: this method should be overridden to add per-action options
        """
        self.parser.set_usage(self.usage)


    def add_scheduled_time_option(self):
        """
        Adds a --when scheduled time option to the option parser
        """
        self.parser.add_option("--when", dest="when", default=None,
                               help=_("Format: 'Year-Month-Day Hour:Min' specifies when to execute task"))


    def parse_scheduled_time_option(self):
        fmt = "%Y-%m-%d %H:%M"
        when = self.opts.when
        if when:
            try:
                when = time.strptime(when, fmt)
                when = time.mktime(when)
            except:
                system_exit(-1, _("Unable to parse scheduled time of: %s. Format needs to be in: %s") % (self.opts.when, fmt))
            if when < time.time():
                system_exit(-1, _("Scheduled time is in the past: %s.  Please re-run with a valid time.") % (self.opts.when))
        return when

    def run(self):
        """
        Action's functionality
        @note: override this method to implement the actoin's functionality
        @raise NotImplementedError: if this method is not overridden
        """
        raise NotImplementedError('Base class method called')

    def check_options(self):
        """
        Add custom option requirements
        @note: this method should be overridden to check for required options
        """
        return

    def grep_output(self):
        if self.has_option('grep'):
            return True
        elif self.has_option('verbose'):
            return False
        else:
            return (Config.parser.get('interface', 'grep_friendly').lower() == 'true')


#    def _pre_setup_parser(self):


    def process_options(self, args):
        """
        This method setups up the parser, parses the arguments, checks options
        and prints argument errors.
        """
        self.opts, self.args = self.parser.parse_args(args)

        self.printer = Printer(self.grep_output(), self.get_option('delimiter'))

        self.optErrors = []
        self.check_options()
        if len(self.optErrors) > 0:
            if len(self.optErrors) == 1:
                self.parser.error(self.optErrors[0])
            else:
                self.parser.error(self.optErrors)

    # this method exists so that an action can run like a command
    # it supports having single name actions (e.g. katello shell)
    def extract_action(self, args):
        pass

    def error(self, errorMsg):
        _log.error("error: %s" % str(errorMsg))
        print >> sys.stderr, _('error: operation failed: ') + str(errorMsg)

    def main(self, args):
        """
        Main execution of the action
        This method setups up the parser, parses the arguments, and calls run()
        in a try/except block, handling RestlibExceptions and general errors
        @warning: this method should only be overridden with care
        """
        try:
            self.process_options(args)
            return self.run()

        except SSL.Checker.WrongHost, wh:
            print _("ERROR: The server hostname you have configured in /etc/katello/client.conf does not match the")
            print _("hostname returned from the katello server you are connecting to.  ")
            print ""
            print _("You have: [%s] configured but got: [%s] from the server.") % (wh.expectedHost, wh.actualHost)
            print ""
            print _("Please correct the host in the /etc/katello/client.conf file")
            sys.exit(1)

        except ServerRequestError, re:
            try:
                msg = ", ".join(re.args[1]["errors"])
            except:
                msg = re.args[1]

            self.error(msg)
            return re.args[0]

        except SocketError, se:
            self.error(se.args[1])
            return se.args[0]

        except OptionParserExitError, opee:
            return opee.args[0]

        except SystemExitRequest, ser:
            msg = "\n".join(ser.args[1]).strip()
            if ser.args[0] == os.EX_OK:
                out = sys.stdout
                _log.error("error: %s" % str(msg))
            else:
                out = sys.stderr

            if msg != "":
                print >> out, msg
            return ser.args[0]

        except KeyboardInterrupt:
            return os.EX_NOUSER

        print ''
