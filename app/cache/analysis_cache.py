import hashlib
import json


class AnalysisCache:

    def __init__(self):
        self.cache = {}

    def _key(self, application, credit, fraud):
        raw = json.dumps({
            "app": application,
            "credit": credit,
            "fraud": fraud
        }, sort_keys=True)

        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, application, credit, fraud):
        return self.cache.get(self._key(application, credit, fraud))

    def set(self, application, credit, fraud, value):
        self.cache[self._key(application, credit, fraud)] = value