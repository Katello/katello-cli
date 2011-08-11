#
# Katello Repos actions
# Copyright (c) 2010 Red Hat, Inc.
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
#

import os
from gettext import gettext as _

from katello.client.config import Config
from katello.client.core.base import Action, Command
from katello.client.core.utils import is_valid_record
from katello.client.core.utils import Printer

Config()

# base system action --------------------------------------------------------

class ClientAction(Action):
    
    def __init__(self):
        super(ClientAction, self).__init__()


# system actions ------------------------------------------------------------

class Remember(ClientAction):
    
    description = _('save an option to the client config')

    def setup_parser(self):
        self.parser.add_option('--option', dest='option',
                       help=_("name of the option to be saved (e.g. org, environment, provider, etc) (required)"))
        self.parser.add_option('--value', dest='value',
                       help=_("value to be store under specified option (required)"))

    def check_options(self):
        self.require_option('option')
        self.require_option('value')

    def run(self):
        option = self.opts.option
        value = self.opts.value
        
        if not Config.parser.has_section('options'):
            Config.parser.add_section('options')
        
        has_option = Config.parser.has_option('options', option)
        Config.parser.set('options', option, value)
        
        try:
            Config.save()
            verb = "overwrote" if has_option else "remembered"
            print ("Successfully " + verb + " option [ {} ] ").format(option)
        except (Exception):
            print ("Unsuccessfully remembered option [ {} ] ").format(option)
            return os.EX_DATAERR
        
        return os.EX_OK
    
class Forget(ClientAction):
    
    description = _('remove an option from the client config')
    
    def setup_parser(self):
        self.parser.add_option('--option', dest='option',
                       help=_("name of the option to be deleted (required)"))
    
    def check_options(self):
        self.require_option('option')
    
    def run(self):
        option = self.opts.option
        
        Config.parser.remove_option('options', option)
        try:
            Config.save()
            print "Successfully forgot option [ {} ]".format(option)
        except (Exception):
            print "Unsuccessfully forgot option [ {} ]".format(option)
            return os.EX_DATAERR
        
        return os.EX_OK
    
class SavedOptions(ClientAction):
    
    description = _('list options saved in the client config')
    
    def setup_parser(self):
        pass
    
    def check_options(self):
        pass
    
    def run(self):
        self.printer.setHeader(_("Saved Options"))
        
        options = Config.parser.options('options')
        
        options_list = []
        for o in options:
            options_list.append({ 'option': o, 'value': Config.parser.get('options', o) })
        
        self.printer.addColumn('option')
        self.printer.addColumn('value')
        self.printer._grep = True
        self.printer.printItems(options_list)
        
        return os.EX_OK
    
class Client(Command):

    description = _('client specific actions in the katello server')