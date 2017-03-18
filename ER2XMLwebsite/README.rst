========================
ER2XML Schema Editor
========================

Features

#. Allow users to upload, edit, and delete ER models
#. Provide interactive editing function to generate XML schema from a ER model
#. Export XML schema as .xsd file and .dtd file (in progress)


Build instructions
==================

This website is developed using Django and SQLite. 

If the environment is not set, install Bitnami Djangostack with SQLite clicked.

Then run Use Bitnami Django Stack.

Go to the ER2XMLwebsite folder and run::

    $ pip install -r requirements.txt
    $ python manage.py migrate ER2XML
    $ python manage.py runserver

You can now visit the website at http://127.0.0.1:8000/.

For admin purpose, the account is
	
	username: hancheng
	password: cs4221er2xml