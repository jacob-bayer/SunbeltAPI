import os
from api import app
import redis
from rq import Worker, Queue, Connection
import argparse
from dotenv import load_dotenv
load_dotenv()

listen = ['SunbeltInsertQueue']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # This is necessary because the app context doesnt include accurate debug state
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--prod', help='Use prod database', action='store_const', 
                                    const=True, default=False)
    args = parser.parse_args()

    with app.app_context():
        with Connection(conn):
            worker = Worker(list(map(Queue, listen)))
            worker.work()