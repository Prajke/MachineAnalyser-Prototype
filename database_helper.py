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
    def validateProduct(self, pid, rev):
        sql = "SELECT COUNT(1) FROM products WHERE pid = ? AND revison = ? "
        val = (pid, rev)
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
    def validateBounderies(self, pid, rev, doc, pop, child):
        product = getProduct(self, pid, rev)
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
    def getProduct(self, pid, rev):
        sql = "SELECT * FROM products WHERE pid = ? AND revison = ? "
        val = (pid, rev)
        self.cursor.execute(sql, val)
        row = self.cursor.fetchone()
        if row == None:
            product = []
            return product
        product = {
            "pid":row[0],
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
