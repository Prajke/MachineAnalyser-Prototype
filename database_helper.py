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
    def validateProduct(self, cid):
        try:
            sql = "SELECT * FROM products WHERE cid = ?"
            val = (cid,)
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
            component = self.getProduct(cid)
            if ( (data["doc"] >= component["minDoc"] or data["doc"] <= component["maxDoc"]) and
                 (data["pop"] >= component["minPop"] or data["pop"] <= component["maxPop"]) and
                 (data["child"] >= component["minChild"] or data["child"] <= component["maxChild"])):
                return True
            else:
                return False
        except:
            return 0

################################################################################
################################################################################
    #Adds a component to the referencelibrary.
    def addProduct(self,data):
        try:
            sql = "INSERT INTO products(cid, meanDoc,meanPop,meanChild,maxDoc,maxPop,maxChild,minDoc,minPop,minChild,nrComponents) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
            values = (data['cid'], data['meanDoc'],data['meanPop'],data['meanChild'],data['maxDoc'],data['maxPop'],data['maxChild'],data['minDoc'],data['minPop'],data['minChild'],data['nrComponents'])
            self.cursor.execute(sql,values)
            self.db.commit()
            return True
        except:
            return 0

################################################################################
################################################################################
    #Extracts a component from the referencelibrary. Returns a dictionary
    #containg component bounderies and mean-values for the different features.
    def getProduct(self, cid):
        try:
            sql = "SELECT * FROM products WHERE cid = ?"
            val = (cid,)
            self.cursor.execute(sql, val)
            row = self.cursor.fetchone()
            if row == None:
                product = []
                return product
            product = {
                "cid":row[0],
                "meanDoc":row[1],
                "meanPop": row[2],
                "meanChild": row[3],
                "maxDoc": row[4],
                "maxPop": row[5],
                "maxChild": row[6],
                "minDoc": row[7],
                "minPop": row[8],
                "minChild": row[9],
                "nrComponents": row[10]
            }
            return product
        except:
            return 0

################################################################################
################################################################################
    def validateComponentAmount(self,cid,var):
        try:
            sql = "SELECT * FROM products WHERE cid = ?"
            val = (cid,)
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
