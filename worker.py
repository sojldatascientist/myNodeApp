import os

import redis,urllib
from rq import Worker, Queue, Connection
from redis import Redis

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
#conn = redis.from_url(redis_url)



redis_url = os.getenv('REDISTOGO_URL')

urllib.parse.uses_netloc.append('redis')
url = urllib.parse.urlparse(redis_url)
conn = Redis(host=url.hostname)#, port=int(url.port), db=0, password=int(url.password))



if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()



