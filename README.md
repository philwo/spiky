# Spiky - Speedy Wiki

Spiky was made by

* Philipp Wollermann - "Mit Django sind das nur vier Zeilen"
* Simon Franz - "Im Prinzip alles der gleiche Code"
* Benjamin Lieberwirth - "Der Rest ist geschenkt"
* Sebastian Sebald - "Ich hab grad noch schnell den CD-Ripper eingebaut"


# Introduction

Why Spiky? We actually don't have time to write some pages about our motivation,
because we're hard on the deadline (as always) ;)

(Update 2013-01-19: Spiky and this documentation were created in the year 2008 as part of a university course about
web development and haven't been updated since then.)

The ["Silk" icons](http://www.famfamfam.com/lab/icons/silk/) used in this project were made by Mark James (famfamfam) and are used under the
Creative Commons Attribution 2.5 License. This project uses the CSS framework [YAML 3.0.3](http://www.yaml.de/) by Dirk Jesse. YAML is licensed
under the Creative Commons Attribution 2.0 License.


# Requirements

* Linux (is the only OS we test on)
* Apache HTTPD 2.x with mod_rewrite, mod_wsgi (for production use) or mod_proxy (for development)
* [Django](http://www.djangoproject.com/) from SVN (0.96 will not work!)
* Python 2.5
* ExtJS 2.x (download it and put it into htdocs/extjs, tested with version 2.0.2 only)


# Installation

We assume that you want to host Spiky on the domain spiky.phorge.de and install Spiky in /var/www/spiky. Please adjust the configuration if you're installing it somewhere else.

## Clone from GitHub

    cd /var/www/
    git clone https://github.com/philwo/spiky.git

## Create a Virtualhost for your Apache

Please note the following: You will not want to serve the sourcecode, and thus you do
not just put everything into one DocumentRoot.

Instead take the following and apply changes specific for your server configuration.
The basic idea is: You have a directory where you install Spiky and then make
*selected* files / dirs available to Apache for serving to the users. That would be:

    # /MyPageName/			-> try to get the static version of the page MyPageName
    # /spiky/MyPageName/		-> everything in /spiky/ is handled by Django!
    # /static/cooldesign.css	-> static media files

    <VirtualHost *:80>
    ServerName spiky.phorge.de

    DocumentRoot /var/www/spiky/persistent/
    <Directory /var/www/spiky/persistent>
            AllowOverride None
            Order allow,deny
            allow from all
    </Directory>

    # We use utf-8
    AddDefaultCharset utf-8

    # Compress Javascript and CSS files
    AddOutputFilterByType DEFLATE text/css application/x-javascript

    # Optimize ETag
    FileETag MTime Size

    # Set the starting page of your Wiki
    DirectoryIndex Start

    # Unbelievable mod_rewrite tricks ahead. ;)
    # They basically do the following:
    # - Try to deliver the requested URL from the static compiled files
    # - If that file does not exist, rewrite to the dynamic URL to Spiky can handle it
    RewriteEngine on
    # Output existing static pages
    RewriteCond %{REQUEST_URI} !^/spiky/.*
    RewriteCond %{REQUEST_URI} !^/static/.*
    RewriteCond /var/www/spiky/persistent%{REQUEST_URI} !-d
    RewriteRule ^/(.+) http://spiky.phorge.de/spiky/$1 [L,QSA]
    # Well ...
    RewriteCond %{REQUEST_URI} !^/spiky/.*
    RewriteCond %{REQUEST_URI} !^/static/.*
    RewriteRule ^/(.+)/ /$1/text.htm [L,QSA]

    # Static files (media, css, js, ...)
    Alias /static/ /var/www/spiky/htdocs/
    <Directory /var/www/spiky/htdocs>
    		# Note! For full performance, specify these Expire-Headers.
    		# Warning: If you then change one of these files then you have to name
    		# them different, else the client will use the cached version!
            #ExpiresActive On
            #ExpiresByType text/css "access plus 1 month"
            #ExpiresByType application/x-javascript "access plus 1 month"
            #ExpiresByType image/png "access plus 1 month"
            #ExpiresByType image/gif "access plus 1 month"

            AllowOverride None
            Order allow,deny
            allow from all
    </Directory>

    # Using mod_wsgi (untested but should work)
    #WSGIScriptAlias /spiky /var/www/spiky/apache/django.wsgi
    #<Directory /var/www/spiky/apache>
    #       Order deny,allow
    #       Allow from all
    #</Directory>

    # Using mod_proxy to django devel server
    ProxyRequests Off
    <Proxy *>
            Order allow,deny
            Allow from all
    </Proxy>
    ProxyPass /spiky/ http://localhost:8000/ retry=0
    ProxyPassReverse /spiky/ http://localhost:8000/
    </VirtualHost>

3) Edit the settings: /var/www/spiky/spiky/settings.py

* Database host / user / password
* MEDIA_ROOT / MEDIA_URL (are the same as the "Static files (media, css, js, ...)" in the Apache config above)
* SPIKY_BASEURL, the Domain of your wiki (installation in Subdirectory is more difficult and untested...)
* SPIKY_CACHEPATH, the path to a directory where Spiky will store compiled Wikipages, must be writable by the Webserver!!!
* SERVER_EMAIL, DEFAULT_FROM_EMAIL (sender adresses for error reports, forgotten password reminders, etc.)
* TEMPLATE_DIRS (/var/www/spiky/templates)

4) Create the databases:

    cd /var/www/spiky/spiky
    python manage.py syncdb

5) Finished. These instructions were written from memory and may not be 100% complete. If anything
didn't work, please file an issue, kthx.

Now have fun with your new Wiki! :)


# License

Copyright (c) 2008 - 2013 by Philipp Wollermann, Simon Franz, Benjamin Lieberwirth, Sebastian Sebald

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Except as contained in this notice, the name(s) of the above copyright holders shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization.
