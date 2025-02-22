class Passage(str):
    babalmandab = 'babalmandab'
    bosporus = 'bosporus'
    gibraltar = 'gibraltar'
    suez = 'suez'
    panama = 'panama'
    ormuz = 'ormuz'
    northwest = 'northwest'
    malacca = 'malacca'
    sunda = 'sunda'
    chili = 'chili'
    south_africa = 'south_africa'
    bering = 'bering'


    @classmethod
    def valid_passages(cls):
        return {value for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(value)}
    
    @classmethod
    def filter_valid_passages(cls, potential_values):
        valid_passages = cls.valid_passages()
        unique_passages = set()
        for value in potential_values:
            if value in valid_passages:
                unique_passages.add(value)
        return list(unique_passages)
