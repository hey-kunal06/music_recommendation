from flask import Flask,jsonify,request
from flask_restful import Api,Resource,reqparse
from sklearn.datasets import (make_blobs,
                                                make_circles,
                                                make_moons)
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.preprocessing  import Normalizer
from scipy.stats import spearmanr
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from datetime import date, timedelta,datetime
from sklearn.preprocessing import StandardScaler
df_info=pd.read_csv('song_info.csv')
df_act=pd.read_csv('song_data.csv')
app=Flask(__name__)
api=Api(app)
playlist=[]
dates=[]
new_list=[]
df_info=pd.read_csv('song_info.csv')
df_act=pd.read_csv('song_data.csv')
df_act=df_act.drop_duplicates(subset=None, keep='first', inplace=False)
df_info=df_info.drop_duplicates(subset=None, keep='first', inplace=False)
df_act=df_act.reset_index()
df_info=df_info.reset_index()
temp=df_act.drop(['song_name'],axis=1)
df=df_act
scaler=Normalizer().fit(temp)
normalized_data=scaler.transform(temp)
normalized_data=pd.DataFrame(normalized_data,index=temp.index,columns=temp.columns)
km_res = KMeans(n_clusters = 500,max_iter=500).fit(normalized_data)
clusters = km_res.cluster_centers_
df['KMeans'] = km_res.labels_
def remove_duplicates (duplist):
  noduplist =[]
  for element in duplist:
    if element not in noduplist:
      noduplist.append(element)

  return noduplist
def sort(li,data):
  temp=0
  speechiness=0
  key=0
  li_score=[]
  for i in range(len(df)):
    if(df['song_name'][i]==data):
      temp=df['tempo'][i]
      speechiness=df['speechiness'][i]
      key=df['key'][i]
  for g in li:
    temp1=0
    speechiness1=0
    key1=0
    for i in range(len(df)):
      if(df['song_name'][i]==g):
        temp1=df['tempo'][i]
        speechiness1=df['speechiness'][i]
        key1=df['key'][i]
        break
    corr_t, _ = spearmanr(temp,temp1)
    corr_s, _ = spearmanr(speechiness, speechiness1)
    corr_k, _ = spearmanr(key, key1)
    li_score.append((corr_t+corr_s+corr_k)/3)
  for i in range(len(li)):
    for j in range(len(li_score)):
      if(li_score[i]<li_score[j]):
        tem=li_score[i]
        li_score[i]=li_score[j]
        li_score[j]=temp
        t=li[i]
        li[i]=li[j]
        li[j]=t
  return li
@app.route('/',methods=['GET','POST'])
def work():
    playlist=request.json['li']['playlist']
    dates=request.json['li']['dates']
    delta=[]
    for i in dates:
      do = datetime.strptime(i,'%d/%m/%y')
      d = datetime.today()-do
      delta.append(d.days)
    for i in range(len(delta)):
      for j in range(i+1,len(delta)):
        if(delta[i]>delta[j]):
          temp=delta[i]
          delta[i]=delta[j]
          delta[j]=temp
          temp2=playlist[i]
          playlist[i]=playlist[j]
          playlist[j]=temp2
    recomm=[]
    p=0
    for g in range(len(playlist)):
      km=0
      recomm.append(playlist[g])
      for i in range(len(df)):
        if(df['song_name'][i]==playlist[g]):
          km=df['KMeans'][i]
          break
      if(p>=0 and p<=5):
        p=p+1
        nam=[]
        for k in range(len(df)):
          if(df['KMeans'][k]==km):
            nam.append(df['song_name'][k])
        name=sort(nam,playlist[g])
        recomm[len(recomm):]=name[:10]
      elif(p>5 and p<15):
        p=p+1
        nam=[]
        for k in range(len(df)):
          if(df['KMeans'][k]==km):
            nam.append(df['song_name'][k])
        name=sort(nam,playlist[g])
        recomm[len(recomm):]=name[:7]
      else:
        nam=[]
        for k in range(len(df)):
          if(df['KMeans'][k]==km):
            nam.append(df['song_name'][k])
        recomm[len(recomm):]=nam
      if(len(recomm)>50):
        break
    r=remove_duplicates(recomm)
    result={
        "playlist":r
    }
    return jsonify(result)
if __name__ == "__main__":
    app.run(debug=True)
