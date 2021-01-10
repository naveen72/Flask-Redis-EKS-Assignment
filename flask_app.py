from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(host='my-redis-svc.default.svc.cluster.local', port=6379)

@app.route('/')
def hello():
    count = redis.incr('hits')
    return 'Hello Nclouds Team! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
