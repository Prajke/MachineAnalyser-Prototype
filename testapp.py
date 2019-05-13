import application as app
import pandas as pd
import database_helper as dbh
import time
import timeit


data = pd.read_csv("exData.csv")
db = dbh.database()

#print(db.getComponent(0))
#dict = data.to_dict('list')
#start= time.time()
#list = data.values.tolist()
#print(list)
#db.insertcsv(list)
#for item in list:
#    db.insert(item)
#elapsed = time.time() - start
#print("Total time: " +  str(elapsed))
#print(app.summarize_components(machinedata).head(10))
#start= time.time()
#print("Machine completness : " + str(app.MachineAnalyse(machinedata)))

#elapsed = time.time() - start
#print("Total time: " +  str(elapsed))


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

#datapool = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/rawdatapool.xlsx")
#datapool = app.summarize_components(datapool)
#datapool.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/datapool.xlsx")

machinedata = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E1_v2.xlsx")
wrapped =wrapper(app.MachineAnalyse, machinedata)
py=timeit.timeit(wrapped, number = 1)
print("Time: " +str(py))
