obento
======

A simple python/django search multiplexing backend for use in a bento-style
frontend.  


requirements
============

Developed using Python 2.7, Django 1.6, and PostgreSQL 9.1 on Ubuntu 12.04.


Installation Instructions
=========================

PART I - Basic server requirements
----------------------------------

1. Install Apache and other dependencies

        $ sudo apt-get install apache2 libapache2-mod-wsgi libaio-dev python-dev python-profiler postgresql postgresql-contrib libpq-dev git libxml2-dev libxslt-dev openjdk-7-jdk python-setuptools python-virtualenv

2. Prepare Java JVM symlink for Jetty

   Create a symlink to the java jvm

        $ sudo mkdir /usr/java

        $ sudo ln -s /usr/lib/jvm/java-7-openjdk-amd64 /usr/java/default

3. Download Jetty and unzip.  

        $ cd /opt

   Go to http://download.eclipse.org/jetty/stable-9/dist/ and copy the link to the .tar.gz version of the latest download of Jetty 9.  Use this link in the following wget command to download the .tar.gz file (again, the URL may change):

        $ sudo wget -O jetty.gz "http://eclipse.org/downloads/download.php?file=/jetty/stable-9/dist/jetty-distribution-9.2.3.v20140905.tar.gz&r=1"

        $ sudo mkdir jetty

        $ sudo tar -xvf jetty.gz -C jetty --strip-components=1

4. Create jetty user and make it the owner of /opt/jetty

        $ sudo useradd jetty -U -s /bin/false

        $ sudo chown -R jetty:jetty /opt/jetty

5. Set up jetty to run as a service

        $ sudo cp /opt/jetty/bin/jetty.sh /etc/init.d/jetty

6. Create the jetty settings file
  
        $ sudo vi /etc/default/jetty

   Paste the following into the file, and save it:

        JAVA=/usr/bin/java
        NO_START=0                 # Start on boot
        JETTY_HOST=0.0.0.0         # Listen to all hosts
        JETTY_ARGS=jetty.port=8983
        JETTY_USER=jetty           # Run as this user
        JETTY_HOME=/opt/jetty

    In production, jetty should be running on a port that won't be publicly exposed.  In development and testing, exposing Solr might be helpful; never expose it in production.
    
    NOTE:  In the step above, JAVA is set to /usr/bin/java.  When upgrading from an environment that had Java 6 installed, /usr/bin/java may be a symbolic link (...to another symbolic link) which still points to a Java 6 JRE.  If that is the case, reconfigure to ensure that either /usr/bin/java resolves to a Java 7 JRE, or point JAVA in the jetty config file to wherever the Java 7 JRE is.

7. Start jetty

        $ sudo service jetty start

   This should return something that starts with:

        Starting Jetty: OK

   Verify that MYSERVER:8983 returns a page that is "Powered by Jetty" (even if it is a 404-Not Found page) 

8. Add jetty to startup

        $ sudo update-rc.d jetty defaults

9. Download and unzip solr

   Go to http://www.apache.org/dyn/closer.cgi/lucene/solr and copy the link to the .tgz version of the latest download of Solr 4.  Use this link in the following wget command to download the .tgz file (again, the URL may change).  This may also require a --no-check-certificate option as well, depending on the download site:

        $ sudo wget -O solr.gz "https://www.carfab.com/apachesoftware/lucene/solr/4.10.2/solr-4.10.2.tgz"

        $ sudo tar -xvf solr.gz

    Copy solr contents (precise solr 4 version number may vary):

        $ sudo cp -R solr-4.10.2/example/solr /opt

        $ sudo cp -r /opt/solr-4.10.2/dist /opt/solr

        $ sudo cp -r /opt/solr-4.10.2/contrib /opt/solr

    Copy ICU Tokenizer jars to /opt/solr/lib

        $ sudo mkdir /opt/solr/lib

        $ sudo cp /opt/solr/contrib/analysis-extras/lib/icu4j-*.jar /opt/solr/lib

        $ sudo cp /opt/solr/contrib/analysis-extras/lucene-libs/lucene-analyzers-icu-* /opt/solr/lib

10. Copy solr .war and .jar files to jetty

        $ sudo cp /opt/solr/dist/solr-4.10.2.war /opt/jetty/webapps/solr.war

        $ sudo cp /opt/solr-4.10.2/example/lib/ext/* /opt/jetty/lib/ext

11. Update jetty settings

        $ sudo vi /etc/default/jetty

    Append the following line:

        JAVA_OPTIONS="-Dsolr.solr.home=/opt/solr $JAVA_OPTIONS"
    
12. Change the owner of the solr folder and contents to jetty
        
        $ sudo chown -R jetty:jetty /opt/solr

13. Change ``collection1`` in solr to ``obento``:

        $ cd /opt/solr
            
        $ sudo mv collection1 obento

    Replace ``name=collection1`` with ``name=obento`` in core.properties:
            
        $ sudo vi obento/core.properties
            
14. Restart jetty

        $ sudo service jetty restart
            

PART II - Set up project environment
------------------------------------

1. Create a directory for your projects (replace &lt;OBENTO_HOME&gt; with 
your desired directory path and name: for instance ```/obento``` or 
```/home/<username>/obento``` )

        $ mkdir <OBENTO_HOME>
        $ cd <OBENTO_HOME>

2. Pull down the project from github

        (GW staff only)
        $ git clone git@github.com:gwu-libraries/obento.git

        (everyone else)
        $ git clone https://github.com/gwu-libraries/obento.git

3. Create virtual Python environment for the project

        $ cd <OBENTO_HOME>/obento
        $ virtualenv --no-site-packages ENV

4. Activate your virtual environment

        $ source ENV/bin/activate

5. Install project dependencies

        (ENV)$ pip install -r requirements.txt
        
   If the previous step encounters problems installing pytz, then it can be installed as follows

        easy_install --upgrade pytz


    
PART III - Set up the database
------------------------------

1. Create a database user for django (and make a note of the password you create).  A name for MYDBUSER might be something like ```obentouser_m1``` (m1 for milestone 1)

        $ sudo -u postgres createuser --createdb --no-superuser --no-createrole --pwprompt MYDBUSER

2. Create a database for the obento application.  A name for MYDBNAME might be something like ```obi_m1```

        $ sudo -u postgres createdb -O MYDBUSER MYDBNAME



PART IV - Configure the web application
---------------------------------------

1. Copy the local settings template to an active file

        $ cd obento/obi/obi
        $ cp local_settings.py.template local_settings.py

2. Update the values in the ```local_settings.py``` file:  for the database, ```NAME```, ```USER```, and ```PASSWORD``` to the database you created above, and set ```ENGINE``` to 'postgresql_psycopg2'; also, set a ```SECRET_KEY```.  Ensure that the port number in ```SOLR_URL``` matches ```JETTY_PORT``` configured earlier in ```/etc/default/jetty```.

        $ vi local_settings.py

3. Copy the WSGI file template to an active file

        $ cp wsgi.py.template wsgi.py

4. Update the wsgi.py file. (Uncomment the virtualenv settings starting with "import site" and Change the value of ENV to your environment path)

        $ vi wsgi.py
        
5. Initialize database tables. WARNING: Be sure you are still using your virtualenv. DO NOT create a superuser when prompted!

        (ENV)$ cd <OBENTO_HOME>/obento/obi
        (ENV)$ python manage.py makemigrations

    If you encounter an authentication error with postgresql edit your local_settings.py file and set HOST = 'localhost'

    If you encounter an error during the above command that ends with:

        TypeError: decode() argument 1 must be string, not None

    Then you need to add location values to your profile. Open your .bashrc file in an editor:

        $ vim ~/.bashrc

    Enter the following values at the end of the file and save.

        export LC_ALL=en_US.UTF-8
        export LANG=en_US.UTF-8

    Now, reload your bashrc changes:

        source ~/.bashrc

    Now, rerun the syncdb command.

6. Migrate the database to the latest updates

        $ python manage.py migrate

7. Copy the Apache virtual host file to the Apache2 directory

        $ cd /<OBENTO_HOME>/obento
        $ sudo cp apache/obento /etc/apache2/sites-available/obento.conf


Part V - Start the server
--------------------------

If you choose to run obento in apache (versus django runserver):

1. Update the values in the Apache virtual host file.

    Edit the host port number
    Edit your server name (base url)
    Edit the many instances of &lt;path to OBENTO_HOME&gt;. Beware: the line for the WSGI Daemon has two references to that path.

        $ sudo vi /etc/apache2/sites-available/obento.conf

    To change all of the path values at once use the global replace command in vim

        :%s/old_value/new_value/g

2. Enable the apache headers module, this is required for CORS support.

        $ sudo a2enmod headers

3. Enable the new virtualhost. If you are using port 80 also disable the default host

        $ sudo a2ensite obento
        $ sudo a2dissite default
        $ sudo service apache2 restart



Part VI - Load some data
------------------------

1.  Copy the obento solr configuration files to solr
        
        $ sudo cp -r /<OBENTO_HOME>/obento/obi/obi/conf /opt/solr/obento/

    Restart jetty

        $ sudo service jetty restart

To load GW's list of databases from libguides, first configure 
```local_settings.py``` with a list of libguides page sids.

Then, to load/parse/add databases from these pages to the database:

        $ ./manage.py load_databases

To verify that the databases loaded, try querying the html or json view:

        http://<OBENTO_URL>/databases_html?q=proquest
        http://<OBENTO_URL>/databases_json?q=proquest

To index the list of databases in Solr:

        $ ./manage.py index_all

Test that indexing worked with this path:

        http://<OBENTO_URL>/databases_solr_html?q=proquest
        http://<OBENTO_URL>/databases_solr_json?q=proquest

The results should look different from the test above.

To load the Excel-formatted extract of journal titles:

        $ ./manage.py load_journals <JOURNALS_EXCEL_FILE>

To verify that the journal titles loaded, try querying the html or json view:

        http://<OBENTO_URL>/journals_html?q=science
        http://<OBENTO_URL>/journals_json?q=science

To index the list of journals in Solr:

        $ ./manage.py index_all

Test that indexing worked with this path:

        http://<OBENTO_URL>/journals_solr_html?q=science
        http://<OBENTO_URL>/journals_solr_json?q=science

The results should look different from the test above.
