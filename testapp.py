import application as app
import pandas as pd
import numpy as np
import database_helper as dbh
import time
import timeit


data = pd.read_csv("exData.csv")
db = dbh.database()

def generate_datapool(machinedata):
    uniquecid = machinedata["Material No."].unique()
    #print(uniquecid)
    datapool_df = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/CH86.xlsx")
    newdatapool_df = pd.DataFrame()
    for id in uniquecid:
        df = datapool_df[datapool_df['Material No.'] == id]
        #df = df[df['Equipment No'].apply(lambda x: x.isnumeric())]
        #print(df.head())
        #df['Equipment No'] = df['Equipment No'].astype(np.int64)
        newdatapool_df = pd.concat([newdatapool_df, df]).reset_index(drop = True)
    #datapool_df = app.summarize_components(datapool_df)
    newdatapool_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/rawdatapool_E4.xlsx")

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

machinedata = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E4.xlsx")

"""
df1 = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E_Scrambled_1_v2.xlsx")
df1 = df1.drop(columns= ['Model'], axis = 1)
df1.dropna(subset=['Material No.'], inplace=True)
uniqueeqnr = df1['Equipment No'].unique()
uniqueeqnr = uniqueeqnr[:2100]
fakemachine_df = pd.DataFrame()
for eqnr in uniqueeqnr:
    df = df1[df1['Equipment No'] == eqnr]
    fakemachine_df= pd.concat([fakemachine_df, df]).reset_index(drop = True)
fakemachine_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/fakemachine_df_v2.xlsx")

datapool_df = pd.DataFrame()
df1 = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E_Scrambled_1.xlsx")
df2 = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E_Scrambled_2.xlsx")
df3 = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E_Scrambled_3.xlsx")
df4 = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E_Scrambled_4.xlsx")
datapool_df = pd.concat([datapool_df, df1]).reset_index(drop = True)
datapool_df = pd.concat([datapool_df, df2]).reset_index(drop = True)
datapool_df = pd.concat([datapool_df, df3]).reset_index(drop = True)
datapool_df = pd.concat([datapool_df, df4]).reset_index(drop = True)
datapool_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/E_Scrambled_total.xlsx")
"""
#generate_datapool(machinedata)

#datapool = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/rawdatapool_E4.xlsx")
#datapool = app.summarize_dataset(datapool)
#datapool.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/datapool_E4.xlsx")
#print(datapool.info())

wrapped =wrapper(app.MachineAnalyse, machinedata)
py=timeit.timeit(wrapped, number = 1)
print("Time: " +str(py))
