
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import database_helper as dbh
import time
from datetime import datetime, date


#Required:
# * A data-set representing a machine
# * A summarized datapool contaning relevant components to the machine

#Dictionary
# * Matnr => Material NO.
# * Eqnr => Equipment NO.
# * CM => Completness measurement, the completness of subtree(Structure of a component)
# * QM => Quality measurement, the quality of a node(Component)

#############################GENERATE REFERENCES AND CALCULATE QM FOR EACH COMPONENT IN THE MACHINE  ################################################################
def MachineAnalyse(machinedata):
    db = dbh.database()
    machine_info = machinedata.iloc[1]

    #Summarize the data-set to a iterable DataFrame, where each row is represented as the components in the machine
    component_df =  summarize_dataset(machinedata)
    #Read the summarized datapool
    datapool = pd.read_excel("summarized_datapool.xlsx")

    #Initiate the variables and lists used

    #The total quality measurement for the machine
    quality_measure = 0
    #Stores the reference that will be added to the library(database)
    reference_list = []
    #Stores the qm for each iterated component
    complete_list = []

    #A loop that iterates through each component in the data-set
    #The QM is calculated for each component
    for index,row in component_df.iterrows():

        #Retrieve all components with identical Material No. as the current component.
        componentpool = datapool[datapool.matnr == row['matnr']]
        #Create a DataFrame containing information about the current component
        current_reference = component_df[component_df.eqnr == row['eqnr']]

        #Retrieves a reference for the components Material NO. If no reference exists it will return a empty dict.
        old_reference = db.getReference(row['matnr'])

        #If a reference exists for the Material NO.
        if old_reference != []:

            #A new reference is created for the Material NO. if:
            # * The number of available components are larger now compared when the reference was generated.
            # * The reference is out of date.
            # * A reference is already generated for this Material NO. during the current runtime.
            if (int(old_reference['nrComponents']) < len(componentpool)) or not(validate_date(old_reference['date']) or not(in_list(row['matnr'], reference_list)) ):
                old_reference = generate_reference(componentpool, old_reference, db)
                reference_list.append(old_reference)

            #The QM is calculated based on a comparison of the current components features and the reference from the library
            #The QM is stored and added to the total QM.
            qm_dict = calculate_qm(current_reference,old_reference)
            quality_measure += qm_dict['qm_total']
            complete_list.append(qm_dict)
        else:
            #A reference is generated if:
            # * A reference is not generated for this Material NO. during the current runtime.
            if not(in_list(row['matnr'], reference_list)):
                old_reference = generate_reference(componentpool, current_reference, db)
                reference_list.append(old_reference)
            else :
                # Retrieve the already generated reference from the reference list
                list_item = [item for item in reference_list if item.get('matnr',None)==row['matnr']]
                old_reference = list_item[0]
            #The QM is calculated based on a comparison of the current components features and the reference from the library
            #The QM is stored and added to the total QM.
            qm_dict = calculate_qm(current_reference,old_reference)
            quality_measure += qm_dict['qm_total']
            complete_list.append(qm_dict)

    #A DataFrame containing all the generated references is created and inserted in the library.
    #Edit or add features here:
    reference_df = pd.DataFrame( reference_list , columns = [ "matnr", "maxBom","minBom", "meanBom","maxChild", "minChild", "meanChild", "maxDoc","minDoc","meanDoc","maxMat","minMat","meanMat","nrComponents", "date"])
    db.insertList(reference_df.values.tolist())
    #A DataFrame containing the QM for each component is created
    complete_df = pd.DataFrame( complete_list , columns = [ "qm_total", "qm_doc","qm_bom", "qm_children","qm_material" ])
    component_df = pd.concat([component_df,complete_df], axis=1)
    ###################################################################################################################################################

    #############################CALCULATE CM FOR EACH COMPONENT STRUCTURE AND THE WHOLE MACHINE ################################################################

    #Stores the qm for each component structure
    complete_list = []

    #A loop that iterates through each component in the data-s
    #Calculates the CM for each component structure
    for index, row in component_df.iterrows():
        #If component has no children, the QM for that specific component will be set as the total QM. (No structure, leaf)
        if row["children"] ==  0:
            complete_list.append(row['qm_total'])
        else:
            #Each children of the component is iterated and the QM is summed for all children.
            sum_qm = 0
            sum_qm += row['qm_total']
            total_subnodes = row['children'] + 1
            children = component_df[component_df['parent'] == row['eqnr']]
            node_dict = summarize_node(children, component_df,sum_qm, total_subnodes)
            sum_qm = node_dict['sum_qm']
            total_subnodes = node_dict['total_subnodes']
            #The CM for the component structure is calculated
            complete_list.append(round((sum_qm/total_subnodes),4))

    #The CM for each component structure is added in the dataframe for the top node in each structure.
    component_df['cm'] = complete_list
    #A row with summarization of the results is added in the top of the DataFrame.
    new_row = pd.DataFrame({'matnr':machine_info['Level'], 'parent':'-', 'children': len(component_df),
                        'documents': component_df['documents'].sum(), 'bomitem':component_df['bomitem'].sum(),
                        'depth':1, 'eqnr':machine_info['Equipment No'], 'qm_total':component_df['qm_total'].sum(),
                        'qm_doc':component_df['qm_doc'].sum(), 'qm_bom': component_df['qm_bom'].sum(),
                        'qm_children': component_df['qm_children'].sum(),
                        'qm_material': component_df['qm_material'].sum(),
                        'cm': component_df['qm_total'].sum()/len(component_df) }, index =[0])

    component_df = pd.concat([new_row, component_df[:]]).reset_index(drop = True)
    columns = ['matnr','eqnr','depth', 'parent', 'children', 'bomitem', 'documents', 'qm_total', 'qm_children', 'qm_bom', 'qm_doc','qm_material','cm']
    component_df = component_df[columns]

    #The result of the applications is added into a Excel file named, "machine_result.xlsx"
    component_df.to_excel("machine_result.xlsx")
##########################################################################################################################################################

#Returns TRUE if values exists in list.
def in_list(value, list):
    return any(item.get('matnr', None) == value for item in list)

#Validate a date based on a requirement, which determines when the references will be classed as outdated
#If a date is not the same as the current date, it will be classed as outdated, this can be changed below.
def validate_date(date_str):
    current_date = date.today()
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    return ( date_object.year == current_date.year and date_object.month == current_date.month and date_object.day == current_date.day)

#A recursive functions that calculates the total sum of QM and the total sum of node for a component structure.
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

#A function that summarizes datasets with a BOM structure to a iterable dataset.
def summarize_dataset(data):
    machinedata = data.iloc[1:]
    machinedata = machinedata[machinedata["Depth"] > 2]
    for col in ['Equipment No', 'Depth', 'Parent', 'No of Docs', 'Material No.']:
        machinedata[col] = machinedata[col].astype('int64')
    cleanup_nums = {"BOM Item": {"-": 0, "Text": 1, "Document": 2, "Material": 4}}
    machinedata.replace(cleanup_nums, inplace=True)
    uniqueeqnr = machinedata["Equipment No"].unique()
    reference_list = []

    #Edit or add features here:
    for id in uniqueeqnr:
        row = {}
        row.update( {
        "matnr": machinedata[machinedata["Equipment No"] == id]["Material No."].unique()[0],
        "parent": int(machinedata[machinedata["Equipment No"] == id]["Parent"].unique()[0]),
        "children": len(machinedata[machinedata["Parent"] == id]["Equipment No"].unique()),
        "documents": machinedata[(machinedata["Equipment No"] == id) & (machinedata["BOM Item"] == 2) ]["No of Docs"].sum(),
        "materials": machinedata[(machinedata["Equipment No"] == id) & (machinedata["BOM Item"] == 4) ]["No of Docs"].sum(),
        "bomitem": machinedata[machinedata["Equipment No"] == id]["BOM Item"].sum(),
        "depth": machinedata[machinedata["Equipment No"] == id]["Depth"].median()
        })
        reference_list.append(row)
    #Edit or add features here:
    component_df = pd.DataFrame( reference_list , columns = [ "matnr", "parent", "children", "documents","materials","bomitem", "depth"])
    component_df['eqnr'] = uniqueeqnr.astype('int64')

    #Remove the comment to save the summarized dataset as a excel
    #component_df.to_excel("summarized_dataset.xlsx")

    return component_df

#Generates a reference for a "Material NO." by using a algorithm that finds anomalies in all available components with identical  "Material NO.".
#The normal values will be used a reference
def generate_reference(componentpool, current_reference, db):

    anomaly_df = pd.DataFrame()
    normal_df = pd.DataFrame()

    #Edit or add features here:
    #These are features that used in the algorithm
    components = componentpool.loc[0:,['bomitem','children', 'documents',"materials"]]

    ############################ Anomaly detection method #############################
    #In this secion the parameters and algorithm/method can be altered or replace
    if len(components) > 5 :
        if len(components) < 100:
            eps = 7.9
            ms = 5
        elif 99 < len(components) < 1000 :
            eps = 10
            ms = 5
        else:
            eps = 8.1
            ms = 23

        algorithm =DBSCAN(eps=eps, metric='euclidean', min_samples=ms)
    #################################################################################
        result = algorithm.fit_predict(components)
        anomaly_df = components[result == -1]
        normal_df = components[result != -1]
    elif (len(components) == 1):
        normal_df = current_reference
    else :
        normal_df = componentpool

    if normal_df.empty:
        normal_df = current_reference
        nrComponents = 1
    else :
        nrComponents = len(components)

    if not (anomaly_df.empty):
        anomaly_df['matnr'] = current_reference.matnr.values[0]
        anomaly_df['date'] = date.today()
        columns = ['matnr', 'bomitem', 'children', 'documents', 'materials', 'date']
        anomaly_df = anomaly_df[columns]
        db.insertAnomalies(anomaly_df.values.tolist())

    #Edit or add features here:
    reference = {}
    reference.update( {
    "matnr" : current_reference.matnr.values[0],
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
    "nrComponents":nrComponents,
    "date": date.today()
    })

    return reference

#Calculates the QM based on a comparison of two references
def calculate_qm(curr, old):
    #Edit or add features here:
    validate_list = [(int(curr["documents"]) >= old["minDoc"] and int(curr["documents"]) <= old["maxDoc"]),
                    (int(curr["bomitem"]) >= old["minBom"] and int(curr["bomitem"]) <= old["maxBom"]),
                    (int(curr["children"]) >= old["minChild"]  and int(curr["children"]) <= old["maxChild"]),
                    (int(curr["materials"]) >= old["minMat"]  and int(curr["materials"]) <= old["maxMat"])]
    qm_dict = {}
    #Edit or add features here:
    qm_dict.update( {
    "qm_total": round((sum(validate_list)/len(validate_list)),4),
    "qm_doc": int(validate_list[0]),
    "qm_bom": int(validate_list[1]),
    "qm_children": int(validate_list[2]),
    "qm_material": int(validate_list[3])
    })
    return qm_dict
