class UserInterrupt(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class MissingDataSet(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidOptimizer(Exception):
    def __init__(self,*args,**kwargs):
        InvalidNetworkType.__init__(self,*args,**kwargs)

class InvalidNetworkType(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidBackend(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
