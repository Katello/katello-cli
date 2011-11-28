#
# Katello Organization actions
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
import itertools
from gettext import gettext as _
from optparse import OptionValueError

from katello.client.api.template import TemplateAPI
from katello.client.config import Config
from katello.client.core.base import Action, Command
from katello.client.core.utils import is_valid_record, get_abs_path, run_spinner_in_bg, wait_for_async_task, system_exit
from katello.client.api.utils import get_locker, get_environment, get_template, get_product

try:
    import json
except ImportError:
    import simplejson as json

# set import (works for both Python 2.6+ and 2.5)
try:
    set
except NameError:
    from sets import Set as set

Config()


# base template action =========================================================
class TemplateAction(Action):

    def __init__(self):
        super(TemplateAction, self).__init__()
        self.api = TemplateAPI()


    def get_parent_id(self, orgName, envName, parentName):
        parent = get_template(orgName, envName, parentName)
        if parent != None:
            return parent["id"]
        system_exit(os.EX_DATAERR)

# ==============================================================================
class List(TemplateAction):

    description = _('list all templates')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required if specifying environment)"))
        self.parser.add_option('--environment', dest='env',
                               help=_("environment name eg: dev (Locker by default)"))

    def check_options(self):
        self.require_option('org')

    def run(self):
        envName = self.get_option('env')
        orgName = self.get_option('org')

        environment = get_environment(orgName, envName)

        if not environment:
            return os.EX_DATAERR
        templates = self.api.templates(environment["id"])

        if not templates:
            print _("No templates found in environment [ %s ]") % environment["name"]
            return os.EX_OK
        self.printer.addColumn('id')
        self.printer.addColumn('name')
        self.printer.addColumn('description', multiline=True)
        self.printer.addColumn('environment_id')
        self.printer.addColumn('parent_id')

        self.printer.setHeader(_("Template List"))
        self.printer.printItems(templates)
        return os.EX_OK


# ==============================================================================
class Info(TemplateAction):

    description = _('list information about a template')

    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("template name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option('--environment', dest='env',
                               help=_("environment name eg: dev (Locker by default)"))

    def check_options(self):
        self.require_option('name')
        self.require_option('org')

    def run(self):
        tplName = self.get_option('name')
        orgName = self.get_option('org')
        envName = self.get_option('env')

        template = get_template(orgName, envName, tplName)
        if template == None:
            return os.EX_DATAERR

        template["products"] = "\n".join([p["name"] for p in template["products"]])
        template["packages"] = "\n".join([self._build_nvrea(p) for p in template["packages"]])
        template["parameters"] = "\n".join([ key+":\t"+value for key, value in template["parameters"].iteritems() ])
        template["package_groups"] = "\n".join([p["name"] for p in template["package_groups"]])
        template["package_group_categories"] = "\n".join([p["name"] for p in template["pg_categories"]])

        self.printer.addColumn('id')
        self.printer.addColumn('name')
        self.printer.addColumn('revision', show_in_grep=False)
        self.printer.addColumn('description', multiline=True)
        self.printer.addColumn('environment_id')
        self.printer.addColumn('parent_id')
        self.printer.addColumn('errata', multiline=True, show_in_grep=False)
        self.printer.addColumn('products', multiline=True, show_in_grep=False)
        self.printer.addColumn('packages', multiline=True, show_in_grep=False)
        self.printer.addColumn('parameters', multiline=True, show_in_grep=False)
        self.printer.addColumn('package_groups', multiline=True, show_in_grep=False)
        self.printer.addColumn('package_group_categories', multiline=True, show_in_grep=False)

        self.printer.setHeader(_("Template Info"))
        self.printer.printItem(template)
        return os.EX_OK


    def _build_nvrea(self, package):

        if package['version'] != None and package['release'] != None:
            nvrea = '-'.join((package['package_name'], package['version'], package['release']))
            if package['arch'] != None:
                nvrea = nvrea +'.'+ package['arch']
            if package['epoch'] != None:
                nvrea = package['epoch'] +':'+ nvrea
            return nvrea

        else:
            return package['package_name']



# ==============================================================================
class Import(TemplateAction):

    description = _('create a template file and import data')


    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option("--file", dest="file",
                               help=_("path to the template file (required)"))
        self.parser.add_option("--description", dest="description",
                               help=_("provider description"))


    def check_options(self):
        self.require_option('org')
        self.require_option('file')


    def run(self):
        desc    = self.get_option('description')
        orgName = self.get_option('org')
        tplPath = self.get_option('file')

        env = get_locker(orgName)
        if env == None:
            return os.EX_DATAERR

        try:
            f = self.open_file(tplPath)
        except:
            print _("File %s does not exist" % tplPath)
            return os.EX_IOERR

        response = run_spinner_in_bg(self.api.import_tpl, (env["id"], desc, f), message=_("Importing template, please wait... "))
        print response
        f.close()
        return os.EX_OK

    def open_file(self, path):
        return open(get_abs_path(path))

# ==============================================================================
class Export(TemplateAction):

    description = _('export the template into the file')
    supported_formats = ['json', 'tdl']

    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("template name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option('--environment', dest='env',
                               help=_("environment name eg: dev"))
        self.parser.add_option("--file", dest="file",
                               help=_("path to the template file (required)"))
        self.parser.add_option("--format", dest="format", choices=self.supported_formats,
                               help=_("format of the export, possible values: %s, default: json") % self.supported_formats)


    def check_options(self):
        self.require_option('org')
        self.require_option('name')
        self.require_option('file')
        self.require_option('env')

    def run(self):
        tplName = self.get_option('name')
        orgName = self.get_option('org')
        envName = self.get_option('env')
        format  = self.get_option('format') or "json"
        tplPath = self.get_option('file')

        template = get_template(orgName, envName, tplName)
        if not template:
            return os.EX_DATAERR

        try:
            f = self.open_file(tplPath)
        except:
            print _("Could not create file %s") % tplPath
            return os.EX_IOERR

        self.api.validate_tpl(template["id"], format)
        response = run_spinner_in_bg(self.api.export_tpl, (template["id"], format), message=_("Exporting template, please wait... "))
        f.write(response)
        f.close()
        print _("Template was exported successfully to file %s") % tplPath
        return os.EX_OK

    def open_file(self, path):
        return open(get_abs_path(path),"w")


# ==============================================================================
class Create(TemplateAction):

    description = _('create an empty template file')


    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("template name (required)"))
        self.parser.add_option('--parent', dest='parent',
                               help=_("name of the parent template"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option("--description", dest="description",
                               help=_("template description"))


    def check_options(self):
        self.require_option('name')
        self.require_option('org')


    def run(self):
        name    = self.get_option('name')
        desc    = self.get_option('description')
        orgName = self.get_option('org')
        parentName = self.get_option('parent')

        env = get_locker(orgName)
        if env != None:
            if parentName != None:
                parentId = self.get_parent_id(orgName, env['name'], parentName)
            else:
                parentId = None

            template = self.api.create(env["id"], name, desc, parentId)
            if is_valid_record(template):
                print _("Successfully created template [ %s ]") % template['name']
                return os.EX_OK
            else:
                print _("Could not create template [ %s ]") % name
                return os.EX_DATAERR
        else:
            return os.EX_DATAERR


# ==============================================================================
class Update(TemplateAction):

    description = _('updates name and description of a template')

    def __init__(self):
        self.current_parameter = None
        self.add_parameters = {}
        super(Update, self).__init__()


    def store_parameter_name(self, option, opt_str, value, parser):
        self.current_parameter = value
        self.add_parameters[value] = None

    def store_parameter_value(self, option, opt_str, value, parser):
        if self.current_parameter == None:
            raise OptionValueError(_("each %s must be preceeded by %s") % (option, "--add_parameter") )

        self.add_parameters[self.current_parameter] = value
        self.current_parameter = None

    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("template name (required)"))
        self.parser.add_option('--parent', dest='parent',
                               help=_("name of the parent template"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option('--new_name', dest='new_name',
                               help=_("new template name"))
        self.parser.add_option("--description", dest="description",
                               help=_("template description"))

        self.parser.add_option('--add_product', dest='add_products',
                                action="append",
                                help=_("name of the product"))
        self.parser.add_option('--remove_product', dest='remove_products',
                                action="append",
                                help=_("name of the product"))

        self.parser.add_option('--add_package', dest='add_packages',
                                action="append",
                                help=_("name or nvre of the product (epoch:name-rel.eas-ver.sio.n)"))
        self.parser.add_option('--remove_package', dest='remove_packages',
                                action="append",
                                help=_("name or nvre of the product (epoch:name-rel.eas-ver.sio.n)"))

        self.parser.add_option('--add_parameter', dest='add_parameters',
                                action="callback", callback=self.store_parameter_name, type="string",
                                help=_("name of the parameter, %s must follow") % "--value")
        self.parser.add_option('--value', dest='value',
                                action="callback", callback=self.store_parameter_value, type="string",
                                help=_("value of the parameter"))
        self.parser.add_option('--remove_parameter', dest='remove_parameters',
                                action="append",
                                help=_("name of the parameter"))

        self.parser.add_option('--add_package_group', dest='add_pgs',
                                action="append",
                                help=_("name of the package group"))
        self.parser.add_option('--remove_package_group', dest='remove_pgs',
                                action="append",
                                help=_("name of the package group"))

        self.parser.add_option('--add_package_group_category', dest='add_pg_categories',
                                action="append",
                                help=_("name of the package group category"))
        self.parser.add_option('--remove_package_group_category', dest='remove_pg_categories',
                                action="append",
                                help=_("name of the package group category"))

        self.parser.add_option('--add_distribution', dest='add_distributions',
                                action="append",
                                help=_("distribution id"))
        self.parser.add_option('--remove_distribution', dest='remove_distributions',
                                action="append",
                                help=_("distribution id"))
        self.resetParameters()


    def check_options(self):
        self.require_option('name')
        self.require_option('org')

        #check for missing values
        for k, v in self.add_parameters.iteritems():
            if v == None:
                self.add_option_error(_("missing value for parameter '%s'") % k)

    def resetParameters(self):
        self.add_parameters = {}

    def getContent(self):
        orgName = self.get_option('org')

        content = {}
        content['+products'] = self.get_option('add_products') or []
        content['+products'] = self.productNamesToIds(orgName, content['+products'])

        content['-products'] = self.get_option('remove_products') or []
        content['-products'] = self.productNamesToIds(orgName, content['-products'])

        content['+packages'] = self.get_option('add_packages') or []
        content['-packages'] = self.get_option('remove_packages') or []

        content['+pgs'] = self.get_option('add_pgs') or []
        content['-pgs'] = self.get_option('remove_pgs') or []

        content['+pg_categories'] = self.get_option('add_pg_categories') or []
        content['-pg_categories'] = self.get_option('remove_pg_categories') or []

        content['+parameters'] = self.add_parameters.copy()
        content['-parameters'] = self.get_option('remove_parameters') or []

        content['+distros'] = self.get_option('add_distributions') or []
        content['-distros'] = self.get_option('remove_distributions') or []
        return content

    def run(self):
        tplName = self.get_option('name')
        orgName = self.get_option('org')
        newName = self.get_option('new_name')
        desc    = self.get_option('description')
        parentName = self.get_option('parent')
        content    = self.getContent()
        #reset parameters for next call in shell mode
        self.resetParameters()

        env = get_locker(orgName)
        if env == None:
            return os.EX_DATAERR

        template = get_template(orgName, env["name"], tplName)
        if template != None:
            if parentName != None:
                parentId = self.get_parent_id(orgName, env["name"], parentName)
            else:
                parentId = None

            run_spinner_in_bg(self.updateTemplate, [template["id"], newName, desc, parentId], _("Updating the template, please wait... "))
            run_spinner_in_bg(self.updateContent,  [template["id"], content], _("Updating the template, please wait... "))
            print _("Successfully updated template [ %s ]") % template['name']
            return os.EX_OK
        else:
            return os.EX_DATAERR


    def productNamesToIds(self, orgName, productNames):
        ids = []
        for prodName in productNames:
            p = get_product(orgName, prodName)
            if p != None:
                ids.append(p['id'])
            else:
                system_exit(os.EX_DATAERR)
        return ids


    def updateTemplate(self, tplId, name, desc, parentId):
        self.api.update(tplId, name, desc, parentId)


    def updateContent(self, tplId, content):

        for p in content['-products']:
            self.api.remove_content(tplId, 'products', p)
        for p in content['+products']:
            self.api.add_content(tplId, 'products', {'id': p})

        for p in content['-packages']:
            self.api.remove_content(tplId, 'packages', p)
        for p in content['+packages']:
            self.api.add_content(tplId, 'packages', {'name': p})

        for p in content['-pgs']:
            self.api.remove_content(tplId, 'package_groups', p)
        for p in content['+pgs']:
            self.api.add_content(tplId, 'package_groups', {'name': p})

        for p in content['-pg_categories']:
            self.api.remove_content(tplId, 'package_group_categories', p)
        for p in content['+pg_categories']:
            self.api.add_content(tplId, 'package_group_categories', {'name': p})

        for p in content['-parameters']:
            self.api.remove_content(tplId, 'parameters', p)
        for p, v in content['+parameters'].iteritems():
            self.api.add_content(tplId, 'parameters', {'name': p, 'value': v})

        for p in content['-distros']:
            self.api.remove_content(tplId, 'distributions', p)
        for p in content['+distros']:
            self.api.add_content(tplId, 'distributions', {'id': p})



# ==============================================================================
class Delete(TemplateAction):

    description = _('deletes a template')

    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("template name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option('--environment', dest='env',
                               help=_("environment name eg: foo.example.com (Locker by default)"))

    def check_options(self):
        self.require_option('name')
        self.require_option('org')

    def run(self):
        tplName = self.get_option('name')
        orgName = self.get_option('org')
        envName = self.get_option('env')

        template = get_template(orgName, envName, tplName)
        if template != None:
            msg = self.api.delete(template["id"])
            print msg
            return os.EX_OK
        else:
            return os.EX_DATAERR


# provider command =============================================================

class Template(Command):

    description = _('template specific actions in the katello server')
