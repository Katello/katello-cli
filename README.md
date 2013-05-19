katello-cli [![Build Status](https://travis-ci.org/Katello/katello-cli.png?branch=master)](https://travis-ci.org/Katello/katello)
===========

This is Katello command line client. For more information, please see the [main
Katello README](https://github.com/Katello/katello/blob/master/README.md).

## What's included in this repository:


 * src - source for katello-cli
 * system-test - integration or smoke tests for testing a katello instance


## Using katello-cli

Once you have a katello server up and running, you can download this project and begin using it.

Usage: katello [options]

### Testing

Run unit tests (install python-mock - available in Fedora 17+)

```
make test
```

Compile a test RPM:

```
tito build --rpm --test --rpmbuild-options=--nodeps
```

Installing via pip into a virtualenv:

Locally:

```
env SWIG_FEATURES="-cpperraswarn -includeall -D__`uname -m`__ -I/usr/include/openssl" pip install -r requirements.txt
```

From the virtualenv:

```
env SWIG_FEATURES="-cpperraswarn -includeall -D__`uname -m`__ -I/usr/include/openssl" pip install -r <env-name>/etc/katello-cli/requirements.txt
```

Found a bug?
------------

For information on how to report a bug, please see the [Katello
README](https://github.com/Katello/katello/blob/master/README.md#found-a-bug).

Contributing
------------

For information on contributing to Katello, please see the [Katello
README](https://github.com/Katello/katello/blob/master/README.md#contributing).

Contact & Resources
-------------------

For resources and information about Katello, please see the [Katello
README](https://github.com/Katello/katello/blob/master/README.md#contact--resources).
