
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import database_helper as dbh
import time


def MachineAnalyse(machinedata):
    db = dbh.database()
    datapool = pd.read_csv("exData.csv")
    start_summarize = time.time()
    listofcomponents = summarize_components(machinedata)
    time_summarize = time.time() - start_summarize
    datapool.loc[datapool['cid'] == 0, 'cid'] = 1008803013
    datapool.loc[datapool['cid'] == 1, 'cid'] = 1008803050
    datapool.loc[datapool['cid'] == 2, 'cid'] = 1008802058
    datapool.loc[datapool['cid'] == 3, 'cid'] = 1008802060
    datapool.loc[datapool['cid'] == 4, 'cid'] = 1008802061

    #listofcomponents = machinedata
    completecomponents = 0
    time_model = 0
    start_comploop = time.time()
    for id in listofcomponents.cid.values:
        #Kollar ifall komponenten finns i referensbibloteket
        componentpool = datapool[datapool.cid == id]
        currcomponent = listofcomponents[listofcomponents.cid == id]
        if db.validateComponent(id):
            #Extraherar referensvärdena och jämföra dessa med värden i komponenten i maskinen

            #Uppdatera referensvärdena om antal komponenter tillgängliga är
            #större än antalet komponenter under förra jämförelsen
            if  db.validateComponentAmount(id,len(componentpool)) :
                start_model = time.time()
                update_variance(componentpool, currcomponent,db)
                time_model += ( time.time() - start_model)
            if db.validateBounderies(id, currcomponent):
                completecomponents += 1
        else:
            start_model = time.time()
            update_variance(componentpool, currcomponent,db)
            time_model += (time.time() - start_model)
            if db.validateBounderies(id, currcomponent):
                completecomponents += 1
    time_comploop = time.time() - start_comploop
    print("Comploop time: " + str(time_comploop-time_model))
    print("Summarize time: " + str(time_summarize))
    print("Model time: " + str(time_model))
    return round((completecomponents/len(listofcomponents)),2)

def summarize_components(data):
    machinedata = data.iloc[4:]
    cleanup_nums = {"BOM Item": {"-": 0, "Text": 1, "Document": 2, "Material": 4}}
    machinedata.replace(cleanup_nums, inplace=True)
    uniquecomponents = machinedata["Equipment No"].unique()
    rows_list = []

    for id in uniquecomponents:
        row = {}
        row.update( {
        "leaves": len(machinedata[machinedata.Parent == id]),
        "documents": machinedata[machinedata["Equipment No"] == id]["No of Docs"].sum(),
        #"totaldocsofchildren": machinedata[machinedata.Parent == id]["No of Docs"].sum(),
        "depth": machinedata[machinedata["Equipment No"] == id].Depth.median(),
        "bomitem": machinedata[machinedata["Equipment No"] == id]["BOM Item"].sum()
        })
        rows_list.append(row)
    componentdata = pd.DataFrame( rows_list , columns = [ "bomitem", "depth", "leaves", "documents"])
    componentdata['cid'] = uniquecomponents.astype(int)
    return componentdata

def update_variance(componentpool, currcomponent,db):
    #Extraherar liknande komponenter från datapoolen
    #componentpool = componentpool.append(pd.DataFrame(currcomponent, columns =[ 'cid','bomitem','leaves', 'documents']))


    if len(componentpool) > 1:
        #X = componentpool.loc[0:,['bomitem','leaves', 'documents']]
        #Local Outlier Factor
        model = LocalOutlierFactor(n_neighbors=20)
        #IsolationForest(n_estimators=100, max_samples='auto')
        #DBSCAN(eps=3, metric='euclidean', min_samples=3)
        #model.fit(X)
        lof_result = model.fit_predict(componentpool)
        df_anomalyvalues = componentpool[lof_result == -1]
        df_normalvalues = componentpool[lof_result != -1]

    else :
        df_normalvalues = currcomponent

    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen

    variance = {
    "cid" : int(currcomponent.cid.values[0]),
    "MaxBOMItem": int(df_normalvalues.bomitem.max()),
    "MinBOMItem":int(df_normalvalues.bomitem.min()),
    "MeanBOMItem":int(round(df_normalvalues.bomitem.mean(),0)),
    "MaxLeaves": int(df_normalvalues.leaves.max()),
    "MinLeaves":int(df_normalvalues.leaves.min()),
    "MeanLeaves":int(round(df_normalvalues.leaves.mean(),0)),
    "MaxDocuments": int(df_normalvalues.documents.max()),
    "MinDocuments": int(df_normalvalues.documents.min()),
    "MeanDocuments":int(round(df_normalvalues.documents.mean(),0)),
    "TotalComponents":len(componentpool)
    }

    db.addComponent(variance)

"""
df_normalvalues = X
df_normalvalues['Anomaly'] = lof_result
df_anomalyvalues = df_normalvalues[df_normalvalues.Anomaly == -1]
df_normalvalues = df_normalvalues[df_normalvalues.Anomaly != -1]
#print(df_normalvalues.head(10))
#df_normalvalues.thalach.max()
#component.plot.scatter('leaves', 'documents', c= lof_result, colormap = 'jet', colorbar = False)
#plt.show()
#uniquecompid = data.compid.unique()
#print(uniquecompid)
"""
