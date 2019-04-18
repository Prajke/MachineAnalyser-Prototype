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
                 (int(data["leaves"]) >= component["minChild"] and int(data["leaves"]) <= component["maxChild"])):
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
            sql = "INSERT INTO components(cid, meanDoc,meanBom,meanChild,maxDoc,maxBom,maxChild,minDoc,minBom,minChild,nrComponents) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
            values = (data['cid'], data['MeanDocuments'],data['MeanBOMItem'],data['MeanLeaves'],data['MaxDocuments'],data['MaxBOMItem'],data['MaxLeaves'],data['MinDocuments'],data['MinBOMItem'],data['MinLeaves'],data['TotalComponents'])
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
            val = (int(cid),)
            self.cursor.execute(sql, val)
            row = self.cursor.fetchone()
            if row == None:
                Component = []
                return Component
            Component = {
                "cid":row[0],
                "meanDoc":row[1],
                "meanBom": row[2],
                "meanChild": row[3],
                "maxDoc": row[4],
                "maxBom": row[5],
                "maxChild": row[6],
                "minDoc": row[7],
                "minBom": row[8],
                "minChild": row[9],
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