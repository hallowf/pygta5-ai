import cProfile, pstats, io
# from pstats import SortKey

def h_profile(fnc):

    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sort = "restats"
        ps = pstats.Stats(pr, stream=s)
        ps.strip_dirs().sort_stats("cumulative").print_stats(10)
        print(s.getvalue())
        return retval

    return inner

class UserInterrupt(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
