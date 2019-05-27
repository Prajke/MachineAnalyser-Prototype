
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
    machine_info = machinedata.iloc[1]
    component_df =  pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx") #pd.read_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx") #summarize_dataset(machinedata)
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
                old_reference = generate_reference(componentpool, current_reference, db)
                reference_list.append(old_reference)
            qm_dict = calculate_qm(current_reference,old_reference)
            quality_measure += qm_dict['qm_total']
            complete_list.append(qm_dict)
        else:
            if not(in_list(row['cid'], reference_list)):
                old_reference = generate_reference(componentpool, current_reference, db)
                reference_list.append(old_reference)
            else :
                list_item = [item for item in reference_list if item.get('cid',None)==row['cid']]
                old_reference = list_item[0]
            qm_dict = calculate_qm(current_reference,old_reference)
            quality_measure += qm_dict['qm_total']
            complete_list.append(qm_dict)

    reference_df = pd.DataFrame( reference_list , columns = [ "cid", "maxBom","minBom", "meanBom","maxChild", "minChild", "meanChild", "maxDoc","minDoc","meanDoc","maxMat","minMat","meanMat","nrComponents", "date"])
    db.insertList(reference_df.values.tolist())
    complete_df = pd.DataFrame( complete_list , columns = [ "qm_total", "qm_doc","qm_bom", "qm_children","qm_material" ])
    component_df = pd.concat([component_df,complete_df], axis=1)

    #Gå igenom varje nod, kolla hur varje barn är komplett och beräkna ihop
    complete_list = []
    for index, row in component_df.iterrows():
        if row["children"] ==  0:
            complete_list.append(row['qm_total'])
        else:
            sum_qm = 0
            sum_qm += row['qm_total']
            total_subnodes = row['children'] + 1
            children = component_df[component_df['parent'] == row['eqnr']]
            node_dict = summarize_node(children, component_df,sum_qm, total_subnodes)
            sum_qm = node_dict['sum_qm']
            total_subnodes = node_dict['total_subnodes']
            complete_list.append(round((sum_qm/total_subnodes),4))

    component_df['cm'] = complete_list
    new_row = pd.DataFrame({'cid':machine_info['Level'], 'parent':'-', 'children': len(component_df),
                        'documents': component_df['documents'].sum(), 'bomitem':component_df['bomitem'].sum(),
                        'depth':1, 'eqnr':machine_info['Equipment No'], 'qm_total':component_df['qm_total'].sum(),
                        'qm_doc':component_df['qm_doc'].sum(), 'qm_bom': component_df['qm_bom'].sum(),
                        'qm_children': component_df['qm_children'].sum(),
                        'qm_material': component_df['qm_material'].sum(),
                        'cm': component_df['qm_total'].sum()/len(component_df) }, index =[0])

    component_df = pd.concat([new_row, component_df[:]]).reset_index(drop = True)
    columns = ['cid','eqnr','depth', 'parent', 'children', 'bomitem', 'documents', 'qm_total', 'qm_children', 'qm_bom', 'qm_doc','qm_material','cm']
    component_df = component_df[columns]
    component_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/completedata.xlsx")


def in_list(value, list):
    return any(item.get('cid', None) == value for item in list)

def validate_date(date_str):
    current_date = date.today()
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    return ( date_object.year == current_date.year and date_object.month == current_date.month and date_object.day == current_date.day)

def summarize_node(children, df, sum_qm, total_subnodes ):
    for index,row in children.iterrows():
        sum_qm += row['qm_total']
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
        "materials": machinedata[(machinedata["Equipment No"] == id) & (machinedata["BOM Item"] == 4) ]["No of Docs"].sum(),
        "bomitem": machinedata[machinedata["Equipment No"] == id]["BOM Item"].sum(),
        "depth": machinedata[machinedata["Equipment No"] == id]["Depth"].median()
        })
        reference_list.append(row)
    component_df = pd.DataFrame( reference_list , columns = [ "cid", "parent", "children", "documents","materials","bomitem", "depth"])
    component_df['eqnr'] = uniqueeqnr.astype(int)
    component_df.to_excel("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/componentdata.xlsx")
    return component_df

def generate_reference(componentpool, current_reference, db):
    #Extraherar liknande komponenter från datapoolen
    anomaly_df = pd.DataFrame()
    if len(componentpool) > 3:
        components = componentpool.loc[0:,['bomitem','children', 'documents',"materials"]]
        algorithm = DBSCAN(eps=0.4, metric='euclidean', min_samples=2)
        #LocalOutlierFactor(n_neighbors=20)
        #IsolationForest(n_estimators=100, max_samples='auto')
        #DBSCAN(eps=3, metric='euclidean', min_samples=3)
        #algorithm.fit(X)
        result = algorithm.fit_predict(components)
        anomaly_df = components[result == -1]
        normal_df = components[result != -1]
    elif len(componentpool) == 1:
        normal_df = current_reference
    else :
        normal_df = componentpool

    if not (anomaly_df.empty):
        anomaly_df['cid'] = current_reference.cid.values[0]
        anomaly_df['date'] = date.today()
        columns = ['cid', 'bomitem', 'children', 'documents', 'materials', 'date']
        anomaly_df = anomaly_df[columns]
        db.insertAnomalies(anomaly_df.values.tolist())

    #current_time = datetime.datetime.now()
    #Skapa en dikt som skickas in till referensbibloteket, baserat på resultatet från modellen
    reference = {}
    reference.update( {
    "cid" : current_reference.cid.values[0],
    "maxBom": int(normal_df.bomitem.max()),
    "minBom":int(normal_df.bomitem.min()),
    "meanBom":int(round(normal_df.bomitem.mean(),0)),
    "maxChild": int(normal_df.children.max()),
    "minChild":int(normal_df.children.min()),
    "meanChild":int(round(normal_df.children.mean(),0)),
    "maxDoc": int(normal_df.documents.max()),
    "minDoc": int(normal_df.documents.min()),
    "meanDoc":int(round(normal_df.documents.mean(),0)),
    "maxMat": int(normal_df.materials.max()),
    "minMat": int(normal_df.materials.min()),
    "meanMat":int(round(normal_df.materials.mean(),0)),
    "nrComponents":len(componentpool),
    "date": date.today()
    })

    return reference

def calculate_qm(curr, old):
    validate_list = [(int(curr["documents"]) >= old["minDoc"] and int(curr["documents"]) <= old["maxDoc"]),
                    (int(curr["bomitem"]) >= old["minBom"] and int(curr["bomitem"]) <= old["maxBom"]),
                    (int(curr["children"]) >= old["minChild"]  and int(curr["children"]) <= old["maxChild"]),
                    (int(curr["materials"]) >= old["minMat"]  and int(curr["materials"]) <= old["maxMat"])]
    qm_dict = {}
    qm_dict.update( {
    "qm_total": round((sum(validate_list)/len(validate_list)),4),
    "qm_doc": int(validate_list[0]),
    "qm_bom": int(validate_list[1]),
    "qm_children": int(validate_list[2]),
    "qm_material": int(validate_list[3])
    })
    return qm_dict
