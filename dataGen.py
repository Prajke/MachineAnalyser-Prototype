#Generates testdata representing a machine, with serveral components
#The component is saved as a csv

#Filname for the csv file containg the
file = "exData.csv"

from random import randint
import csv

components = []
for i in range(0,5):
    component = []
    for x in range(0,50):
        feature = [randint(20,30) for p in range(0,3)]
        feature.append(i)
        feature.reverse()
        component.append(feature)
    components.append(component)

    with open(file, 'w') as writeFile:
        for j in components:
            writer = csv.writer(writeFile)
            writer.writerows(j)
