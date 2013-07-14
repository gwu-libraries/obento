obento
======

A simple python/django search multiplexing backend for use in a bento-style
frontend.  


requirements
============

Developed using Python 2.7, Django 1.5, and PostgreSQL 9.1 on Ubuntu 12.04.


Installation Instructions
=========================

PART I - Basic server requirements
----------------------------------

1. Install Apache and other dependencies

        $ sudo apt-get install apache2 libapache2-mod-wsgi libaio-dev python-dev python-profiler

2. Install Postgresql

        $ sudo apt-get install postgresql postgresql-contrib libpq-dev

3. Set up Postgresql

    Create a user for django

        $ sudo -u postgres createuser --createdb --no-superuser --no-createrole --pwprompt django

    Create a database for the obento application

        $ sudo -u postgres createdb -O django obento

4. Install Git

        $ sudo apt-get install git-core

PART II - Set up project environment
------------------------------------

1. Install virtualenv

        $ sudo apt-get install python-setuptools
        $ sudo easy_install virtualenv

2. Create a directory for your projects (replace &lt;OBENTO_HOME&gt; with your desired directory path and name: for instance /obento or /home/&lt;username&gt;/obento)

        $ mkdir /<OBENTO_HOME>
        $ cd /<OBENTO_HOME>

3. Pull down the project from github

        (GW staff only)
        $ git clone git@github.com:gwu-libraries/obento.git

        (everyone else)
        $ git clone https://github.com/gwu-libraries/obento.git

4. Create virtual Python environment for the project

        $ cd /<OBENTO_HOME>/obento
        $ virtualenv --no-site-packages ENV

5. Activate your virtual environment

        $ source ENV/bin/activate

6. install django, tastypie, and other python dependencies

        (ENV)$ pip install -r requirements.txt

PART III - Configure your installation
--------------------------------------

0. Create a logs directory

        $ mkdir logs

1. Copy the local settings template to an active file

        $ cd obento/obi
        $ cp local_settings.py.template local_settings.py

2. Update the values in the local_setting.py file:  for the database, NAME, USER, and PASSWORD to the database you created above, and set ENGINE to 'postgresql_psycopg2'; also, set a SECRET_KEY. Enter appropriate values for requester, minter, url and port under IDSERVICE and TEST_IDSERVICE.

        $ vim local_settings.py

3. Copy the WSGI file template to an active file

        $ cp wsgi.py.template wsgi.py

4. Update the wsgi.py file. (Change the value of ENV to your environment path)

        $ vim wsgi.py
