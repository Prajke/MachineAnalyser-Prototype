
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
    #datapool = pd.read_csv("exData.csv")
    #start_summarize = time.time()
    listofcomponents = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx") #pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx") #summarize_components(machinedata)
    #time_summarize = time.time() - start_summarize

    #for i in range(0,2058):
    #for i in range(0,313):
    #    datapool.loc[datapool['cid'] == i, 'cid'] = listofcomponents.cid.values[i]
    datapool = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/datapool.xlsx")

    completecomponents = 0
    rows_list = []
    complete_list = []
    #time_model = 0
    #start_comploop = time.time()

    #for id in listofcomponents.cid.values:
    for index,row in listofcomponents.iterrows():
        #Kollar ifall komponenten finns i referensbibloteket
        componentpool = datapool[datapool.cid == row['cid']]
        currcomponent = listofcomponents[listofcomponents.eqnr ==row['eqnr']]
        oldcomponent = db.getComponent(row['cid'])
        if oldcomponent != []:
            #Extraherar referensvärdena och jämföra dessa med värden i komponenten i maskinen
            #Uppdatera referensvärdena om antal komponenter tillgängliga är
            #större än antalet komponenter under förra jämförelsen
            if int(oldcomponent["nrComponents"]) < len(componentpool):

                #start_model = time.time()
                oldcomponent = update_variance(componentpool, currcomponent,db)
                rows_list.append(oldcomponent)
                #time_model += ( time.time() - start_model)

            quality_dict = validateBounderies(currcomponent,oldcomponent)
            completecomponents += quality_dict['qm']
            complete_list.append(quality_dict)
        else:
            #start_model = time.time()
            oldcomponent = update_variance(componentpool, currcomponent,db)

            rows_list.append(oldcomponent)
            #time_model += (time.time() - start_model)

            quality_dict = validateBounderies(currcomponent,oldcomponent)
            completecomponents += quality_dict['qm']
            #Dict med completecomponents , quality_list[0], quality_list[1], quality_list[2]
            complete_list.append(quality_dict) #completecomponents , quality_list[0], quality_list[1], quality_list[2]

    referencedata = pd.DataFrame( rows_list , columns = [ "cid", "maxBom","minBom", "meanBom","maxChild", "minChild", "meanChild","maxDoc","minDoc","meanDoc","nrComponents"])
    listofreferences = referencedata.values.tolist()
    db.insertList(listofreferences)
    componentdata = listofcomponents
    complete_df = pd.DataFrame( complete_list , columns = [ "qm", "qm_doc","qm_bom", "qm_children"])
    componentdata = pd.concat([componentdata,complete_df], axis=1)

    #leavesdata = componentdata[componentdata['children'] == 0]
    #componentdata = componentdata[componentdata['children'] != 0]

    #completedata = pd.DataFrame( complete_list , columns = ["complete"])
    #completedata['eqnr'] = listofcomponents.eqnr.values
    #completedata['cid'] = listofcomponents.cid.values
    #completedata['depth'] = listofcomponents.depth.values

    #Gå igenom varje nod, kolla hur varje barn är komplett och beräkna ihop
    complete_list = []
    for index, row in componentdata.iterrows():
        if row["children"] ==  0:
            complete_list.append(0)
        else:
            completecomponents = 0
            completecomponents += row['qm']
            totalnodes = row['children'] + 1
            if row['eqnr'] == 1008803013:
                print(completecomponents)
                print(totalnodes)
            children = componentdata[componentdata['parent'] == row['eqnr']]
            dict = calc_child(children, componentdata,completecomponents, totalnodes)
            completecomponents = dict['total_qm']
            totalnodes = dict['totalchildren']
            if row['eqnr'] == 1008803013:
                print(completecomponents)
                print(totalnodes)
            complete_list.append(round((completecomponents/totalnodes),4))

    #print (round((completecomponents/len(listofcomponents)),4))

    componentdata['qm_totals '] = complete_list
    #componentdata = componentdata.append(leavesdata) #pd.concat([df1, df2])
    componentdata.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/completedata.xlsx")
    #time_comploop = time.time() - start_comploop
    #print("Comploop time: " + str(time_comploop-time_model))
    #print("Summarize time: " + str(time_summarize))
    #print("Model time: " + str(time_model))
def calc_child(children, df, completecomponents, totalnodes ):
    #completecomponents = 0
    #totalchildren = 0
    for index,row in children.iterrows():
        completecomponents += row['qm']
        if row['children'] != 0:
            totalnodes += row['children']
            dict = calc_child(df[df['parent'] == row['eqnr']], df, completecomponents, totalnodes)
            totalnodes = dict['totalchildren']
            completecomponents = dict['total_qm']
        if row['parent'] == 1008803013:
            print(completecomponents)
            print(totalnodes)
    dict =	{
      "total_qm": completecomponents,
      "totalchildren": totalnodes
    }
    return dict

def summarize_components(data):
    #machinedata = data.iloc[4:]
    machinedata = data.iloc[1:]
    machinedata = machinedata[machinedata["Depth"] > 2]
    cleanup_nums = {"BOM Item": {"-": 0, "Text": 1, "Document": 2, "Material": 4}}
    machinedata.replace(cleanup_nums, inplace=True)
    uniqueeqnr = machinedata["Equipment No"].unique()
    rows_list = []

    for id in uniqueeqnr:
        row = {}
        row.update( {
        "cid": machinedata[machinedata["Equipment No"] == id]["Material No."].unique()[0],
        "parent": int(machinedata[machinedata["Equipment No"] == id]["Parent"].unique()[0]),
        "children": len(machinedata[machinedata["Parent"] == id]["Equipment No"].unique()),
        "documents": machinedata[(machinedata["Equipment No"] == id) & (machinedata["BOM Item"] == 2) ]["No of Docs"].sum(),
        "bomitem": machinedata[machinedata["Equipment No"] == id]["BOM Item"].sum(),
        "depth": machinedata[machinedata["Equipment No"] == id]["Depth"].median()
        })
        rows_list.append(row)
    componentdata = pd.DataFrame( rows_list , columns = [ "cid", "parent", "children", "documents", "bomitem", "depth"])
    componentdata['eqnr'] = uniqueeqnr.astype(int)
    #print(uniqueeqnr)
    componentdata.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx")
    return componentdata

def update_variance(componentpool, currcomponent,db):
    #Extraherar liknande komponenter från datapoolen
    #componentpool = componentpool.append(pd.DataFrame(currcomponent, columns =[ 'cid','bomitem','children', 'documents']))
    #time_model = 0
    if len(componentpool) > 3:

        X = componentpool.loc[0:,['bomitem','children', 'documents']]
        #Local Outlier Factor
        algorithm = DBSCAN(eps=0.4, metric='euclidean', min_samples=2)
        #LocalOutlierFactor(n_neighbors=20)
        #IsolationForest(n_estimators=100, max_samples='auto')
        #DBSCAN(eps=3, metric='euclidean', min_samples=3)
        #algorithm.fit(X)
        lof_result = algorithm.fit_predict(X)
        df_anomalyvalues = X[lof_result == -1]
        df_normalvalues = X[lof_result != -1]
        #print(componentpool)
        #print(len(df_normalvalues))
    elif len(componentpool) == 1:
        df_normalvalues = currcomponent
    else :
        df_normalvalues = componentpool


    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen
    variance ={}
    variance.update( {
    "cid" : currcomponent.cid.values[0],
    "maxBom": int(df_normalvalues.bomitem.max()),
    "minBom":int(df_normalvalues.bomitem.min()),
    "meanBom":int(round(df_normalvalues.bomitem.mean(),0)),
    "maxChild": int(df_normalvalues.children.max()),
    "minChild":int(df_normalvalues.children.min()),
    "meanChild":int(round(df_normalvalues.children.mean(),0)),
    "maxDoc": int(df_normalvalues.documents.max()),
    "minDoc": int(df_normalvalues.documents.min()),
    "meanDoc":int(round(df_normalvalues.documents.mean(),0)),
    "nrComponents":len(componentpool)
    })
    #start_model = time.time()
    return variance
    #time_model = ( time.time() - start_model)
    #return time_model

def validateBounderies(curr, old):
    quality_list = [(int(curr["documents"]) >= old["minDoc"] and int(curr["documents"]) <= old["maxDoc"]),
                    (int(curr["bomitem"]) >= old["minBom"] and int(curr["bomitem"]) <= old["maxBom"]),
                    (int(curr["children"]) >= old["minChild"]  and int(curr["children"]) <= old["maxChild"])]
    row = {}
    row.update( {
    "qm": round((sum(quality_list)/len(quality_list)),4),
    "qm_doc": int(quality_list[0]),
    "qm_bom": int(quality_list[1]),
    "qm_children": int(quality_list[2])
    })
    return row

"""
df_normalvalues = X
df_normalvalues['Anomaly'] = lof_result
df_anomalyvalues = df_normalvalues[df_normalvalues.Anomaly == -1]
df_normalvalues = df_normalvalues[df_normalvalues.Anomaly != -1]
#print(df_normalvalues.head(10))
#df_normalvalues.thalach.max()
#component.plot.scatter('children', 'documents', c= lof_result, colormap = 'jet', colorbar = False)
#plt.show()
#uniquecompid = data.compid.unique()
#print(uniquecompid)
"""
