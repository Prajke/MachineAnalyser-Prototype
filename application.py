
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import database_helper as dbh
import time
from datetime import datetime, date

def MachineAnalyse(machinedata):
    db = dbh.database()
    component_df = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx") #pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/component_df.xlsx") #summarize_dataset(machinedata)
    datapool = pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/datapool.xlsx")

    quality_measure = 0
    reference_list = []
    complete_list = []

    for index,row in component_df.iterrows():
        #Kollar ifall komponenten finns i referensbibloteket
        componentpool = datapool[datapool.cid == row['cid']]
        current_reference = component_df[component_df.eqnr == row['eqnr']]
        old_reference = db.getComponent(row['cid'])
        if old_reference != []:
            #Extraherar referensvärdena och jämföra dessa med värden i komponenten i maskinen
            #Uppdatera referensvärdena om antal komponenter tillgängliga är
            #större än antalet komponenter under förra jämförelsen
            if (int(old_reference['nrComponents']) < len(componentpool)) or not(validate_date(old_reference['date']) or not(in_list(row['cid'], reference_list)) ):
                old_reference = update_variance(componentpool, current_reference)
                reference_list.append(old_reference)
            qm_dict = validateBounderies(current_reference,old_reference)
            quality_measure += qm_dict['qm']
            complete_list.append(qm_dict)
        else:
            if not(in_list(row['cid'], reference_list)):
                old_reference = update_variance(componentpool, current_reference)
                reference_list.append(old_reference)
            else :
                list_item = [item for item in reference_list if item.get('cid',None)==row['cid']] 
                old_reference = list_item[0]
            qm_dict = validateBounderies(current_reference,old_reference)
            quality_measure += qm_dict['qm']
            complete_list.append(qm_dict)

    reference_df = pd.DataFrame( reference_list , columns = [ "cid", "maxBom","minBom", "meanBom","maxChild", "minChild", "meanChild","maxDoc","minDoc","meanDoc","nrComponents", "date"])
    db.insertList(reference_df.values.tolist())
    complete_df = pd.DataFrame( complete_list , columns = [ "qm", "qm_doc","qm_bom", "qm_children"])
    component_df = pd.concat([component_df,complete_df], axis=1)

    #Gå igenom varje nod, kolla hur varje barn är komplett och beräkna ihop
    complete_list = []
    for index, row in component_df.iterrows():
        if row["children"] ==  0:
            complete_list.append(row['qm'])
        else:
            sum_qm = 0
            sum_qm += row['qm']
            total_subnodes = row['children'] + 1
            children = component_df[component_df['parent'] == row['eqnr']]
            node_dict = summarize_node(children, component_df,sum_qm, total_subnodes)
            sum_qm = node_dict['sum_qm']
            total_subnodes = node_dict['total_subnodes']
            complete_list.append(round((sum_qm/total_subnodes),4))

    component_df['qm_total '] = complete_list
    component_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/completedata.xlsx")

def in_list(value, list):
    return any(item.get('cid', None) == value for item in list)

def validate_date(date_str):
    current_date = date.today()
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    return ( date_object.year == current_date.year and date_object.month == current_date.month and date_object.day == current_date.day)

def summarize_node(children, df, sum_qm, total_subnodes ):
    for index,row in children.iterrows():
        sum_qm += row['qm']
        if row['children'] != 0:
            total_subnodes += row['children']
            node_dict = summarize_node(df[df['parent'] == row['eqnr']], df, sum_qm, total_subnodes)
            total_subnodes = node_dict['total_subnodes']
            sum_qm = node_dict['sum_qm']
    node_dict =	{
      "sum_qm": sum_qm,
      "total_subnodes": total_subnodes
    }
    return node_dict

def summarize_dataset(data):
    machinedata = data.iloc[1:]
    machinedata = machinedata[machinedata["Depth"] > 2]
    cleanup_nums = {"BOM Item": {"-": 0, "Text": 1, "Document": 2, "Material": 4}}
    machinedata.replace(cleanup_nums, inplace=True)
    uniqueeqnr = machinedata["Equipment No"].unique()
    reference_list = []

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
        reference_list.append(row)
    component_df = pd.DataFrame( reference_list , columns = [ "cid", "parent", "children", "documents", "bomitem", "depth"])
    component_df['eqnr'] = uniqueeqnr.astype(int)
    component_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/component_df.xlsx")
    return component_df

def update_variance(componentpool, current_reference):
    #Extraherar liknande komponenter från datapoolen
    if len(componentpool) > 3:
        components = componentpool.loc[0:,['bomitem','children', 'documents']]
        algorithm = DBSCAN(eps=0.4, metric='euclidean', min_samples=2)
        #LocalOutlierFactor(n_neighbors=20)
        #IsolationForest(n_estimators=100, max_samples='auto')
        #DBSCAN(eps=3, metric='euclidean', min_samples=3)
        #algorithm.fit(X)
        result = algorithm.fit_predict(components)
        anomalyvalues = components[result == -1]
        normalvalues = components[result != -1]
    elif len(componentpool) == 1:
        normalvalues = current_reference
    else :
        normalvalues = componentpool

    #current_time = datetime.datetime.now()
    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen
    reference = {}
    reference.update( {
    "cid" : current_reference.cid.values[0],
    "maxBom": int(normalvalues.bomitem.max()),
    "minBom":int(normalvalues.bomitem.min()),
    "meanBom":int(round(normalvalues.bomitem.mean(),0)),
    "maxChild": int(normalvalues.children.max()),
    "minChild":int(normalvalues.children.min()),
    "meanChild":int(round(normalvalues.children.mean(),0)),
    "maxDoc": int(normalvalues.documents.max()),
    "minDoc": int(normalvalues.documents.min()),
    "meanDoc":int(round(normalvalues.documents.mean(),0)),
    "nrComponents":len(componentpool),
    "date": date.today()
    })
    return reference

def validateBounderies(curr, old):
    #print(curr)
    #print(old)
    validate_list = [(int(curr["documents"]) >= old["minDoc"] and int(curr["documents"]) <= old["maxDoc"]),
                    (int(curr["bomitem"]) >= old["minBom"] and int(curr["bomitem"]) <= old["maxBom"]),
                    (int(curr["children"]) >= old["minChild"]  and int(curr["children"]) <= old["maxChild"])]
    qm_dict = {}
    qm_dict.update( {
    "qm": round((sum(validate_list)/len(validate_list)),4),
    "qm_doc": int(validate_list[0]),
    "qm_bom": int(validate_list[1]),
    "qm_children": int(validate_list[2])
    })
    return qm_dict
