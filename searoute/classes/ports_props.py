import operator

class PortProps(tuple):
    port_id = property(operator.itemgetter(0))
    share = property(operator.itemgetter(1))
    props = property(operator.itemgetter(2))

    def __new__(self, port_id, share = 1, props = None):
        return tuple.__new__(PortProps, (str(port_id), share, props))