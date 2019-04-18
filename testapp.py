import application as app
import pandas as pd
import database_helper as dbh

data = pd.read_csv("machine.csv")

db = dbh.database()

#print(db.getComponent(0))
machinedata = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E1.xlsx")
print(app.MachineAnalyse(machinedata))
