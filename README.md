Obento
======

A simple python/django search multiplexing backend for use in a bento-style
frontend for GW Libraries.


Requirements
============

Developed using Python 2.7, Django 1.8, and PostgreSQL 9.3 on Ubuntu 14.04.


API
===

The current production Obento endpoint is at http://gwbento-prod.wrlc.org:8080 .  This can only be accessed directly from within the GW network.

Query API
---------

Query API endpoints are as follows:

`/` - returns a results page with six boxes of results (seven if Best Bets contains a result)

`/articles_html` - returns an HTML page with only the articles results

`/articles_json` - returns article results as JSON

`/books_media_html` - returns an HTML page with only the books & media results (wrapper for `/launchpad_html`)

`/books_media_json` - returns books & media results as JSON (wrapper for `/launchpad_json`)

`/databases_solr_html` - returns an HTML page with database results retrieved by querying Solr

`/databases_solr_json` - returns database results retrieved by querying Solr, as JSON

`/journals_solr_html` - returns an HTML page with journal title results retrieved by querying Solr 

`/journals_solr_json` - returns journal title results retrieved by querying Solr, as JSON

`/launchpad_html` - returns an HTML page with launchpad query results

`/launchpad_json` - returns launchpad query results as JSON

`/summon_html` - returns an HTML page with Summon query results with a scope of `all` as defined in settings

`/summon_json` - returns Summon query results as JSON, with a scope of `all` as defined in settings

`/summon_books_media_html` - returns an HTML page with Summon query results with a scope of `books_media` as defined in settings

`/summon_books_media_json` - returns Summon query results as JSON, with a scope of `books_media` as defined in settings

`/research_guides_html` - returns an HTML page with Summon query results with a scope of `research_guides` as defined in settings

`/research_guides_json` - returns Summon query results as JSON, with a scope of `research_guides` as defined in settings

`/best_bets_html` - returns an HTML page with Summon query results with a scope of `best_bets` as defined in settings

`/best_bets_json` - returns Summon query results as JSON, with a scope of `best_bets` as defined in settings

`/libsite_html` - returns an HTML page with library website query results

`/libsite_json` - returns library website query results as JSON


**Request parameters** for the Query endpoints are as follows:

*q* (optional): query string, e.g.  http://gwbento-prod.wrlc.org:8080?q=computer+science

*count* (optional): the number of results to return in each box, e.g. http://gwbento-prod.wrlc.org:8080?q=computer+science&count=4 .  This overrides the default value configured `in local_settings.py`.

*ignoresearch* (optional): if `true`, do not record the query in the Searches table, e.g. http://gwbento-prod.wrlc.org:8080?q=computer+science&ignore=true .  If this parameter is not specified, the query will be recorded.

Searches API
------------

`/searches` - returns an HTML page containing:
* a paginated table of recorded queries
* a list of the terms most frequently queried in the recent period

**Request parameters** for the Searches endpoint are as follows:

* *token* (required):  the secret token required to access the /searches endpoint.
* *last_n_days* (optional):  the number of days worth of searches (from the present date back) to aggregate in the "top searches" list
* *top_n_searches* (optional):  the number of top searches to list in the "top searches" list
* *page* (optional): pagination page
* *per_page* (optional): number of results per paginated page
* *sortby* (optional): primary column to sort by.  `-` prefix indicates reverse sort.  Sorting can also be accomplished by clicking on the column header.  Values may include:
   * `q` / `-q`  sort by query text
   * `date_searched` / `-date_searched`
   * `articles_count` / `-articles_count`
   * `books_count` / `-books_count`
   * `database_count` / `-database_count`
   * `journals_count` / `-journals_count`
   * `researchguides_count` / `-researchguides_count`






Installation Instructions
=========================

PART I - Basic server requirements
----------------------------------

1. Install Apache, OpenJDK8 and other dependencies

        $ sudo apt-get install apache2 libapache2-mod-wsgi libaio-dev python-dev python-profiler postgresql postgresql-contrib libpq-dev git libxml2-dev libxslt-dev python-setuptools python-virtualenv

        $ sudo add-apt-repository ppa:openjdk-r/ppa

        $ sudo apt-get update 
    
        $ sudo apt-get install openjdk-8-jdk	

2. Install Chrome and ChromeDriver (needed for loading and scraping the libguides databases list)

        $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        $ sudo dpkg -i google-chrome-stable_current_amd64.deb

   If you encounter errors related to missing dependencies, then use:

        $ sudo apt-get -f install

   Now proceed with ChromeDriver installation:

        $ sudo apt-get install unzip
        $ wget https://chromedriver.storage.googleapis.com/2.38/chromedriver_linux64.zip
        $ unzip chromedriver_linux64.zip
        $ sudo mv chromedriver /usr/local/bin
        $ sudo chown root:root /usr/local/bin/chromedriver

3. Prepare Java JVM symlink for Jetty

   Create a symlink to the java jvm

        $ sudo mkdir /usr/java

        $ sudo ln -s /usr/lib/jvm/java-8-openjdk-amd64 /usr/java/default

4. Download Jetty and unzip.  

        $ cd /opt

   Go to http://www.eclipse.org/jetty/download.html and copy the link to the .tar.gz version of the latest download of Jetty 9.  Use this link in the following wget command to download the .tar.gz file (again, the URL may change):

        $ sudo wget -O jetty.gz "http://central.maven.org/maven2/org/eclipse/jetty/jetty-distribution/9.4.2.v20170220/jetty-distribution-9.4.2.v20170220.tar.gz"

        $ sudo mkdir jetty

        $ sudo tar -xvf jetty.gz -C jetty --strip-components=1

5. Create jetty user and make it the owner of /opt/jetty

        $ sudo useradd jetty -U -s /bin/false

        $ sudo chown -R jetty:jetty /opt/jetty

6. Set up jetty to run as a service

        $ sudo cp /opt/jetty/bin/jetty.sh /etc/init.d/jetty

7. Create the jetty settings file
  
        $ sudo vi /etc/default/jetty

   Paste the following into the file, and save it:

        JAVA=/usr/bin/java
        NO_START=0                 # Start on boot
        JETTY_HOST=0.0.0.0         # Listen to all hosts
        JETTY_ARGS=jetty.port=8983
        JETTY_USER=jetty           # Run as this user
        JETTY_HOME=/opt/jetty

    In production, jetty should be running on a port that won't be publicly exposed.  In development and testing, exposing Solr might be helpful; never expose it in production.
    
    NOTE:  In the step above, JAVA is set to /usr/bin/java.  When upgrading from an environment that had Java 7 installed, /usr/bin/java may be a symbolic link (...to another symbolic link) which still points to a Java 7 JRE.  If that is the case, reconfigure to ensure that either /usr/bin/java resolves to a Java 8 JRE, or point JAVA in the jetty config file to wherever the Java 8 JRE is.

8. Start jetty

        $ sudo service jetty start

   This should return something that starts with:

        Starting Jetty: OK

   A possible cause for a failed Jetty start is that `/var/run/jetty` and contents may need to be owned by the jetty user.  To set `jetty:jetty` as the owner, use `sudo chown jetty:jetty /var/run/jetty`

   Verify that MYSERVER:8983 returns a page that is "Powered by Jetty" (even if it is a 404-Not Found page) 

9. Add jetty to startup

        $ sudo update-rc.d jetty defaults

10. Download and unzip solr

   Go to http://archive.apache.org/dist/lucene/solr/4.10.4/ and copy the link to the .tgz version of Solr 4.10.4.  Use this link in the following wget command to download the .tgz file (again, the URL may change).  This may also require a --no-check-certificate option as well, depending on the download site:

        $ sudo wget -O solr.gz "http://archive.apache.org/dist/lucene/solr/4.10.4/solr-4.10.4.tgz"

        $ sudo tar -xvf solr.gz

    Copy solr contents:

        $ sudo cp -r solr-4.10.4/example/solr /opt

        $ sudo cp -r solr-4.10.4/dist /opt/solr

        $ sudo cp -r solr-4.10.4/contrib /opt/solr

    Copy ICU Tokenizer jars to /opt/solr/lib

        $ sudo mkdir /opt/solr/lib

        $ sudo cp /opt/solr/contrib/analysis-extras/lib/icu4j-*.jar /opt/solr/lib

        $ sudo cp /opt/solr/contrib/analysis-extras/lucene-libs/lucene-analyzers-icu-* /opt/solr/lib

11. Copy solr .war and .jar files to jetty

        $ sudo cp /opt/solr/dist/solr-4.10.4.war /opt/jetty/webapps/solr.war

        $ sudo cp solr-4.10.4/example/lib/ext/* /opt/jetty/lib/ext

    Ensure that these are now owned by jetty:

        $ sudo chown -R jetty:jetty /opt/jetty

12. Update jetty settings

        $ sudo vi /etc/default/jetty

    Append the following line:

        JAVA_OPTIONS="-Dsolr.solr.home=/opt/solr $JAVA_OPTIONS"
    
13. Change the owner of the solr folder and contents to jetty
        
        $ sudo chown -R jetty:jetty /opt/solr

14. Change ``collection1`` in solr to ``obento``:

        $ cd /opt/solr
            
        $ sudo mv collection1 obento

    Replace ``name=collection1`` with ``name=obento`` in core.properties:
            
        $ sudo vi obento/core.properties
            
15. Restart jetty

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

5. Upgrade to the latest pip and install project dependencies

        (ENV)$ pip install pip --upgrade
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

2. Update the values in the ```local_settings.py``` file:  for the database, ```NAME```, ```USER```, and ```PASSWORD``` to the database you created above, and set ```ENGINE``` to 'postgresql_psycopg2'; also, set a ```SECRET_KEY```.  Ensure that the port number in ```SOLR_URL``` matches ```JETTY_PORT``` configured earlier in ```/etc/default/jetty```. Provide a ```LOG_FILE_PATH``` and create a corresponding logs directory in the obento top directory.

        $ vi local_settings.py

3. Copy the WSGI file template to an active file

        $ cp wsgi.py.template wsgi.py

4. Update the wsgi.py file. (Uncomment the virtualenv settings starting with "import site" and Change the value of ENV to your environment path)

        $ vi wsgi.py
        
5. Initialize database tables. WARNING: Be sure you are still using your virtualenv. DO NOT create a superuser when prompted!

        (ENV)$ cd <OBENTO_HOME>/obento/obi
        (ENV)$ python manage.py migrate

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

    Now, rerun the migrate command.

        (ENV)$ python manage.py migrate

7. Copy the Apache virtual host file to the Apache2 directory

        $ cd /<OBENTO_HOME>/obento
        $ sudo cp apache/obento /etc/apache2/sites-available/obento.conf

8. Configure self signed SSL certificates. Refer https://github.com/gwu-libraries/SSL_HowTo



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

        $ ./manage.py index_databases

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

        $ ./manage.py index_journals

Test that indexing worked with this path:

        http://<OBENTO_URL>/journals_solr_html?q=science
        http://<OBENTO_URL>/journals_solr_json?q=science

The results should look different from the test above.

You may also wish to have a cron job reload (and reindex) the databases list on a
regular basis.  To accomplish this, you can add a line in your crontab similar to this:

       0 2 * * * <PATH TO YOUR APP>/obento/ENV/bin/python <PATH TO YOUR APP>/obento/obi/manage.py load_databases && <PATH TO YOUR APP>/obento/ENV/bin/python <PATH TO YOUR APP>/obento/obi/manage.py index_databases 

This would run ```load_databases```, then ```index_databases``` every night at 2:00 A.M.
