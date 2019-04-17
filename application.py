#hej
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor

#Read and prepare data
data = pd.read_csv("C:/Users/nikla/OneDrive/Python/Datascience/AnomalydetectionApplication/exData.csv")
print(data.head(10))
uniquecompid = data.compid.unique()
print(uniquecompid)
for id in uniquecompid:
    component = data[data.compid == id]
    #print(component.head(10))
#plt.plot(component.leaves, component.documents,  'o')

    X = component.loc[0:,['depth','leaves', 'documents']]
    #print(X.head(10))

    #Local Outlier Factor
    model = LocalOutlierFactor(n_neighbors=10)
    lof_result = model.fit_predict(X)
    #component.plot.scatter('leaves', 'documents', c= lof_result, colormap = 'jet', colorbar = False)
    #plt.show()
    df_normalvalues = X
    df_normalvalues['Anomaly'] = lof_result
    df_anomalyvalues = df_normalvalues[df_normalvalues.Anomaly == -1]
    df_normalvalues = df_normalvalues[df_normalvalues.Anomaly != -1]
    print(df_anomalyvalues)
    #print(df_normalvalues.head(10))
    #df_normalvalues.thalach.max()
    variance = pd.Series(data=[df_normalvalues.depth.max(),df_normalvalues.depth.min(), df_normalvalues.leaves.max(),df_normalvalues.leaves.min(), df_normalvalues.documents.max(), df_normalvalues.documents.min()],
                         index=['Max Depth', 'Min Depth','Max Leaves', 'Min Leaves', 'Max Documents', 'Min Documents'], name = 'Variance')
    #variance = pd.DataFrame({'Max Thalach' : [df_normalvalues.thalach.max()], 'Min Thalach' : [df_normalvalues.thalach.min()],
                          #   'Max Age': [df_normalvalues.age.max()],  'Min Age' : [df_normalvalues.age.min()]})
    print(variance)


"""
if validate_product():
     if !(nr_comp()):
        uppdate_bounderies()
else:
    update_bounderies()

if check_bounderies():
        var +=1

"""
