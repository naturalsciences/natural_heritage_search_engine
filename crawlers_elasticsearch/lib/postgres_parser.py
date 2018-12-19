import sys 
import linecache
import psycopg2
import psycopg2.extras
import ConfigParser
import datetime


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

class PostgresParser(object):

    def __init__(self ):
        self.m_inifile="/var/developments/crawlers_elasticsearch/lib/App.ini"
        self.m_conn = None
        self.m_curs = None
        appConfig = ConfigParser.ConfigParser()
        appConfig.read(self.m_inifile)
        self.HOST = appConfig.get("DatabaseServer", "host")
        self.USER = appConfig.get("DatabaseServer", "user")
        self.PORT = appConfig.get("DatabaseServer", "port")
        self.PASSWORD = appConfig.get("DatabaseServer", "password")
        self.DATABASE = appConfig.get("DatabaseServer", "database")
        self.initconn()
        
    def initconn(self):
        try:
            self.m_conn= psycopg2.connect(host=self.HOST, dbname=self.DATABASE, port=self.PORT, user= self.USER, password=self.PASSWORD)
            self.m_curs = self.m_conn.cursor()
        except Exception, e:
            PrintException()
            return

        
    def log_json_row(self, url, json_data):
        try:
            self.m_curs.execute('INSERT INTO copy_elastic_search_document (url, document_data ) VALUES (%s, %s) ON CONFLICT (url) DO UPDATE SET document_data = %s, update_date=%s ', (url, psycopg2.extras.Json(json_data), psycopg2.extras.Json(json_data), datetime.datetime.now()))
            self.m_conn.commit()
        except Exception, e:
            self.m_conn.rollback()
            print 'FAILED TO INSERT JSON '.format(str(json_data))
            PrintException()
        
        
