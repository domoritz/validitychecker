Climate Goggles
===============
-- protect your brain from climate fiction

## How to use

### Version 1
#### Dependencies
* [Python 2.7](http://python.org/)
* [Django](https://www.djangoproject.com/)
* [Beautiful soup](http://www.crummy.com/software/BeautifulSoup/)
* [lxml](http://lxml.de/)
* [SQLite](http://www.sqlite.org/) or any other relational database that is supported by django


#### Installation
Just in case you have no idea how to get going here are the required commands for Ubuntu:
    
    git clone git@github.com:lehmannro/validitychecker.git
    sudo apt-get install python python-pip python-dev sqlite3
    sudo pip install django
    sudo pip install beautifulsoup
    sudo pip install lxml
    cd validitychecker/www/
    python manage.py syncdb --noinput
    python manage.py runserver

### Version 2
#### Dependencies
* [Python 2.7](http://python.org/)
* [Django](https://www.djangoproject.com/)
* [SQLite](http://www.sqlite.org/) or any other relational database that is supported by django
* [Redis](http://redis.io/) or rabbitMQ as a celery broker

Full list of required Python packages can be found in www/devel-req.txt. Install them with:

    pip install -r www/devel-req.txt

#### Installation
This Version requires a little bit more work that version 1 since it is more powerful.

    git clone git@github.com:domoritz/validitychecker.git
    git co develop
    sudo apt-get install python python-pip python-dev sqlite3 redis
    # use virtualenv if possible!
    pip install -r devel-req.txt
    cd validitychecker/www/bin/
    python manage.py syncdb --noinput
    python manage.py migrate

#### Run
Run these three command in different sessions on your command line

    # start redis
    redis-server /usr/local/etc/redis.conf

    # run celery
    python manage.py celeryd -l INFO -E

    # run django
    python manage.py runserver

#### Monitor celery tasks

    # on the command line
    python manage.py celeryev --frequency=1.0

    # run celerycam for monitoring tasks in django admin
    python manage.py celerycam


#### Run tests

    python manage.py test validitychecker -v 2


## Documentation
* [Wiki](/domoritz/validitychecker/wiki)

## Problem
* It is difficult for normal people to classify the background of scientific statements and what is serious. 
* Climate change is a very complex subject with a  lot of misinformation circulating. 
* This misinformation creates uncertainty. 
* Some incorrect information is scattered by climate skeptics, with the aim to sow doubt and ultimately to prevent climate protection.
* [Problem definition](http://www.rhok.org/problems/validity-detectorchecker-aggregation-and-validation-statements-about-climate-change-deen)

## Challenges
* Sorting and ranking scientific papers is hard
* Scientific papers are written in technical language
* Few resources provide proper APIs

## Solution
* User enters search query
* Lookup on Google Scholar
* Match the authors against ISI
* Compute a score for the authors
* Find easy-to-read resources of the author
* [Description of our solution on the RHoK website](http://www.rhok.org/solutions/climate-goggles)

## User expierience
* The user experience is designed to be simple

* Seamless browser integration with Greasemonkey script
* Available in English and German
* Adaptive Design for smaller screen sizes

## Remaining issues
* Register for the ISI Web of Knowledge API and implement the hooks
* Digestible article summaries 

## Team


### Backend
* [Robert Lehmann](https://github.com/lehmannro/)
* [Dominik Moritz](https://github.com/domoritz/)
* [André Rieck](https://github.com/Varek/)
* [Thomas Werkmeister](https://github.com/lesnail/)

### Frontend
* [David Owens](https://github.com/fineartdavid/)
* [Norman Rzepka](https://github.com/normanrz/)
* [Dominik Moritz](https://github.com/domoritz/)

### Design
* [Milena Glim](https://github.com/milenskaya/)

## Stuff we used
* [Google Scholar](http://scholar.google.com/)
* [ISI Web of Knowledge](http://apps.isiknowledge.com/)
* [Arvo Font](http://www.fontsquirrel.com/fonts/arvo)
* ...

