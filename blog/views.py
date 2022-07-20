from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render ,HttpResponse,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User,auth
import datetime
from blog import views
from django.contrib.auth import logout,authenticate, login
import numpy as np
# Create your views here.
import pymongo
from gensim.summarization import keywords
from bson.objectid import ObjectId
from .models import *
from nltk.stem import PorterStemmer 
import nltk
from django.contrib import messages
import json
from django.http import JsonResponse
import time
from django.core.serializers import serialize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
def index (request):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    #myclient = pymongo.MongoClient("mongodb+srv://admin:12345@cluster0.sns8m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = myclient.test
    print(db)
    mydb = myclient["test"]
    mycol1 = mydb["blogs2"]
    mydoc = mycol1.find({'post_type':"post"}).limit(300)
    a=[]
    
    for i in mydoc:
        c=[]
        i['id']=str(i['_id'])
        for j in i['cmm']:
            print(j)
            temp=mycol1.find_one(j)
            c.append(temp)
        i['comment']=c
        i['c_n']=len(c)
        a.append(i)
    return render(request,'home.html',{'mydoc':a})
def signup (request):
    if request.method == 'POST':
      form=UserCreationForm(request.POST)

      if form.is_valid():
          form.save()
          return redirect('login')
    else:
        form=UserCreationForm()
    return render (request,'singnup.html',{'form': form})

def logout (request):
    if request.user.is_authenticated:
        auth.logout(request)
        messages.error(request, 'Logout.')
        return redirect('/')
    else:
        return HttpResponse("Please Login First")

def login (request):

    if request.method=='POST':
        username1=request.POST['username']
        password1=request.POST['password']
        print(username1)
        print(password1)
        print("_____________________________")
        user=authenticate(username=username1,password=password1)
        p=Profile.objects.all()
        if user is not None:
            auth.login(request, user)
            flag=0
            for temp in p:
                s1=str(temp.user)
                s2=str(username1)
                if s1==s2:
                    flag=1
            print("Flag_____________",flag)

            if flag==0:
                new_pro=Profile(user=request.user)
                new_pro.save()
            messages.success(request, 'Login Successfully')
            return redirect("/")
        else:
            return redirect("/")
            #return HttpResponse("Information is not correct")
def post_text(x,privacy,cmm,request):
    print("Working____________________________")
    text_tokens = nltk.word_tokenize(x)
    
    w=keywords(x, words=5)
    
    splitString = w.split("\n") 
    
    for a in splitString:
        if " " in a:
            b=a.split()
            for temp in b:
                splitString.append(temp)
    w_array=[]
    wt=[]
    ps =PorterStemmer()

    for fw in text_tokens:
        rootWord=ps.stem(fw)
        wt.append(rootWord)
    r_array=[]
    c_array=[]
    for fw in splitString:
        
        rootWord=ps.stem(fw)

        wordfreq = wt.count(rootWord)
        r_array.append(rootWord)
        w_array.append({"word":rootWord, "frequency":wordfreq, "org_word":fw})
    return {'text':x,'keywords':w_array, 'cls_status':ObjectId(), 'author':str(request.user.username),'post_type':cmm,'cmm':c_array, 'privacy':privacy}

def postText (request):
    if request.method=='POST':
        x=request.POST['text']
        privacy=request.POST['privacy']
        data=post_text(x,privacy,'post',request)


        #Save in db
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        #myclient = pymongo.MongoClient("mongodb+srv://admin:12345@cluster0.sns8m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = myclient.test
        #print(db)
        mydb = myclient["test"]
        mycol1 = mydb["blogs2"]
        clscol=mydb["Kcluster"]
        c_array=[]
        id=mycol1.insert_one(data)
        
    
    messages.success(request, 'Post Successfully')
    return redirect('/')


def profile(request):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    #myclient = pymongo.MongoClient("mongodb+srv://admin:12345@cluster0.sns8m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = myclient.test
    print(db)
    print(request.user.username)
    print("____________________________________")
    mydb = myclient["test"]
    mycol1 = mydb["blogs2"]
    mydoc = mycol1.find({'author':str(request.user.username)})
    a=[]

    
    for i in mydoc:
        c=[]
        i['id']=str(i['_id'])
        for j in i['cmm']:
            print(j)
            temp=mycol1.find_one(j)
            c.append(temp)
        i['comment']=c
        i['c_n']=len(c)
        a.append(i)
    return render(request,'profile.html',{'mydoc':a})


def relaventPost(request):
    if request.method=='GET':
        
        s1=time.time()
        key=request.GET['post_id']
        print("___________________"+key+"_________________________")
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["test"]
        mycol1 = mydb["blogs2"]
        mycol2=mydb["Kcluster"]
        mydoc = mycol1.find_one({'_id':ObjectId(key)})
        my_words=[]
        for i in mydoc['keywords']:
            my_words.append(i['word'])
        #clusterKey=mydoc['cls_status']
        cluster2=mycol2.find()

        #print(cluster['text_set'])
        data=[]
        data.clear()

        for cluster in cluster2:
            a_set=my_words
            b_set=cluster['rep_words']
            similarity=int(len(set(a_set)&set(b_set))) / int(len(set(a_set)|set(b_set)))
            print(similarity)
            print("Similarity___________________________________")
            if similarity>0.1:
                for temp in cluster['text_set']:

                    if str(temp)!=str(key):
                        print(temp)
                        x=mycol1.find_one({'_id':ObjectId(temp),'privacy':"enable"})
                        my_words2=[]
                        for i in x['keywords']:
                            my_words2.append(i['word'])
                        a_set2=my_words2
                        b_set2=my_words
                        similarity2=int(len(set(a_set2)&set(b_set2))) / int(len(set(a_set2)|set(b_set2)))
                        print(similarity2)
                        print("Similarity2_______________________")
                        if similarity2>0.1:

                            return_sub_array = {}
                            return_sub_array['author'] = x['author']
                            return_sub_array['text'] = x['text']
                            fName=""
                            lName=""
                            img=""
                            address=""
                            email=""
                            phone=""
                            try:
                                u=User.objects.get(username=x['author'])
                                try:
                                    fName=u.profile.first_name
                                    lName=u.profile.last_name
                                    img=u.profile.image
                                    address=u.profile.address
                                    email=u.profile.email
                                    phone=u.profile.phone
                                except:
                                    print("ex")
                            except:
                                print("Exeption")

                            return_sub_array['first_name'] = fName
                            return_sub_array['last_name'] = lName
                            return_sub_array['img'] = str(img)
                            return_sub_array['address'] = address
                            return_sub_array['email'] = email
                            return_sub_array['phone'] = phone

                            data.append(return_sub_array)





        #messages.success(request, 'Most Relavent Posts')
        print(len(data))
        e1=time.time()
        print("_______________________________")
        print("Total Insers Time: ",e1-s1)
        return HttpResponse(json.dumps(data))
     
        
        # return render(request,'relatedpost.html',{'data':data})
 


def postComment(request):
    if request.method=='POST':
        key=request.POST['c_comment']
        x=request.POST['comment']
        privacy=request.POST['privacy']
        data=post_text(x,privacy,'cmm',request)
        
        #Save in db
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        #myclient = pymongo.MongoClient("mongodb+srv://admin:12345@cluster0.sns8m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = myclient.test
        print(db)
        mydb = myclient["test"]
        mycol1 = mydb["blogs2"]
        clscol=mydb["Kcluster"]
        id=mycol1.insert_one(data)

        mycol1.update_one( 
  { '_id' : ObjectId(key) },
  { '$push': { 'cmm': id.inserted_id  } }
)

        messages.success(request, 'Comment Post Successfully')
        return redirect('/')

def delete_text(request):
    if request.method=='POST':
        x=request.POST['target']
        x2=request.POST['target2']
     
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["test"]
        mycol1 = mydb["blogs2"]
        mycol2=mydb["Kcluster"]
        mycol1.delete_one({'_id':ObjectId(x)})
        mycol2.update_one( 
  { '_id' : ObjectId(x2) },
  { '$pull': { 'text_set': x } }

)
 

# )
        return redirect('/profile')
def myFunc(e):
  return e['frequency']
def api_post(request):
    
    x=request.GET['name']
    if x!="":
        text_tokens = nltk.word_tokenize(x)
    #print(text_tokens)
        w=keywords(x, words=10)
        splitString = w.split("\n") 
        for a in splitString:
            if " " in a:
                b=a.split()
                for temp in b:
                    splitString.append(temp)
        w_array=[]
        wt=[]
        ps =PorterStemmer()
    #ps = LancasterStemmer()
        #wordnet_lemmatizer = WordNetLemmatizer()
        #Calculate Frequency
    for fw in text_tokens:
        rootWord=ps.stem(fw)
        wt.append(rootWord)
    #print(wt)
    for fw in splitString:
    
        rootWord=ps.stem(fw)
#      rootWord=wordnet_lemmatizer.lemmatize(fw)
        wordfreq = wt.count(rootWord)
        w_array.append({"word":rootWord, "frequency":wordfreq, "org_word":fw})
        w_array.sort(reverse=True,key=myFunc)
    
    
    tag=[]
    i=0
    n=6
    
    for y in w_array:
        if i>=n:
            break
        else:
            tag.append(y['word'])
            i=i+1
    st=""
    for y in w_array:
        i=0
      
        while i<y['frequency']:
            st=st+" "+y['word']
            i+=1
 
    
    a={'text':x, 'st':st,'tag':tag, 'words':w_array}
    print(a)
    
    

    return HttpResponse(json.dumps(a), content_type='application/json')
def p_api_post(x):
    
    
    if x!="":
        text_tokens = nltk.word_tokenize(x)
    #print(text_tokens)
        w=keywords(x, words=10)
        splitString = w.split("\n") 
        for a in splitString:
            if " " in a:
                b=a.split()
                for temp in b:
                    splitString.append(temp)
        w_array=[]
        wt=[]
        ps =PorterStemmer()
    #ps = LancasterStemmer()
        #wordnet_lemmatizer = WordNetLemmatizer()
        #Calculate Frequency
    for fw in text_tokens:
        rootWord=ps.stem(fw)
        wt.append(rootWord)
    #print(wt)
    for fw in splitString:
    
        rootWord=ps.stem(fw)
#      rootWord=wordnet_lemmatizer.lemmatize(fw)
        wordfreq = wt.count(rootWord)
        w_array.append({"word":rootWord, "frequency":wordfreq, "org_word":fw})
        w_array.sort(reverse=True,key=myFunc)
    
    
    tag=[]
    i=0
    n=6
    
    for y in w_array:
        if i>=n:
            break
        else:
            tag.append(y['word'])
            i=i+1
    st=""
    for y in w_array:
        i=0
      
        while i<y['frequency']:
            st=st+" "+y['word']
            i+=1
 
    
    a={'text':x, 'st':st,'tag':tag, 'words':w_array}
   
    return (a)
def myFunc2(e):
  return e['distance']
def tofind_rel_post(request):
    x=request.GET['clusters']
    
    a=json.loads(x)
    cluster=a['cluster']
    centers=a['centers']
    key_data=a['key_data']
    all_data=a['all_data']
    all_data.append(key_data)
    pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
])      
    print("Pipie Line Ok")
#print(newsgroups_train)
    X = pipeline.fit_transform(all_data).todense()
#print(X)

    pca = PCA(n_components=2).fit(X)
    data2D = pca.transform(X)
    last_data_point=data2D[len(data2D)-1]
    #find nearest clusters
    i=0
    distance=[]
    for a in centers:
        x=last_data_point[0]
        y=last_data_point[1]
        
        x1=float(a['x'])
        y1=float(a['y'])
        d=((x-x1)*(x-x1)+(y-y1)*(y-y1))**0.5
        print("X and y ")
        print(i)
        print(d)
        i=i+1
        distance.append({'cluster':i,'distance':d})
        
    distance.sort(reverse=False,key=myFunc2)
    close_cluster=[distance[0],distance[1],distance[2],distance[4]]
    print(len(cluster))
    i=0
    close_data=[]
    for a in cluster:
        if int(a)==distance[0]['cluster'] or int(a)==distance[1]['cluster'] or int(a)==distance[2]['cluster'] or int(a)==distance[3]['cluster']:
            close_data.append(data2D[i]) 
            i=i+1
    final_close_data=[]
    i=0
    for a in close_data:
        x=last_data_point[0]
        y=last_data_point[1]
        
        x1=float(a[0])
        y1=float(a[1])
        d=((x-x1)*(x-x1)+(y-y1)*(y-y1))**0.5
        final_close_data.append({'data':i,'distance':d})
        i=i+1
    final_close_data.sort(reverse=False,key=myFunc2)
    print(final_close_data)

    return HttpResponse(json.dumps(final_close_data), content_type='application/json')



def new_cluster(request):
    
    x=request.GET["size"]
    array=[]
    #x=["Data"]
    i=0
    while i<int(x):
        array.append(request.GET[str(i)])
        i=i+1
    print(array)
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
    pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
])  
    X = pipeline.fit_transform(array).todense()
    pca = PCA(n_components=2).fit(X)
    k = int(7)
    model = KMeans(n_clusters=k, init='k-means++', max_iter=1000, n_init=1)
    model.fit(X)
    centers2D = pca.transform(model.cluster_centers_)

    result=[]
    for a in model.labels_:
        result.append(str(a))
    cen=[]
    for a in centers2D:
        cen.append({"x":str(a[0]),"y":str(a[1])})
  
    a={'cluster':result,'centers':cen,'size':x}
    return HttpResponse(a, content_type='application/json')

def testing(request):
    print("Working_____________________")
def insert(request):
    x=request.GET["data"]
    data=json.loads(x)
    username=data['username']
    text=data['collection']
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["test"]
    mycol1 = mydb[username+"_blogs2"]
 
    mycol1.insert_one({'text':text,'positionX':9999,'positionY':9999})
    # print(x['collection'])
    
    return HttpResponse("Data Inserted Successfully", content_type='application/json')
def fetch_all(request):
    x=request.GET["data"]
    data=json.loads(x)
    username=data['username']
    print("____________________________")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["test"]
    mycol1 = mydb[username+"_blogs2"]
    data=mycol1.find().limit(100)
    result=[]
    for a in data:
   
        result.append({'text':a['text'],'id':str(a['_id'])})
    print(len(result))
    print("__________text size__________")
    return HttpResponse(json.dumps({'result':result}), content_type='application/json')

def score(X,lebels):
    import sklearn
    print(sklearn.metrics.silhouette_score(X,lebels))
    
def p_all_cluster(request):
    
    username=request.GET['username']

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["test"]
    mycol1 = mydb[username+"_blogs2"]
    data=mycol1.find()
    array=[]
    
    for a in data:
        array.append(a["text"])
    
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
    pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
])  
    X = pipeline.fit_transform(array).todense()
    pca = PCA(n_components=2).fit(X)
    pca2 = PCA(n_components=2).fit(X)
    datacenters2D= pca2.transform(X)
    
    print("Working1")
# print(features)
    i=0
    data=mycol1.find()
    for a in data:
        print(a['_id'])
        print(datacenters2D[i])
        mycol1.update_one( 
  { '_id' : a['_id'] },
  { '$set': { 'positionX':   datacenters2D[i][0]} })
        mycol1.update_one( 
  { '_id' : a['_id'] },
  { '$set': { 'positionY':   datacenters2D[i][1]} }
)
        i=i+1

    k = int(11)
    from sklearn.cluster import MiniBatchKMeans
#Clustering
    model = MiniBatchKMeans(n_clusters=k, init='k-means++', max_iter=1000, n_init=1)
    model.fit(X)
    import sklearn
    print(sklearn.metrics.silhouette_score(X,model.labels_))
    centers2D = pca.transform(model.cluster_centers_)
    print("Working2")
    result=[]
    for a in model.labels_:
        result.append(str(a))
    cen=[]
    for a in centers2D:
        cen.append({"x":str(a[0]),"y":str(a[1])})
  
    a={'cluster':result,'centers':cen}
    mycol2 = mydb[username+"_cluster"]
    mycol2.drop()
    data=mycol2.insert_one(a)
    print("Working3")

    return HttpResponse("Successfully Clusteres", content_type='application/json')

def p_tofind_rel_post(request):
    x=request.GET["data"]
    data=json.loads(x)
    key=data['post_id']
    
    username=data['username']
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["test"]
    text_col = mydb[username+"_blogs2"]
    cluster_col=mydb[username+"_cluster"]
  
    cluster_obj=cluster_col.find()
    centers=[]
    cluster=[]
  
    for a in cluster_obj:
        centers.append(a['centers'])
        cluster.append(a['cluster'])

    dataset=text_col.find()
    
    last_data_point=[]
    data2D=[]
    all_post=[]
    for a in dataset:

        if str(a["_id"])==key:
            print("COndition ok")
            last_data_point=[a['positionX'],a['positionY']]
        data2D.append([a['positionX'],a['positionY']])
        all_post.append(a['text'])
   

    #find nearest clusters
    i=0
    distance=[]
    print("__________________________")
    for a in centers[0]:
        x=last_data_point[0]
        y=last_data_point[1]
        
        x1=float(a['x'])
        y1=float(a['y'])
        d=((x-x1)*(x-x1)+(y-y1)*(y-y1))**0.5
        print("X and y ")
        print(i)
        print(d)
        
        distance.append({'cluster':i,'distance':d})
        i=i+1
    distance.sort(reverse=False,key=myFunc2)
    print(len(cluster))
    i=0
    close_data=[]

    for a in cluster[0]:
        if int(a)==int(distance[0]['cluster']) :
            
            close_data.append(data2D[i]) 
            i=i+1
 
 #Find Simila documents
    final_close_data=[]
    i=0
    for a in close_data:
        x=last_data_point[0]
        y=last_data_point[1]
        
        x1=float(a[0])
        y1=float(a[1])
        d=((x-x1)*(x-x1)+(y-y1)*(y-y1))**0.5
        if d<0.7:
            final_close_data.append({'data':i,'distance':d})
        i=i+1
    final_close_data.sort(reverse=False,key=myFunc2)
    print("Final CLose Dataset")
 
  
    result=[]
   
    n=len(final_close_data)
    print(n)
    i=0
    while i<n:
        result.append(all_post[final_close_data[i]["data"]])
        i=i+1
    return HttpResponse(json.dumps(result), content_type='application/json')





