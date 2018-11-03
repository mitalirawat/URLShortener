import unittest
import dateutil.parser
from bson.objectid import ObjectId
from bson import SON
from apis import create_app
from mockupdb import go, Command, MockupDB, OpMsg, OpReply
import json
import time

dateStr = "2018-11-11T00:00:00.000Z"
date = dateutil.parser.parse(dateStr)
mapping_dict={"e5a53874fbde55": {'_id': "5bdb5bb371456673d36ba963", 'shorturl' : "e5a53874fbde55",
    	 "longurl" : "newlonnnn44", "events" : [date]},
    	 "fggg874fbde55": None}

class MockupDBFlaskTest(unittest.TestCase):
    def setUp(self):
        self.server = MockupDB(auto_ismaster=True)
        self.server.run()
        self.app = create_app(self.server.uri).test_client()

    def tearDown(self):
        self.server.stop()

    def mock_db_get(self, url=None):
    	# dateStr = "2018-11-11T00:00:00.000Z"
    	# date = dateutil.parser.parse(dateStr)
    	request = self.server.receives(
        OpMsg('find', 'urls', filter={'shorturl': url}))

    	request.ok(cursor={'id': 0, 'firstBatch': [mapping_dict[url]]})

    def mock_db_update(self):

		request = self.server.pop().reply({"modified_count":1})

    def mock_db_get_many(self, url=None):
        request = self.server.pop()
        # request = self.server.receives(
        # OpMsg({"count": "urls", "query": {"shorturl": url}}))
        request.ok(cursor={'id': 0, 'firstBatch': [mapping_dict[url]], 'count':1})

    def test_get_url_not_empty(self):
    	future = go(self.app.get, "/urls/e5a53874fbde55")
    	self.mock_db_get(url="e5a53874fbde55")
    	self.mock_db_update()

    	http_response = future()
    	# print http_response.status
    	# print http_response.mimetype
    	# print http_response.response
    	# print http_response.get_data()
    	self.assertEqual(("Long url is : newlonnnn44\n"),
                     http_response.get_data())

    def test_get_url_not_found(self):
    	future = go(self.app.get, "/urls/fggg874fbde55")
    	self.mock_db_get(url="fggg874fbde55")

    	http_response = future()
    	self.assertEqual("No long url found for this short url fggg874fbde55\n",
                     http_response.get_data())

    def test_get_access_time_all(self):

        future = go(self.app.get, "/urls/alltime_access/e5a53874fbde55")
    	self.mock_db_get_many(url="e5a53874fbde55")

    	http_response = future()
    	self.assertEqual("Access times for url: 'e5a53874fbde55'; for time duration: ' all' is: 1\n",
                     http_response.get_data())


if __name__ == '__main__':
	unittest.main()


