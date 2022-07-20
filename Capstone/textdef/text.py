
from ast import ImportFrom

#import importlib_metadata

#https://cloud.mongodb.com/v2/61f573b06f97eb56adb5875f#metrics/replicaSet/61f574a111b8177a34f94684/explorer/test/Keywords/find
from gensim.summarization import keywords
text1 = "I am looking for a book to read that is absolutely magical (does not need to have magic in it, more the feelings it sparks) something that will grip me from the very beginning and make me feel as though as I am living the story myself. Bonus if it has the ability to make me laugh and cry. Basically just looking for an absolutely captivating book that will make me read way past when I should have gone to bed."
print(len(text1.split()))
c=int(len(text1.split())/5)
a=keywords(text1)
import pymongo
# #myclient = pymongo.MongoClient("mongodb://localhost:27017/")

myclient = pymongo.MongoClient("mongodb+srv://admin:12345@cluster0.sns8m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = myclient.test
print(db)
# mydb = myclient["test"]
# mycol1 = mydb["Keywords"]
# mycol1.insert_one({"words":a})
print(a)
