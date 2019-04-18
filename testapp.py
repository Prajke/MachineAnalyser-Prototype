import application as app
import pandas as pd
import database_helper as dbh

data = pd.read_csv("machine.csv")

db = dbh.database()

#print(db.getComponent(0))
print(app.MachineAnalyse(data))
