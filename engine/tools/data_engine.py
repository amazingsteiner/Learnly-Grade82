from statistics import mean,median,multimode
class DataEngine:
    def summary(self,values):
        v=[float(x) for x in values]
        return {"count":len(v),"sum":sum(v),"mean":mean(v) if v else None,"median":median(v) if v else None,
                "mode":multimode(v) if v else [],"minimum":min(v) if v else None,"maximum":max(v) if v else None,
                "range":max(v)-min(v) if v else None}
