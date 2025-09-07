class MemoryStore:
    _store = {}

    def set(self, case_id, name, data):
        self._store.setdefault(case_id, {})[name] = data

    def get(self, case_id, name):
        return self._store.get(case_id, {}).get(name)

    def to_dict(self, case_id):
        return self._store.get(case_id, {})
