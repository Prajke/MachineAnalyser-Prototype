import application as app
import pandas as pd
import database_helper as dbh
import time

data = pd.read_csv("machine.csv")
db = dbh.database()
#print(db.getComponent(0))


machinedata = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E1.xlsx")
start= time.time()
print("Machine completness : " + str(app.MachineAnalyse(machinedata)))
elapsed = time.time() - start
print("Total time: " +  str(elapsed))
