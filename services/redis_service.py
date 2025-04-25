import redis 
import json
import os

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(os.getenv("REDIS_URL"))

    def set_session(self, session_id, session_data):
        self.redis.set(session_id, json.dumps(session_data))
        print("Session stored")
        return

    def get_session(self, session_id):
        session = self.redis.get(session_id)
        return json.loads(session)     

    def delete_session(self, session_id):
        self.redis.delete(session_id)
        print(f'Session: {session_id} deleted.')