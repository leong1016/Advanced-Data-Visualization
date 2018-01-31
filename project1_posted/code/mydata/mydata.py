import pandas as pd
from sklearn import preprocessing

pd.set_option('max_rows', 1000, 'max_columns', 1000, 'expand_frame_repr', False)

data = pd.read_csv('mydata.csv')
data = data.head(1000)

newdata = data.drop(['encounter_id', 'patient_nbr', 'weight', 'payer_code'], axis=1)

race = newdata['race']
gender = newdata['gender']
age = newdata['age']

le = preprocessing.LabelEncoder()
for col in newdata.columns:
    if newdata[col].dtype == 'object':
        newdata[col] = le.fit_transform(newdata[col])

min_max = preprocessing.MinMaxScaler()
array = min_max.fit_transform(newdata)


import kmapper as km
from sklearn import manifold
from sklearn import cluster

mapper = km.KeplerMapper()

projected_data = mapper.fit_transform(array, projection=manifold.TSNE())

graph = mapper.map(projected_data,
                   clusterer=cluster.DBSCAN(eps=0.3, min_samples=3),
                   nr_cubes=20, overlap_perc=0.2)

mapper.visualize(graph,
                 path_html="mydata_race.html",
                 graph_gravity=0.25,
                 custom_tooltips=race)

mapper.visualize(graph,
                 path_html="mydata_gender.html",
                 graph_gravity=0.25,
                 custom_tooltips=gender)

mapper.visualize(graph,
                 path_html="mydata_age.html",
                 graph_gravity=0.25,
                 custom_tooltips=age)