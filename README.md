**Obento ReadMe**


1.  **Installing dependencies**

$ sudo apt-get install apache2 libapache2-mod-wsgi libaio-dev python-dev
python-profiler postgresql postgresql-contrib libpq-dev git libxml2-dev
libxslt-dev


2.  **Installing Jetty**

    1.  Install jdk

$ sudo apt-get install openjdk-7-jdk


2.  Create a symlink for easier reference from jetty

$ sudo mkdir /usr/java

$ sudo ln -s /usr/lib/jvm/java-7-openjdk-amd64 /usr/java/default

\

3.  Go to opt directory

$ cd /opt


4.  Download Jetty and unpack the archive

$ sudo wget
"[http://eclipse.org/downloads/download.php?file=/jetty/stable-9/dist/jetty-distribution-9.2.2.v20140723.tar.gz&r=1](http://eclipse.org/downloads/download.php?file=/jetty/stable-9/dist/jetty-distribution-9.2.2.v20140723.tar.gz&r=1)"


$ sudo mv
download.php\\?file\\=%2Fjetty%2Fstable-9%2Fdist%2Fjetty-distribution-9.2.2.v20140723.tar.gz\\&r\\=1
jetty-distribution-9.2.2.v20140723.tar.gz


$ sudo tar -xvf jetty-distribution-9.2.2.v20140723.tar.gz


$ sudo mv jetty-distribution-9.2.2.v20140723 jetty


5.  Create jetty user and make it the owner of /opt/jetty

$ sudo useradd jetty -U -s /bin/false

$ sudo chown -R jetty:jetty /opt/jetty


6.  Copy Jetty Script to run as a service

$ sudo cp /opt/jetty/bin/jetty.sh /etc/init.d/jetty


7.  Create settings file for jetty

$ sudo vi /etc/default/jetty


\#add the following to the file

JAVA=/usr/bin/java \# Path to Java

NO\_START=0 \# Start on boot

JETTY\_HOST=0.0.0.0 \# Listen to all hosts

JETTY\_ARGS=jetty.port=8983

JETTY\_USER=jetty \# Run as this user

JETTY\_HOME=/opt/jetty


8.  Start Jetty

$ sudo service jetty start


9.  Check status

$ sudo service jetty check


10. Add jetty to start up

$ sudo update-rc.d jetty defaults


11. Reboot the system

$ sudo reboot


12. Check jetty's status

$ sudo service jetty check



3.  **Installing Solr**

    1.  Goto opt directory

cd /opt


2.  Download and unpack solr

$ sudo wget
"[http://www.motorlogy.com/apache/lucene/solr/4.9.0/solr-4.9.0.tgz](http://www.motorlogy.com/apache/lucene/solr/4.9.0/solr-4.9.0.tgz)"

$ sudo tar -xvf solr-4.9.0.tgz


3.  Copying solr dir and other contents

$ sudo cp -R solr-4.9.0/example/solr /opt

$ sudo cp -r /opt/solr-4.9.0/dist /opt/solr

$ sudo cp -r /opt/solr-4.9.0/contrib /opt/solr


4.  Copying .war and .jar files to jetty

$ sudo cp solr-4.9.0/dist/solr-4.9.0.war /opt/jetty/webapps/solr.war


$ sudo cd /opt/solr-4.9.0/example/lib/ext

$ sudo cp jcl-over-slf4j-1.7.6.jar log4j-1.2.17.jar
slf4j-log4j12-1.7.6.jar jul-to-slf4j-1.7.6.jar slf4j-api-1.7.6.jar
/opt/jetty/lib/ext/


5.  Update jetty settings

$ sudo vi /etc/default/jetty

\#add the following after the last line

JAVA\_OPTIONS="-Dsolr.solr.home=/opt/solr $JAVA\_OPTIONS"


6.  Change owner of solr folder to jetty

$ sudo chown -R jetty:jetty /opt/solr


7.  Change “collection1” in solr to “obento”

$ cd /opt/solr

$ sudo mv collection1 obento

$ sudo vi obento/core.properties

\#replace collection1 with obento

name=obento



4.  **Installing Obento**

    1.  **Set up Postgresql**

        1.  Create a user for django (and make a note of the password
            you create). A name for MYDBUSER might be something like
            obentouser\_m1 (m1 for milestone 1)

$
`sudo -u postgres createuser --createdb --no-superuser --no-createrole --pwprompt MYDBUSER`{.western}


2.  `Create             a database for the obento application. A name for MYDBNAME might             be something like obi_m1`{.western}

`$ sudo -u postgres createdb -O MYDBUSER MYDBNAME`{.western}


2.  **Set up project environment**

    1.  Install virtualenv

$ sudo apt-get install python-setuptools

$ sudo easy\_install virtualenv


2.  Create a directory for your projects (replace <OBENTO\_HOME\> with
    your desired directory path and name: for instance /obento or
    /home/<username\>/obento )

$ mkdir <OBENTO\_HOME\>

$ cd <OBENTO\_HOME\>


3.  Pull down the project from github

(GW staff only)

$ git clone git@github.com:gwu-libraries/obento.git


(everyone else)

$ git clone
[https://github.com/gwu-libraries/obento.git](https://github.com/gwu-libraries/obento.git)


4.  Create virtual Python environment for the project

$ cd <OBENTO\_HOME\>/obento

$ virtualenv --no-site-packages ENV


5.  Activate your virtual environment

$ source ENV/bin/activate


6.  Install django, tastypie, and other python dependencies

(ENV)$ pip install -r requirements.txt


If the previous step encounters problems installing pytz, then it can be
installed as follows

(ENV)$ easy\_install --upgrade pytz


3.  **Configure your installation**

    1.  Copy the local settings template to an active file

$ cd obento/obi/obi

$ cp local\_settings.py.template local\_settings.py


2.  Update the values in the local\_settings.py file: for the database,
    NAME, USER, and PASSWORD to the database you created above, and set
    ENGINE to 'postgresql\_psycopg2'; also, set a SECRET\_KEY. Ensure
    that the port number in SOLR\_URL matches JETTY\_PORT configured
    earlier in /etc/default/jetty.


$ vim local\_settings.py


3.  Copy the WSGI file template to an active file

$ cp wsgi.py.template wsgi.py


4.  Update the wsgi.py file. (Change the value of ENV to your
    environment path)

$ vim wsgi.py


5.  Initialize database tables. WARNING: Be sure you are still using
    your virtualenv. DO NOT create a superuser when prompted!

(ENV)$ cd <OBENTO\_HOME\>/obento/obi

(ENV)$ python manage.py syncdb


If you encounter an authentication error with postgresql edit your
local\_settings.py file and set HOST = 'localhost'


If you encounter an error during the above command that ends with:


TypeError: decode() argument 1 must be string, not None

Then you need to add location values to your profile. Open your .bashrc
file in an editor:


$ vim \~/.bashrc

Enter the following values at the end of the file and save.


export LC\_ALL=en\_US.UTF-8

export LANG=en\_US.UTF-8

Now, reload your bashrc changes


source \~/.bashrc

Now, rerun the syncdb command


6.  Migrate the database to the latest updates

$ python manage.py migrate


4.  **Start the server**

    1.  Copy the Apache virtual host file to the Apache2 directory

$ cd /<OBENTO\_HOME\>/obento

$ sudo cp apache/obento /etc/apache2/sites-available/obento


2.  Update the values in the Apache virtual host file.

Edit the host port number Edit your server name (base url) Edit the many
instances of <path to OBENTO\_HOME\>. Beware: the line for the WSGI
Daemon has two references to that path.

$ sudo vim /etc/apache2/sites-available/obento


To change all of the path values at once use the global replace command
in vim

~~~ {.western}
:%s/old_value/new_value/g
~~~


3.  Enable the apache headers module, this is required for CORS support.

$ sudo a2enmod headers


4.  Enable the new virtualhost. If you are using port 80 also disable
    the default host


$ sudo a2ensite obento

$ sudo a2dissite default

$ sudo /etc/init.d/apache2 restart


Visit the site from the browser. If it displays an error(500) change the
access permission of the logfile.log (path specified in
local-settings.py)


5.  **Load some data**

    1.  Copy the conf folder to obento dir in solr

$ sudo cp -r cd /<OBENTO\_HOME\>/obento/obi/obi/conf /opt/solr/obento/


2.  To load GW's list of databases from libguides, first configure
    local\_settings.py with a list of libguides page sids


3.  Load/parse/add databases from these pages to the database:

$ ./manage.py load\_databases


To verify that the databases loaded, try querying the html or json view:

http://<OBENTO\_URL\>/databases\_html?q=proquest

http://<OBENTO\_URL\>/databases\_json?q=proquest


4.  To index the list of databases in Solr:

$ ./manage.py index\_all


Test that indexing worked with this path:

http://<OBENTO\_URL\>/databases\_solr\_html?q=proquest

http://<OBENTO\_URL\>/databases\_solr\_json?q=proquest


The results should look different from the test above.


5.  To load the Excel-formatted extract of journal titles:

$ ./manage.py load\_journals <JOURNALS\_EXCEL\_FILE\>


To verify that the journal titles loaded, try querying the html or json
view:

http://<OBENTO\_URL\>/journals\_html?q=science

http://<OBENTO\_URL\>/journals\_json?q=science


6.  To index the list of journals in Solr:

$ ./manage.py index\_all


Test that indexing worked with this path:

http://<OBENTO\_URL\>/journals\_solr\_html?q=science

http://<OBENTO\_URL\>/journals\_solr\_json?q=science


The results should look different from the test above.


