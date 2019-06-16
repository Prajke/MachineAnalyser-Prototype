###########################################################################
#This file contains functions for handling the referencelibrary.          #
#                                                                         #
#                                                                         #
############################################################################
import sqlite3, json, datetime

class database:
################################################################################
    #Init database
    def __init__(self):
        self.db = sqlite3.connect("database.db", check_same_thread = False)
        self.cursor = self.db.cursor()

    def __exit__(self):
        self.commit()
        self.connection.close()

################################################################################
#Adds a single reference  to the referencelibrary.
################################################################################
    def addReference(self,data):
        try:
            sql = "REPLACE INTO components(matnr, meanDoc,meanBom,meanChild,maxDoc,maxBom,maxChild,minDoc,minBom,minChild,nrComponents) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
            values = (data['matnr'], data['meanDoc'],data['meanBom'],data['meanChild'],data['maxDoc'],data['maxBom'],data['maxChild'],data['minDoc'],data['minBom'],data['minChild'],data['nrComponents'])
            self.cursor.execute(sql,values)
            self.db.commit()
            return True
        except:
            raise Exception("Error at addComponent")
################################################################################
#Get a reference from the referencelibrary
################################################################################
    def getReference(self, matnr):
        try:
            sql = "SELECT * FROM components WHERE matnr = ?"
            val = (matnr,)
            self.cursor.execute(sql, val)
            row = self.cursor.fetchone()
            if row == None:
                Component = []
                return Component
            Component = {
                "matnr":row[0],
                "maxBom":row[1],
                "minBom": row[2],
                "meanBom": row[3],
                "maxChild": row[4],
                "minChild": row[5],
                "meanChild": row[6],
                "maxDoc": row[7],
                "minDoc": row[8],
                "meanDoc": row[9],
                "maxMat": row[10],
                "minMat": row[11],
                "meanMat": row[12],
                "nrComponents": row[13],
                "date": row[14]
            }
            return Component
        except:
            raise Exception("Error at GetComponent")

################################################################################
#Inserts a list of components defined as anomalies
################################################################################
    def insertAnomalies(self, list):
        try:
            sql = "INSERT INTO anomalies(matnr, bomitem, children, documents, materials, date) VALUES(?,?,?,?,?,?)"
            self.cursor.executemany(sql, list)
            self.db.commit()
        except:
            raise Exception("Error at GetComponent")
################################################################################
#Inserts a list of references
###############################################################################
    def insertList(self, list):
        try:
            sql =  "REPLACE INTO components(matnr, maxBom,minBom, meanBom,maxChild, minChild, meanChild,maxDoc,minDoc,meanDoc,maxMat,minMat,meanMat,nrComponents,date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            self.cursor.executemany(sql, list)
            self.db.commit()
        except:
            raise Exception("Error at insertList")
