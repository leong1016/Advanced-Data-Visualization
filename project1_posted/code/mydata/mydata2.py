import pandas as pd
import sklearn as sk
import kmapper as km


raw = pd.read_csv('mydata2.csv', header=None)

data = raw.iloc[:,:4]
label = raw.iloc[:,4]

mapper = km.KeplerMapper(verbose=2)

projected_data = mapper.fit_transform(data, projection=sk.manifold.TSNE())

graph = mapper.map(projected_data,
                   clusterer=sk.cluster.DBSCAN(eps=0.3, min_samples=3),
                   nr_cubes=10, overlap_perc=0.25)

mapper.visualize(graph,
                 path_html="mydata2.html",
                 graph_gravity=0.1,
                 custom_tooltips=label)