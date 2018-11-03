import pymongo
import flask

# def init():
#     myclient  = pymongo.MongoClient("mongodb://localhost:27017/")
#     global mydb
#     mydb = myclient["UserInfo"]
#     global urlcoll
#     urlcoll  = mydb["urls"]
    

def create_error_response(errmsg="Unexpected error in operation"):
    resp = flask.Response("ErrorResponse:"+errmsg, status=400, mimetype='application/json')
    return resp