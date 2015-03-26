#!/usr/bin/python

import sys
import hashlib
import time
import random
import mysql.connector as mysql

TRIES = 10
DB_NAME = "GEOQUERY_CACHE"
TABLES = {}
TABLES['query'] = (
        "CREATE TABLE IF NOT EXISTS `query` ("
        "   `hash` varchar(255) NOT NULL,"
        "   `query` text NOT NULL,"
        "   `result` text NOT NULL,"
        "   PRIMARY KEY (`hash`)) ENGINE=InnoDB"
)

def hash_q(query):
    return str(hashlib.sha224(b"%s" % (query)).hexdigest())

def parse_config(config_file):
    ret_dict = {}
    with open(config_file) as c_p:
        for line in c_p:
            line = line.strip().split("\t")
            ret_dict[line[0]] = line[1]
    return ret_dict

class MySql:
    # Init DB
    def __init__(self,config):
        config = parse_config(config)
        self.username = config["user"]
        self.password = config["password"]
        self.host = config["host"]

        # Initiate database
        try:
            db = mysql.connect(user=config["user"], password=config["password"], host=config["host"])
            cursor = db.cursor()
        
            try:  
                cursor.execute("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET 'utf8'" % (DB_NAME))
                db.database = DB_NAME
                for name, ddl in TABLES.items():
                    cursor.execute(ddl)
            finally:    
                cursor.close()
                db.close()
        except:
            pass

    def connect(self):
        db = None
        i = 0
        try:
            db = mysql.connect(user=self.username, password=self.password, host=self.host, database=DB_NAME)
        except:
            pass
        return db
    
    def write(self,query,result):
        db = self.connect()
        if db is None:
            return
        
        cursor = db.cursor()
        try:
            add_query = ("INSERT IGNORE INTO `query`" 
                "(hash, query, result) VALUES (%s, %s, %s)")
    
            query_data = (hash_q(query), query, result)
    
            cursor.execute(add_query, query_data)
            db.commit()
        finally:
            db.close()
            cursor.close()
    
    def read(self,query):
        db = self.connect()
        if db is None:
            return None

        cursor = db.cursor()
        try:
            select_query = ("SELECT q.result FROM `query` AS q WHERE q.hash = \"%s\"" % hash_q(query))
            cursor.execute(select_query)
            
            result = [data for data in cursor]
            if len(result) > 0:
                return result[0][0]
            else:
                return None
        finally:
            cursor.close()
       
