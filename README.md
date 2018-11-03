# URLShortener

This repository implements a basic RESTful HTTP API for-

* creating a shortened url from a given long url, 
* get number of times a short url has been accessed in the last 24 hours, in the last week or all number of times

App defined in apis.py.

**Database**

1. One mongodb collection to store data.

 Urls: attributes
 
    shorturl
    longurl
    events : list of timestamps when this short url has been accessed
    
**Usage via Curl**

This implementation has been hosted on a VM and below are
some examples of curl requests that can be sent to the server.

Add a long url: Returns short url for the given long url

`curl -H "Content-type: application/json" -X POST http://35.237.34.177:5002/urls -d '{"urls": [{"longurl":"aaaaaaaaaaaaaaaaaa222"}]}'`
  
Get all urls information from DB:

`curl -X GET http://35.237.34.177:5002/urls`

Get number of times a short url has been accessed: Replace short_url_id value with the short url returned from the POST call.

`curl -H "Content-type: application/json" -X GET http://35.237.34.177:5002/urls/alltime_access/529229d1978f23`

Get number of times a short url has been accessed in the past 24 hours.

`curl -H "Content-type: application/json" -X GET http://35.237.34.177:5002/urls/day_access/529229d1978f23`

Get number of times a short url has been accessed in the last 7 days.

`curl -H "Content-type: application/json" -X GET http://35.237.34.177:5002/urls/week_access/529229d1978f23`

*Test Script*

Including a python script that runs few testcases for unit testing functions. To run it, use the following command:

`python test_unittest.py`

**Future Work**:

1. Currently, when short url is accessed, I add an event with the current timestamp to this url.
Also need to include events when long url is accessed.
2. Add more testcases specially with respect to connection failures
3. Hash calculation to include alphabets more frequently, default python implementation seems to be using digits more often.


