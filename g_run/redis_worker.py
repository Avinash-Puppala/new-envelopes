import os

#from redis import Redis
import redis

from rq import Worker, Queue, Connection


r = redis.Redis(host='localhost', port=6379, db=1)
#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

#listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

#conn = redis.from_url(redis_url)

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

#r.set('CaseyG', 'world')

#value = conn.get('CaseyG')

#print(value)

#r.delete('hello')
#print(r.get('hello'))

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


"""""
# Returns all workers registered in this connection
redis = Redis()
workers = Worker.count(connection=redis)


# Count the number of workers for a specific queue
queue = Queue('default', connection=redis)
workers = Worker.all(queue=queue)

for worker in Worker.all(queue=queue):
    print(worker)
    os.kill(worker.pid, signal.SIGINT)
    
print(str(workers))
"""
