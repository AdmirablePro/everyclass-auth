import redis
from everyclass.auth.config import get_config
config = get_config()
redis_client = redis.Redis(host=config.REDIS_CONFIG['host'], port=config.REDIS_CONFIG['port'])

