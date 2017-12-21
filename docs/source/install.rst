Installation
============

If you have **Python 3** installed, then simply type::

    pip install aosss


Pre-requisites
--------------

Python 3
~~~~~~~~

If you need to set up your Python 3 environment, one option is to visit project F311
installation instructions at `<http://trevisanj.github.io/f311/install.html>`_. That page also
provides a troubleshooting section that applies.

Installing AOSSS in developer mode
-----------------------------------

This is an alternative to the "pip" at the beginning of this section.
Use this option if you would like to download and modify the Python source code.

First clone the "aosss" GitHub repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/aosss.git

or

.. code:: shell

   git clone http://github.com/trevisanj/aosss

Then, install AOSSS in **developer** mode:

.. code:: shell

   cd aosss
   python setup.py develop

Upgrade ``aosss``
------------------

Package ``aosss`` can be upgraded to a new version by typing::

    pip install aosss --upgrade
