
from os.path import abspath, dirname

# this path is substituted in spec for different path in production
main_path = abspath(dirname(__file__)+'/../../src/katello')
__path__.append(main_path)

from katello.client.i18n import configure_i18n
configure_i18n()
