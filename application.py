
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest

def MachineAnalyse(machinedata):
    datapool = pd.read_csv("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/exData.csv")
    listofcomponents = summarize_components(machinedata)
    completecomponents = 0

    for id in listofcomponents.cid.values:
        #Kollar ifall komponenten finns i referensbibloteket
        componentpool = datapool[datapool.cid == id]
        currcomponent = listofcomponents[listofcomponents.cid == id]

        if validate_component(id) :
            #Extraherar referensvärdena och jämföra dessa med värden i komponenten i maskinen

            #Uppdatera referensvärdena om antal komponenter tillgängliga är
            #större än antalet komponenter under förra jämförelsen
            if  validate_componentamount(len(componentpool), id) :
                update_variance(componentpool, currcomponent)

            if compare_component(id, currcomponent):
                completecomponents += 1
        else:
            update_variance(componentpool, currcomponent)
            if compare_component(id, currcomponent):
                completecomponents += 1

    return (completecomponents/listofcomponents.length())

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
    componentdata['cid'] = uniquecomponents
    return componentdata

def update_variance(componentpool, currcomponent):
    #Extraherar liknande komponenter från datapoolen
    componentpool = componentpool.append(pd.DataFrame(currcomponent, columns =[ 'cid','bomitem','leaves', 'documents']))


    if len(componentpool) > 1:
        X = componentpool.loc[0:,['bomitem','leaves', 'documents']]
        #Local Outlier Factor
        model = LocalOutlierFactor(n_neighbors=20)
        #IsolationForest(n_estimators=100, max_samples='auto')
        #DBSCAN(eps=3, metric='euclidean', min_samples=3)
        #model.fit(X)
        lof_result = model.fit_predict(X)
        df_anomalyvalues = X[lof_result == -1]
        df_normalvalues = X[lof_result != -1]

    else :
        df_normalvalues = currcomponent

    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen

    variance = {
    "cid" : currcomponent.cid[0],
    "MaxBOMItem": df_normalvalues.bomitem.max(),
    "MinBOMItem":df_normalvalues.bomitem.min(),
    "MeanBOMItem":int(round(df_normalvalues.bomitem.mean(),0)),
    "MaxLeaves": df_normalvalues.leaves.max(),
    "MinLeaves":df_normalvalues.leaves.min(),
    "MeanLeaves":int(round(df_normalvalues.leaves.mean(),0)),
    "MaxDocuments": df_normalvalues.documents.max(),
    "MinDocuments": df_normalvalues.documents.min(),
    "MeanDocuments":int(round(df_normalvalues.documents.mean(),0)),
    "TotalComponents":len(componentpool)
    }

    #put_component(variance)
    print(variance)

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
