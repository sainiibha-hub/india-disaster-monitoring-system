"""
Using PyMySQL as a drop-in replacement for mysqlclient.

Django's default MySQL backend expects the `MySQLdb` package (mysqlclient),
which needs a C compiler to install on Windows. PyMySQL is pure Python and
installs anywhere with a plain `pip install pymysql`, and can impersonate
MySQLdb with the two lines below -- so Django's stock `django.db.backends.mysql`
engine works unmodified.
"""
import pymysql

pymysql.install_as_MySQLdb()
