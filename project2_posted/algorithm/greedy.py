
# coding: utf-8

# In[ ]:


import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt


# In[ ]:


empinfo = pd.read_csv('UT_asu_exampleData.csv', thousands=',')
empinfo.set_index('geoid', inplace=True)


# In[ ]:


emp = empinfo[['name', 'pop', 'emp', 'unemp']]


# In[ ]:


geoinfo = gpd.read_file('tl_2016_49_tract/tl_2016_49_tract.shp')
geoinfo['geoid'] = geoinfo['GEOID'].astype(str).astype(int)
geoinfo.set_index('geoid', inplace=True)


# In[ ]:


geo = geoinfo[['geometry']]


# In[ ]:


# emp2 = empinfo[['name', 'pop', 'emp', 'unemp']]
# geo2 = geoinfo[['GEOID', 'geometry']]
# d3 = geo2.merge(emp2, left_index=True, right_index=True)
# d3 = d3.rename(columns={'GEOID':'geoid'})
# d3.to_file('../vis/utah.json', driver="GeoJSON")


# In[ ]:


data = geo.merge(emp, left_index=True, right_index=True)
data['seed'] = data['unemp']/(data['emp']+data['unemp']) >= 0.065
data['count'] = 1


# In[ ]:


def union(data, p, q):
    for i, r in data.iterrows():
        if (r['group'] == q):
            data.loc[i, 'group'] = p


# In[ ]:


def expand(rawdata):
    data = rawdata.copy()
    t = 0
    while (True):
        nseeds = data[data['seed'] > 0.0].shape[0]
        cnt= 0
        for index, row in data.iterrows():
            if (row['seed'] < 1.0):
                continue;
            maxrate = 0
            maxgeoid = 0
            counter = 0
            for i, r in data.iterrows():
                if (i == index):
                    continue;
                if (r['geometry'].touches(row['geometry'])):
                    if (r['unemp'] + r['emp'] == 0):
                        rate = 0
                    else:
                        rate = r['unemp'] / (r['unemp'] + r['emp'])
                    if (rate > maxrate):
                        counter += 1
                        maxrate = rate
                        maxgeoid = i
            if (counter == 1):
                for i, r in data.iterrows():
                    if (i == index):
                        continue;
                    maxpop = 0
                    if (r['geometry'].touches(row['geometry'])):
                        if ((r['unemp'] + row['unemp']) / (r['unemp'] + row['unemp'] + r['emp'] + row['emp']) >= 0.065):
                            maxpop = r['pop']
                            maxgeoid = i
            candidate = data.loc[maxgeoid]
            newemp = row['emp'] + candidate['emp']
            newunemp = row['unemp'] + candidate['unemp']
            if (newemp + newunemp == 0):
                newrate = 0
            else:
                newrate = newunemp / (newunemp + newemp)
            if (newrate >= 0.065):
                data['group'] = data.index
                union(data, index, maxgeoid)
                data = data.dissolve(by='group', aggfunc='sum')
            else:
                cnt += 1
        print('{} != {}'.format(nseeds, cnt))
        if (nseeds == cnt):
            break;
    return data


# In[ ]:


newdata = expand(data)


# In[ ]:


newdata.plot(figsize=(5, 5), column='seed')
plt.show()


# In[ ]:


high = newdata[newdata['seed'] > 0.0]
low = newdata[newdata['seed'] == 0.0]


# In[ ]:


components = []
asu = set()
for index, row in high.iterrows():
    component = set()
    for i, r in data.iterrows():
        if (row['geometry'].contains(r['geometry'])):
            component.add(i)
            asu.add(i)
    components.append(component)


# In[ ]:


highresult = high.drop('geometry', axis=1)
highresult['rate'] = highresult['unemp'] / (highresult['unemp'] + highresult['emp'])
highresult = highresult.join(pd.Series(components, index=highresult.index, name='components'))
highresult.reset_index(drop=True).to_csv('greedy_high.csv')


# In[ ]:


lowresult = low.drop('geometry', axis=1)
lowresult['rate'] = lowresult['unemp'] / (lowresult['unemp'] + lowresult['emp'])
lowresult['components'] = lowresult.index
lowresult.reset_index(drop=True).to_csv('greedy_low.csv')


# In[ ]:


for i in range(len(components)):
    result2 = emp.loc[components[i]]
    result2json = result2.to_json(orient='index')
    with open('asu'+str(i+1)+'.json', 'w') as f:
        f.write(result2json)


# In[ ]:


result2 = emp.loc[asu]
result2json = result2.to_json(orient='index')
with open('asu.json', 'w') as f:
    f.write(result2json)

