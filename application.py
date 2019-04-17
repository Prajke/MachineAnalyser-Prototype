
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

    for id in Listofcomponents.compid:
        #Kollar ifall komponenten finns i referensbibloteket
        componentpool = datapool[datapool.compid == id]
        variance = listofcomponents[listofcomponents.compid == id]

        if validate_component(id) :
            #Extraherar referensvärdena och jämföra dessa med värden i komponenten i maskinen

            if componentpool == None:
                #Skapa en dikt som skickas in till referensbibloteket, baserat på värdena i maskinen
                put_component(variance)
                completecomponents += 1
            else:
                #Uppdatera referensvärdena om antal komponenter tillgängliga är
                #större än antalet komponenter under förra jämförelsen
                if  validate_componentamount(componentpool.length, id) :
                    update_variance(componentpool)

                if compare_component(id, variance):
                    completecomponents += 1
        else:

            if componentpool == None:
                #Skapa en dikt som skickas in till referensbibloteket, baserat på värdena i maskinen
                put_component(variance)
                completecomponents += 1
            else:
                #Jämför komponenten med liknande komponenter från datapoolen
                update_variance(componentpool)
                if compare_component(id, variance):
                    completecomponents += 1

    return (completecomponents/listofcomponents.length())

def summarize_components(data):
    machinedata = data.iloc[4:]
    cleanup_nums = {"BOM Item": {"-": 0, "Text": 1, "Document": 2, "Material": 4}}
    machinedata.replace(cleanup_nums, inplace=True)

    uniquecomponents = machinedata["Equipment No"].unique()
    rows_list = []

    for component in uniquecomponents:
        row = {}
        row.update( {
        "nrofchildren": len(machinedata[machinedata.Parent == component]),
        "totaldocs": machinedata[machinedata["Equipment No"] == component]["No of Docs"].sum(),
        "totaldocsofchildren": machinedata[machinedata.Parent == component]["BOM Item"].sum(),
        "depth": machinedata[machinedata["Equipment No"] == component].Depth.median(),
        "BOMitems": machinedata[machinedata["Equipment No"] == component]["BOM Item"].sum()
        })
        rows_list.append(row)

    componentdata = pd.DataFrame( rows_list , columns = [ "BOMitems", "depth", "nrofchildren", "totaldocs", "totaldocsofchildren"])
    componentdata['combid'] = uniquecomponents
    return componentdata

def update_variance(components):
    #Extraherar liknande komponenter från datapoolen
    X = components.loc[0:,['bomitem','leaves', 'documents']]

    #Local Outlier Factor
    model = LocalOutlierFactor(n_neighbors=20)
    #IsolationForest(n_estimators=100, max_samples='auto')
    #DBSCAN(eps=3, metric='euclidean', min_samples=3)
    #model.fit(X)
    lof_result = model.fit_predict(X)
    df_anomalyvalues = X[lof_result == -1]
    df_normalvalues = X[lof_result != -1]

    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen
    #variance = pd.Series(data=[df_normalvalues.depth.max(),df_normalvalues.depth.min(), df_normalvalues.leaves.max(),df_normalvalues.leaves.min(), df_normalvalues.documents.max(), df_normalvalues.documents.min()],
                         #index=['Max Depth', 'Min Depth','Max Leaves', 'Min Leaves', 'Max Documents', 'Min Documents'], name = 'Variance')
    variance = {
    "MaxBOMItem": df_normalvalues.bomitem.max(),
    "MinBOMItem":df_normalvalues.bomitem.min(),
    "MeanBOMItem":int(round(df_normalvalues.bomitem.mean(),0)),
    "MaxLeaves": df_normalvalues.leaves.max(),
    "MinLeaves":df_normalvalues.leaves.min(),
    "MeanLeaves":int(round(df_normalvalues.leaves.mean(),0)),
    "MaxDocuments": df_normalvalues.documents.max(),
    "MinDocuments": df_normalvalues.documents.min(),
    "MeanDocuments":int(round(df_normalvalues.documents.mean(),0)),
    "TotalComponents":len(components)
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
