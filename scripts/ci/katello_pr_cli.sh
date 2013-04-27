#!/bin/bash
sudo apt-get install libssl-dev m2crypto
sudo pip install -r requirements-dev.pip --use-mirrors

echo ""
echo "********* Python CLI Unit Tests ***************"
echo "RUNNING: make test"
make test || exit 5

echo ""
echo "********* Running Pylint ************************"
echo "RUNNING: PYTHONPATH=src/ pylint --rcfile=./etc/spacewalk-pylint.rc --additional-builtins=_ katello"
PYTHONPATH=src/ pylint --rcfile=./etc/spacewalk-pylint.rc --additional-builtins=_ katello || exit 1

