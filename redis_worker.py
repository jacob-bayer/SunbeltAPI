import os
from api import app
import redis
import logging
from rq import Worker, Queue, Connection
import argparse
from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger('REDIS WORKER')
logging.basicConfig(level=logging.INFO)

listen = ['SunbeltInsertQueue']

#app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('LOCAL_SUNBELT_DB_URL') #'sqlite:///app.db'
log.warning('Using prod database')
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # This is necessary because the app context doesnt include accurate debug state
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--prod', help='Use prod database', action='store_const', 
                                    const=True, default=False)
    args = parser.parse_args()

    # figure out how to make the prod stuff work 
    #also see: https://flask-migrate.readthedocs.io/en/latest/#multiple-database-support


    with app.app_context():
        with Connection(conn):
            worker = Worker(list(map(Queue, listen)))
            worker.work()