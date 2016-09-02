"""Memcache for storing data like auth tokens, iqt metadata"""

import memcache


class Cache(object):
    """Context manager for automatically closing memcache connection"""
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cache_api.client.disconnect_all()

    def __enter__(self):
        class CacheResource(object):
            """API for memcache related operations"""
            def __init__(self):
                self.client = memcache.Client([('127.0.0.1', 11211)])

            def set(self, key, val, expiry_time=0):
                """Stores data in memcached"""
                self.client.set(key, val, time=expiry_time)

            def get(self, key):
                """Retrieves data from memcached"""
                return self.client.gets(key)

        self.cache_api = CacheResource()
        return self.cache_api
