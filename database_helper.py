###########################################################################
#This file contains functions for handling the referencelibrary.          #
#                                                                         #
#                                                                         #
############################################################################
import sqlite3, json

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
################################################################################
    #Validates if a componet exisits in the referencelibrary. If the component
    #exsists the function returns True, otherwise False.
    def validateComponent(self, cid):
        try:
            sql = "SELECT * FROM components WHERE cid = ?"
            val = (int(cid),)
            self.cursor.execute(sql,val)
            row = self.cursor.fetchone()
            if row == None:
                return False
            else:
                return True
        except:
            return 0

################################################################################
################################################################################
    #Validates a components bounderies. If the bounderies are within the
    #bounderies set in the referencelibrary, the function returns True,
    #otherwise false.
    def validateBounderies(self, cid, data):
        try:
            component = self.getComponent(cid)

            if ( (int(data["documents"]) >= component["minDoc"] and int(data["documents"]) <= component["maxDoc"]) and
                 (int(data["bomitem"]) >= component["minBom"] and int(data["bomitem"]) <= component["maxBom"]) and
                 (int(data["children"]) >= component["minChild"] and int(data["children"]) <= component["maxChild"])):

                return True
            else:
                return False
        except:
            raise Exception("Error at validateBounderies")

################################################################################
################################################################################
    #Adds a component to the referencelibrary.
    def addComponent(self,data):
        #try:
            sql = "REPLACE INTO components(cid, meanDoc,meanBom,meanChild,maxDoc,maxBom,maxChild,minDoc,minBom,minChild,nrComponents) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
            values = (data['cid'], data['meanDoc'],data['meanBom'],data['meanChild'],data['maxDoc'],data['maxBom'],data['maxChild'],data['minDoc'],data['minBom'],data['minChild'],data['nrComponents'])
            self.cursor.execute(sql,values)
            self.db.commit()
            return True
        ##except:
        #    return 0

################################################################################
################################################################################
    #Extracts a component from the referencelibrary. Returns a dictionary
    #containg component bounderies and mean-values for the different features.
    def getComponent(self, cid):
        try:
            sql = "SELECT * FROM components WHERE cid = ?"
            val = (cid,)
            self.cursor.execute(sql, val)
            row = self.cursor.fetchone()
            if row == None:
                Component = []
                return Component
            Component = {
                "cid":row[0],
                "maxBom":row[1],
                "minBom": row[2],
                "meanBom": row[3],
                "maxChild": row[4],
                "minChild": row[5],
                "meanChild": row[6],
                "maxDoc": row[7],
                "minDoc": row[8],
                "meanDoc": row[9],
                "nrComponents": row[10]
            }
            return Component
        except:
            raise Exception("Error at GetComponent")


################################################################################
################################################################################
    def validateComponentAmount(self,cid,var):
        try:
            sql = "SELECT nrComponents FROM components WHERE cid = ?"
            val = (int(cid),)
            self.cursor.execute(sql,val)
            row = self.cursor.fetchone()
            if row[0] < var:
                return True
            else:
                return False
        except:
            return 0
################################################################################
################################################################################
    def changeComponentBounderies(self):
        print( "HELLO")

################################################################################
################################################################################
    def insertAnonmaly(self, cid):
        try:
            sql = "INSERT INTO anomalies(cid) VALUES(?)"
            values = (cid)
            self.cursor.execute(sql,values)
            return True
        except:
            return 0
################################################################################
################################################################################
    def getAnomalies(self, cid=None):
        if (cid==None):
            sql = "SELECT * FROM anomalies"
        else:
            sql = "SELECT * FROM anomalies WHERE cid = ?"
        try:
            val = (cid)
            self.cursor.execute(sql,val)
            data = self.cursor.fetchall()
            return data
        except:
            return 0
################################################################################
################################################################################
    def deleteAnomalies(self, cid=None ):
        if(cid==None):
            sql= "TRUNCATE TABLE anomalies"
        else:
            sql = "DELETE FROM anomalies WHERE cid = ?"
        try:
            val = (cid)
            self.cursor.execute(sql,val)
            data = self.cursor.fetchall()
            return True
        except:
            return 0

    def insertList(self, list):
        sql = "REPLACE INTO components(cid, maxBom,minBom, meanBom,maxChild, minChild, meanChild,maxDoc,minDoc,meanDoc,nrComponents) VALUES(?,?,?,?,?,?,?,?,?,?,?) "
        self.cursor.executemany(sql, list)
        self.db.commit()
