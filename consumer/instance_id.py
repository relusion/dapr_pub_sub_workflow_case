import os
import uuid

def generate_random_instance_id():
    return str(uuid.uuid4())

class InstanceID:
    _instance = None
    
    def __new__(cls, instance_id=None):
        if cls._instance is None:
            cls._instance = super(InstanceID, cls).__new__(cls)
            cls._instance._id = os.environ.get("INSTANCE_ID", generate_random_instance_id())
        return cls._instance
 
    @property
    def id(self):
        return self._instance._id