import redis
import time

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=8080, db=0)

    def get(self, key):
        return self.redis_client.get(key)

    def set(self, key, value, expire_time):
        self.redis_client.setex(key, expire_time, value)
        
    def keys(self,pattern="*"):
        return self.redis_client.scan_iter(match=pattern)

# 測試程式碼
cache = RedisCache()

# 將資料放入快取，設置有效期為5秒
cache.set('name', 'John', 5)
cache.set('age', 30, 10)

# 從快取中獲取資料
name = cache.get('name')
age = cache.get('age')
keys = list(cache.keys())

print(name.decode('utf-8'))  # 輸出: b'John' (在Redis中存儲的資料是bytes類型)
print(age.decode('utf-8'))   # 輸出: b'30'
print(len(keys))
time.sleep(6)  # 等待6秒，讓'name'過期
name = cache.get('name')
age = cache.get('age')

print(name)  # 輸出: None
# 如果 'name' 不存在，或已過期，name_ttl 將為 -2
name_ttl = cache.redis_client.ttl('name')
print(f"名稱快取時間:{name_ttl}")


print(age.decode('utf-8'))
age = cache.get('age')
while age != None:
# 如果 'age' 不存在，或已過期，age_ttl 將為 -1
    age_ttl = cache.redis_client.ttl('age')
    print(f"年齡快取剩餘時間:{age_ttl}")
    time.sleep(1)
    age = cache.get('age')




# import time
# import threading

# class SimpleCache:
#     def __init__(self):
#         self.cache = {}

#     def get(self, key):
#         item = self.cache.get(key)
#         if item and time.time() < item['expire_time']:
#             return item['value']
#         else:
#             self.cache.pop(key, None)
#             return None

#     def set(self, key, value, expire_time):
#         self.cache[key] = {
#             'value': value,
#             'expire_time': time.time() + expire_time
#         }

#     def clean_expired(self):
#         while True:
#             expired_keys = [key for key, item in self.cache.items() if time.time() >= item['expire_time']]
#             for key in expired_keys:
#                 self.cache.pop(key, None)
#             time.sleep(60)  # 每隔60秒清理一次過期資料

# # 測試程式碼
# cache = SimpleCache()

# # 將資料放入快取，設置有效期為5秒
# cache.set('name', 'John', 30)
# cache.set('age', 30, 30)

# # 啟動線程，定期清理過期資料
# clean_thread = threading.Thread(target=cache.clean_expired)
# clean_thread.daemon = True
# clean_thread.start()

# # 從快取中獲取資料
# name = cache.get('name')
# age = cache.get('age')

# print(name)  # 輸出: John
# print(age)   # 輸出: 30

# while cache.get('age') and cache.get('name'):
#     timer = time.sleep(10)
#     print(f"快取資料剩餘{timer}")
#     # name = cache.get('name')
#     # age = cache.get('age')
#     # print(f"name:{name}")  # 輸出: None
#     # print(f"age:{age}")

