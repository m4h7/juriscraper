|Build Status|

What is This?
=============

Juriscraper is a scraper library started several years ago that gathers
judicial opinions and oral arguments in the American court system. It is
currently able to scrape:

-  opinions from all major appellate Federal courts
-  opinions from all state courts of last resort except for Georgia
   (typically their "Supreme Court")
-  oral arguments from all appellate federal courts that offer them

Juriscraper is part of a two-part system. The second part is your code,
which calls Juriscraper. Your code is responsible for calling a scraper,
downloading and saving its results. A reference implementation of the
caller has been developed and is in use at
`CourtListener.com <http://courtlistener.com>`__. The code for that
caller can be `found
here <https://github.com/freelawproject/courtlistener/blob/master/alert/scrapers/management/commands/cl_scrape_and_extract.py>`__.
There is also a basic sample caller `included in
Juriscraper <https://github.com/freelawproject/juriscraper/blob/master/sample_caller.py>`__
that can be used for testing or as a starting point when developing your
own.

Some of the design goals for this project are:

-  extensibility to support video, oral argument audio, etc.
-  extensibility to support geographies (US, Cuba, Mexico, California)
-  Mime type identification through magic numbers
-  Generalized architecture with minimal code repetition
-  XPath-based scraping powered by lxml's html parser
-  return all meta data available on court websites (caller can pick
   what it needs)
-  no need for a database
-  clear log levels (DEBUG, INFO, WARN, CRITICAL)
-  friendly as possible to court websites

Installation & Dependencies
===========================

First step: Install Python 2.7.x, then:

::

    # install the dependencies
    sudo apt-get install libxml2-dev libxslt-dev  # In Ubuntu prior to 14.04 this is libxslt-devel

    # Install PhantomJS
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-linux-x86_64.tar.bz2
    tar -x -f phantomjs-1.9.7-linux-x86_64.tar.bz2
    sudo mkdir -p /usr/local/phantomjs
    sudo mv phantomjs-1.9.7-linux-x86_64/bin/phantomjs /usr/local/phantomjs
    rm -r phantomjs-1.9.7*  # Cleanup

    # Finally, install the code.
    pip install juriscraper

    # create a directory for logs (this can be skipped, and no logs will be created)
    sudo mkdir -p /var/log/juriscraper


Joining the Project as a Developer
==================================

We use a few tools pretty frequently while building these scrapers. The
first is `a sister project called
xpath-tester <https://github.com/mlissner/lxml-xpath-tester>`__ that
helps debug XPath queries. xpath-tester can be installed locally in a few
minutes.

We also generally use Eclipse with the PyDev and Aptana tools installed
or Intellij with PyCharm installed. These are useful because they allow
syntax highlighting, code inspection, and PyLint integration. Intellij
is particularly strong in these areas and a license is available to
interested contributors.

For scrapers to be merged:

-  ``python setup.py test`` must pass, listing the results for any new
   scrapers. This will be run automatically by
   `Travis-CI <https://travis-ci.org/freelawproject/juriscraper>`__.
-  a \*\_example\* file must be included in the ``tests/examples``
   directory (this is needed for the tests to run your code).
-  your code should be
   `PEP8 <http://www.python.org/dev/peps/pep-0008/>`__ compliant with no
   major Pylint problems or Intellij inspection issues.
-  your code should efficiently parse a page, returning no exceptions or
   speed warnings during tests on a modern machine.

When you're ready to develop a scraper, get in touch, and we'll find you
a scraper that makes sense and that nobody else is working on. We have `a wiki
list <https://github.com/freelawproject/juriscraper/wiki/Court-Websites>`__
of courts that you can browse yourself. There are templates for new
scrapers `here (for
opinions) <https://github.com/freelawproject/juriscraper/blob/master/juriscraper/opinions/opinion_template.py>`__
and `here (for oral
arguments) <https://github.com/freelawproject/juriscraper/blob/master/juriscraper/oral_args/oral_argument_template.py>`__.

When you're done with your scraper, fork this repository, push your
changes into your fork, and then send a pull request for your changes.
Be sure to remember to update the ``__init__.py`` file as well, since it
contains a list of completed scrapers.

Before we can accept any changes from any contributor, we need a signed
and completed Contributor License Agreement. You can find this agreement
in the root of the repository. While an annoying bit of paperwork, this
license is for your protection as a Contributor as well as the
protection of Free Law Project and our users; it does not change your
rights to use your own Contributions for any other purpose.


Getting Set Up as a Developer
=============================

To get set up as a developer of Juriscraper, you'll want to install the code
from git. To do that, install the dependencies and phantomjs as described above.
Instead of installing Juriscraper via pip, do the following:

::

    git clone https://github.com/freelawproject/juriscraper.git .
    python setup.py install


Usage
=====

The scrapers are written in Python, and can can scrape a court as
follows:

::

    from juriscraper.opinions.united_states.federal_appellate import ca1

    # Create a site object
    site = ca1.Site()

    # Populate it with data, downloading the page if necessary
    site.parse()

    # Print out the object
    print str(site)

    # Print it out as JSON
    print site.to_json()

    # Iterate over the item
    for opinion in site:
        print opinion

That will print out all the current meta data for a site, including
links to the objects you wish to download (typically opinions or oral
arguments). If you download those opinions, we also recommend running the
``_cleanup_content()`` method against the items that you download (PDFs,
HTML, etc.). See the ``sample_caller.py`` for an example and see
``_cleanup_content()`` for an explanation of what it does.

It's also possible to iterate over all courts in a Python package, even
if they're not known before starting the scraper. For example:

::

    # Start with an import path. This will do all federal courts.
    court_id = 'juriscraper.opinions.united_states.federal'
    # Import all the scrapers
    scrapers = __import__(
        court_id,
        globals(),
        locals(),
        ['*']
    ).__all__
    for scraper in scrapers:
        mod = __import__(
            '%s.%s' % (court_id, scraper),
            globals(),
            locals(),
            [scraper]
        )
        # Create a Site instance, then get the contents
        site = mod.Site()
        site.parse()
        print str(site)

This can be useful if you wish to create a command line scraper that
iterates over all courts of a certain jurisdiction that is provided by a
script. See ``lib/importer.py`` for an example that's used in
the sample caller.

Tests
=====

We got that! You can (and should) run the tests with
``python setup.py test``. This will iterate over all of the
``*_example*`` files and run the scrapers against them.

In addition, we use `Travis-CI <https://travis-ci.org/>`__ to
automatically run the tests whenever code is committed to the repository
or whenever a pull request is created. You can make sure that your pull
request is good to go by waiting for the automated tests to complete.

The current status of Travis CI on our master branch is:

|Build Status|

Version History
===============

**Past**

-  0.1 - Supports opinions from all 13 Federal Circuit courts and the
   U.S. Supreme Court
-  0.2 - Supports opinions from all federal courts of special
   jurisdiction (Veterans, Tax, etc.)
-  0.8 - Supports oral arguments for all possible Federal Circuit
   courts.
-  0.9 - Supports all state courts of last resort (typically the
   "Supreme" court)
-  1.0 - Support opinions from for all possible federal bankruptcy
   appellate panels (9th and 10th Cir.)

**Current**

-  1.1.* - Major code reorganization and first release on the Python Package Index (PyPi)

**Future Roadmap**

-  1.5 - Support opinions from for all intermediate appellate state
   courts
-  1.6 - Support opinions from for all courts of U.S. territories (Guam,
   American Samoa, etc.)
-  2.0 - Support opinions from for all federal district courts with
   non-PACER opinion listings
-  2.5 - Support opinions from for all federal district courts with
   PACER written opinion reports (+JPML)
-  2.6 - Support opinions from for all federal district bankruptcy
   courts
-  3.0 - For every court above where a backscraper is possible, it is
   implemented.

**Beyond** - Support video, additional oral argument audio, and
transcripts everywhere available - Add other countries, starting with
courts issuing opinions in English.


Deployment
==========

Deployment to PyPi should happen automatically by Travis CI whenever a new tag is created in Github on the master branch. It will fail if the version has not been updated or if Travis CI failed.

If you wish to create a new version manually, the process is:

1. Update version info in ``juriscraper/__init__.py``

1. Install the requirements in requirements_dev.txt

1. Set up a config file at ~/.pypirc

1. Generate a distribution

    ::

        python setup.py bdist_wheel

1. Upload the distribution

    ::

        twine upload dist/* -r pypi (or pypitest)


License
=======

Juriscraper is licensed under the permissive BSD license.

.. |Build Status| image:: https://travis-ci.org/freelawproject/juriscraper.svg?branch=master
   :target: https://travis-ci.org/freelawproject/juriscraper
