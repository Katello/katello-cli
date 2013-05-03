katello-cli [![Build Status](https://travis-ci.org/Katello/katello-cli.png?branch=master)](https://travis-ci.org/Katello/katello)
===========

This is Katello command line client.


Getting Started
---------------

The easiest way to get stable version of Katello up and running is following
[Katello Wiki Installation Instructions](https://fedorahosted.org/katello/wiki/Install).

If you like living on the edge, go for
[nightly builds](https://fedorahosted.org/katello/wiki/InstallTesting)
instead.

Found a bug?
------------

That's rather unfortunate. But don't worry! We can help. Just file a bug
[on our Bugzilla](https://bugzilla.redhat.com/enter_bug.cgi?product=Katello) or
[in Github](https://github.com/Katello/katello-cli/issues)


Contributing
------------

See
[development instructions](https://fedorahosted.org/katello/wiki/AdvancedInstallation#GettingupandRunningGIT).

What's included in this repository:

 * src - source for katello-cli
 * system-test - integration or smoke tests for testing a katello instance


### Using katello-cli

Once you have a katello server up and running, you can download this project and begin using it.

Usage: katello [options]

#### Testing

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

Contact & Resources
-------------------

 * [Katello.org](http://katello.org)
 * [Wiki](https://fedorahosted.org/katello/wiki)
 * [User mailing list](https://fedorahosted.org/mailman/listinfo/katello)
 * [Developer mailing list](https://www.redhat.com/mailman/listinfo/katello-devel)
 * [IRC Freenode](http://freenode.net/using_the_network.shtml): #katello
 * [Twitter](https://twitter.com/Katello_Project)
