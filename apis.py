from bson.objectid import ObjectId
from flask import Flask, request, Response
from flask_restful import Resource, Api
from flask_bcrypt import Bcrypt
from pymongo.errors import ConnectionFailure
import json
import pymongo
import hashlib
import time
import random
from datetime import datetime

import settings

''' constants to keep track of access events'''
day_in_seconds = 24*60*60
days_in_a_week = 7

def create_app(mongo_uri):
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    api = Api(app)
    myclient  = pymongo.MongoClient(mongo_uri)
    urlcoll = myclient.UserInfo.urls

    # create_urls creates short urls for the given list if urls and adds them to the DB
    @app.route('/urls', methods=['POST', 'DELETE'])
    def create_urls():

        url_data = request.json
        if request.headers['Content-Type'] != 'application/json':
            return settings.create_error_response(errmsg="415 Unsupported Media Type")
        
        if request.method == "POST":
            err = add_urls(url_data)
            if err:
                return settings.create_error_response(str(err))

            create_url_response(url_data)

        resp = Response("Response:" + json.dumps(url_data) + "\n", status=200, mimetype='application/json')
        return resp
            
    @app.route('/urls/<url_id>', methods = ['GET'])
    def get_url(url_id):

        try:
            url = urlcoll.find_one({"shorturl":url_id})
        except ConnectionFailure:
            return settings.create_error_response('connection closed for DB, recheck')
        if url == None:
            respdata="No long url found for this short url " +url_id
            resp = Response(respdata +"\n", status=200, mimetype='application/json')
            return resp

        respstr=""
        longurl = url["longurl"]
        #append the current time to the list of access events for this short url
        url["events"].append(datetime.now())
        r = urlcoll.update_one({'_id':url["_id"]}, {"$set": url}, upsert=False)
        
        respstr = "Long url is : "+ longurl
        resp = Response(respstr +"\n", status=200, mimetype='application/json')
        #print resp
        return resp

    #to get the number of times this url has been accessed
    @app.route('/urls/alltime_access/<url_id>', methods = ['GET'])
    def get_allaccess_times(url_id):
        return get_access_times(url_id)

    #to get the number of times this url is accessed in the last week
    @app.route('/urls/week_access/<url_id>', methods = ['GET'])
    def get_weekaccess_times(url_id):
        return get_access_times(url_id, time="week")

    #to get the number of times this url is accessed in the past 24 hours
    @app.route('/urls/day_access/<url_id>', methods = ['GET'])
    def get_dayaccess_times(url_id):
        return get_access_times(url_id, time="day")
        
    # get all the url data from the DB
    @app.route('/urls', methods=['GET'])
    def get_urls():
        data = {}
        urllist=[]
        cursor = urlcoll.find()
        for url in cursor:
            urllist.append(url)
        data["urls"]=urllist
        create_url_response(data)
        resp = Response("Response:" + json.dumps(data) + "\n", status=200, mimetype='application/json')
        return resp

    def generate_short_url(longurl):
        hashnew = hashlib.sha1(longurl)
        hashnew = hashnew.hexdigest()[:12]
        print "hashnew is" + hashnew
        #hashnew.update(str(time.time()))
        done = False
        counter = 0
        while not done:

            random_number = random.randint(1, 100)
            short_url = hashnew+str(random_number)
            cursor = urlcoll.find({"shorturl":short_url})
            if cursor.count() == 0:
                done = True
            counter +=1
            if counter > 100:
                return None, Error("could not generate short url, too many collisions")

        return short_url, None


    def add_urls(url_data):
        
        urllist = url_data["urls"]
        for url in urllist:
            if not validate_url(url):
                return settings.create_error_response(errmsg="invalid or missing keys in data\n")
            short_url,err = generate_short_url(url["longurl"])
            if err: return err
            url["shorturl"] = short_url
            url["events"] = []

        x = urlcoll.insert_many(urllist)
        print x.inserted_ids
        return None
            

    def get_access_times(url_id, time="all"):
        cursor = urlcoll.find({"shorturl":url_id})

        #there was no hasNext() in cursor.Cursor for pymongo
        if cursor.count() != 0:
            url = cursor.next()
        else: 
            respdata="No long url found for this short url" + url_id
            return create_error_response(respdata)

        longurl = ""
        url["id"] = str(url["_id"])
        url.pop("_id")
        accesstimes = url["events"]
        #check if it is null
        count =0
        curr_time = datetime.now()

        #reversed returns an iterator that accesses the given sequence in the reverse order.
        for acctime in reversed(accesstimes):
            timedelta = curr_time - acctime
            if time =="day" and timedelta.seconds > day_in_seconds:
                break
            if time == "week" and timedelta.days > days_in_a_week:
                break
            count+=1

        respdata = 'Access times for url: \'{}\'; for time duration: \' {}\' is: {}'.format(url_id, time, count)
        resp = Response(respdata +"\n", status=200, mimetype='application/json')
        return resp

    def validate_url(data):
        if "longurl" not in data:
            return False
        return True

    def create_url_response(data):
        for url in data["urls"]:
            url["id"] = str(url["_id"])
            url.pop("_id", None)

    return app

if __name__ == '__main__':
    app = create_app("mongodb://localhost:27017/")
    #settings.init()
    app.run(host= '0.0.0.0', port='5002')