class ArtifactStore:
    _store = {}

    @classmethod
    def set(cls, case_id, name, data):
        cls._store.setdefault(case_id, {})[name] = data

    @classmethod
    def get(cls, case_id, name):
        return cls._store.get(case_id, {}).get(name)

    @classmethod
    def to_dict(cls, case_id):
        return cls._store.get(case_id, {})
