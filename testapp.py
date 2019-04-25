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
def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

machinedata = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E1.xlsx")
#print(app.summarize_components(machinedata))
#start= time.time()
#print("Machine completness : " + str(app.MachineAnalyse(machinedata)))
wrapped =wrapper(app.MachineAnalyse, machinedata)
py=timeit.timeit(wrapped, number = 1)
#elapsed = time.time() - start
#print("Total time: " +  str(elapsed))
print("Time: " +str(py))


#LOAD DATA INFILE 'data.txt' INTO TABLE db2.my_table;
#FIELDS TERMINATED BY ','
#ENCLOSED BY '"'
#LINES TERMINATED BY '\r\n'
#IGNORE 1 LINES
#(col1, col2, col3, col4, col5...);
