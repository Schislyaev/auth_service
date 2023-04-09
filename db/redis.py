import redis

from core.settings import settings

redis = redis.from_url(f'redis://{settings.redis_url}:{settings.redis_port}')
