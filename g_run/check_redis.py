import os

#from redis import Redis
import redis

from rq import Worker, Queue, Connection


#r = redis.Redis(host='localhost', port=6379, db=1)
#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

#conn.set('CasG', 'world')

value = conn.get('CaseyG')
value2 = conn.get("CasG")

print(str(value))
print(str(value2))