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
    def validateProduct(self, cid, rev):
        sql = "SELECT COUNT(1) FROM products WHERE cid = ? AND revison = ? "
        val = (cid, rev)
        self.cursor.execute(sql, val)
        row = self.cursor.fetchone()
        if row == 1:
            return True
        else:
            return False

################################################################################
################################################################################
    #Validates a components bounderies. If the bounderies are within the
    #bounderies set in the referencelibrary, the function returns True,
    #otherwise false.
    def validateBounderies(self, cid, rev, doc, pop, child):
        product = getProduct(self, cid, rev)
        if ( doc >= product["minDoc"] or doc <= product["maxDoc"] or
             pop >= product["minPop"] or pop <= product["maxPop"] or
             child >= product["minChild"] or child <= product["popChild"]):
            return True
        else:
            return False

################################################################################
################################################################################
    #Adds a component to the referencelibrary.
    def addProduct(self,data):
        print ("hej")

################################################################################
################################################################################
    #Extracts a component from the referencelibrary. Returns a dictionary
    #containg component bounderies and mean-values for the different features.
    def getProduct(self, cid, rev):
        sql = "SELECT * FROM products WHERE cid = ? AND revison = ? "
        val = (cid, rev)
        self.cursor.execute(sql, val)
        row = self.cursor.fetchone()
        if row == None:
            product = []
            return product
        product = {
            "cid":row[0],
            "revison":row[1],
            "meanDoc":row[2],
            "meanPop": row[3],
            "meanChild": row[4],
            "maxDoc": row[5],
            "maxPop": row[6],
            "maxChild": row[7],
            "minDoc": row[8],
            "minPop": row[9],
            "minChild": row[10]
        }
        return product
################################################################################
################################################################################
    def insertAnonmaly(self, cid, rev):
        try:
            sql = "INSERT INTO anomalies(cid, revison) VALUES(cid,rev)"
            self.cursor.execute(sql)
            return 1
        except:
            return 0
################################################################################
################################################################################
    def getAnomalies(self, cid=None, rev=None):
        if (cid==None or rev==None):
            sql = "SELECT * FROM anomalies"
        else:
            sql = "SELECT * FROM anomalies WHERE cid = ? AND revison = ? "
        try:
            val = (cid, rev)
            self.cursor.execute(sql,val)
            data = self.cursor.fetchall()
            return data
        except:
            return 0
################################################################################
################################################################################
    def deleteAnomalies(self, cid=None, rev=None ):
        if(cid==None or rev==None):
            sql= "TRUNCATE TABLE anomalies"
        else:
            sql = "DELETE FROM anomalies WHERE cid = ? AND revison = ?"
        try:
            val = (cid, rev)
            self.cursor.execute(sql,val)
            data = self.cursor.fetchall()
            return 1
        except:
            return 0
