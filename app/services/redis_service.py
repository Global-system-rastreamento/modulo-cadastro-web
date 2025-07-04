import os
import redis
import streamlit as st
import uuid
import time
from contextlib import contextmanager
import atexit
from functools import lru_cache

# --- Redis Connection ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD') # Ensure this is set in .env or provide default
REDIS_DB_MAIN = int(os.getenv('REDIS_DB_MAIN', 8))

@lru_cache(maxsize=1)
def get_redis_client(db: int = REDIS_DB_MAIN):
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=db, decode_responses=True)
        redis_client.ping()
        return redis_client
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis DB {REDIS_DB_MAIN}: {e}")
        exit(1)

redis_client = get_redis_client()

class SafeRedisLock:
    def __init__(self, redis_client, key, expire_time=30):
        self.redis_client = redis_client
        self.key = key
        self.expire_time = expire_time
        self.lock_id = str(uuid.uuid4())  # ID único para este processo
        self.acquired = False
    
    def acquire(self, timeout=60):
        """Adquire o lock com ID único"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Tenta adquirir com ID único
            acquired = self.redis_client.set(
                self.key, 
                self.lock_id, 
                nx=True, 
                ex=self.expire_time
            )
            
            if acquired:
                self.acquired = True
                return True
            
            time.sleep(1)
        
        return False
    
    def release(self):
        """Libera o lock apenas se foi este processo que adquiriu"""
        if not self.acquired:
            return False
        
        # Script Lua para liberação segura
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        script = self.redis_client.register_script(lua_script)
        result = script(keys=[self.key], args=[self.lock_id])
        
        if result:
            self.acquired = False
            return True
        return False

@contextmanager
def safe_redis_lock(key, timeout=60, expire=30):
    """Context manager que garante liberação do lock"""
    
    lock = SafeRedisLock(redis_client, key, expire)
    
    try:
        # Registra cleanup para casos extremos
        def cleanup():
            if lock.acquired:
                lock.release()
        
        atexit.register(cleanup)
        
        # Tenta adquirir o lock
        if lock.acquire(timeout):
            yield lock
        else:
            raise TimeoutError(f"Não foi possível adquirir lock para {key}")
    
    except Exception as e:
        st.error(f"Erro durante operação com lock: {e}")
        raise
    
    finally:
        # SEMPRE tenta liberar
        try:
            lock.release()
            atexit.unregister(cleanup)
        except:
            st.warning("Aviso: Possível problema ao liberar lock")