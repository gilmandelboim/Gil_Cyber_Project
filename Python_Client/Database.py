import sqlite3 
import sys


NAME_DB = "RemoteViewerClient.db"


class Database(object):

    def __init__(self):
        self.con = sqlite3.connect(NAME_DB)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS Words(Id INT, Name TEXT, Category INT, Quantity INT)")

    def  exec_query(self, query):
         #  cur.executemany("INSERT INTO Cars VALUES(?, ?, ?)", cars)
        self.cur.execute(query)

    def  insert(self, table_name, data):
        query = "INSERT INTO " + table_name + " VALUES(?, ?, ?, ?)"
        self.cur.executemany(query, data)

    def  get_rows(self, table_name):
        self.cur.execute("SELECT * FROM " + table_name)
        rows = self.cur.fetchall()
        return  rows

    def  printTable(self, table_name):
        rows = self.get_rows(table_name)
        for row in rows:
            print row

    def get_dict_from_table(self,table_name):
        ''' Turn a list with sqlite3.Row objects into a dictionary'''
        dict ={} # the dictionary to be filled with the row data and to be returned

        for i, row in enumerate(self.get_rows(table_name)): # iterate throw the sqlite3.Row objects
            fields = [] # for each Row use a separate list
            for col in range(0, len(row)): # copy over the row date (ie. column data) to a list
                fields.append(row[col])
            dict[fields[1]] = (fields[2], fields[3]) # add the list to the dictionary
        return dict

    def set_dict_to_table(self,table_name,dict):
        keys = ','.join(dict.keys())
        i = 1
        for word in dict.keys():
            value = dict[word]
            self.cur.execute("INSERT INTO "+ table_name +" VALUES (" + str(i) + ",'" + word + "'," + str(value[0]) + "," + str(value[1]) + ")" )
            i+=1
        self.con.commit()
    def get_most_used_words(self,dict):
        dict= {i:dict[i] for i in dict if dict[i][1]>5}
        return dict

