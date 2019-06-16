import application as app
import pandas as pd
import numpy as np
import database_helper as dbh
import time
import timeit

db = dbh.database()

#Extracts only components with a Material NO. that exists in the machine dataset from a rawdatapool.
#These components are summarized into a iterable dataset.
def generate_datapool(machinedata):
    uniquecid = machinedata["Material No."].unique()
    #print(uniquecid)
    datapool_df = pd.read_excel("rawdatapool.xlsx")
    newdatapool_df = pd.DataFrame()
    for id in uniquecid:
        df = datapool_df[datapool_df['Material No.'] == id]
        #df = df[df['Equipment No'].apply(lambda x: x.isnumeric())]
        #print(df.head())
        #df['Equipment No'] = df['Equipment No'].astype(np.int64)
        newdatapool_df = pd.concat([newdatapool_df, df]).reset_index(drop = True)
    datapool_df = app.summarize_components(newdatapool_df)
    datapool_df.to_excel("summarized_datapool.xlsx")

#Only used to enable timeit
def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

machinedata = pd.read_excel("machine.xlsx")
#A summarized datapool is generated before the MachineAnalyse function can be used.(Only needs to be done once for each machine)
generate_datapool(machinedata)
wrapped =wrapper(app.MachineAnalyse, machinedata)
py=timeit.timeit(wrapped, number = 1)
print("Time: " +str(py))
