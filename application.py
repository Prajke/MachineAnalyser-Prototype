
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import database_helper as dbh
import time

##Minska funktions calling i comploop
#Minska databasåtkomst i comploop => en get component

def MachineAnalyse(machinedata):
    db = dbh.database()
    datapool = pd.read_csv("exData.csv")
    start_summarize = time.time()
    listofcomponents = summarize_components(machinedata)
    time_summarize = time.time() - start_summarize

    for i in range(0,2058):
        datapool.loc[datapool['cid'] == i, 'cid'] = listofcomponents.cid.values[i]

    #listofcomponents = machinedata
    completecomponents = 0
    time_model = 0
    start_comploop = time.time()
    #for id in listofcomponents.cid.values:
    for index,row in listofcomponents.iterrows():
        #Kollar ifall komponenten finns i referensbibloteket

        componentpool = datapool[datapool.cid == int(row['cid'])]
        currcomponent = listofcomponents[listofcomponents.cid ==row['cid']]

        #oldcomponent = db.getComponent(int(row['cid']))

        #if oldcomponent != []:
        if db.validateComponent(row['cid']):
            #Extraherar referensvärdena och jämföra dessa med värden i komponenten i maskinen

            #Uppdatera referensvärdena om antal komponenter tillgängliga är
            #större än antalet komponenter under förra jämförelsen
            #if int(oldcomponent["nrComponents"]) > len(componentpool):
            if  db.validateComponentAmount(row['cid'],len(componentpool)) :
                start_model = time.time()
                oldcomponent = update_variance(componentpool, currcomponent,db)
                time_model += ( time.time() - start_model)
            if db.validateBounderies(row['cid'], currcomponent):
            #if validateBounderies(currcomponent,oldcomponent):
                completecomponents += 1
        else:
            start_model = time.time()
            oldcomponent = update_variance(componentpool, currcomponent,db)
            time_model += (time.time() - start_model)
            if db.validateBounderies(row['cid'], currcomponent):
            #if validateBounderies(currcomponent,oldcomponent):
                completecomponents += 1
    time_comploop = time.time() - start_comploop
    print("Comploop time: " + str(time_comploop-time_model))
    print("Summarize time: " + str(time_summarize))
    print("Model time: " + str(time_model))
    return round((completecomponents/len(listofcomponents)),4)

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

    #time_model = 0
    if len(componentpool) > 1:

        X = componentpool.loc[0:,['bomitem','leaves', 'documents']]
        #Local Outlier Factor
        model =  LocalOutlierFactor(n_neighbors=20)
        #LocalOutlierFactor(n_neighbors=20)
        #IsolationForest(n_estimators=100, max_samples='auto')
        #DBSCAN(eps=3, metric='euclidean', min_samples=3)
        model.fit(X)
        lof_result = model.fit_predict(X)
        df_anomalyvalues = X[lof_result == -1]
        df_normalvalues = X[lof_result != -1]
    else :
        df_normalvalues = currcomponent

    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen

    variance = {
    "cid" : int(currcomponent.cid.values[0]),
    "maxBom": int(df_normalvalues.bomitem.max()),
    "minBom":int(df_normalvalues.bomitem.min()),
    "meanBom":int(round(df_normalvalues.bomitem.mean(),0)),
    "maxChild": int(df_normalvalues.leaves.max()),
    "minChild":int(df_normalvalues.leaves.min()),
    "meanChild":int(round(df_normalvalues.leaves.mean(),0)),
    "maxDoc": int(df_normalvalues.documents.max()),
    "minDoc": int(df_normalvalues.documents.min()),
    "meanDoc":int(round(df_normalvalues.documents.mean(),0)),
    "nrComponents":len(componentpool)
    }
    #start_model = time.time()
    db.addComponent(variance)

    return variance
    #time_model = ( time.time() - start_model)
    #return time_model
def validateBounderies(curr, old):
    if ( (int(curr["documents"]) >= old["minDoc"] and int(curr["documents"]) <= old["maxDoc"]) and
         (int(curr["bomitem"]) >= old["minBom"] and int(curr["bomitem"]) <= old["maxBom"]) and
         (int(curr["leaves"]) >= old["minChild"]  and int(curr["leaves"]) <= old["maxChild"])):
        return True
    else:
        return False
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
