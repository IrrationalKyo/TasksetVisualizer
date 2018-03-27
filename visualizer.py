import matplotlib as plt
import re
import glob

#  3 priorities: high med low
#  disproportionally distributed such that most utilization is on one of the
#  three
#  visualiza by the following:
#  per task utilization

def getUtil(me):
    executionTimeH = me[3]["exe"]
    periodH = me[3]["per"]

    executionTimeM = me[2]["exe"]
    periodM = me[2]["per"]

    executionTimeL = me[1]["exe"]
    periodL = me[1]["per"]

    return executionTimeH/periodH,executionTimeM/periodM,executionTimeL/periodL

def getExe(me):
    executionTimeH = me[3]["exe"]
    executionTimeM = me[2]["exe"]
    executionTimeL = me[1]["exe"]
    return executionTimeH, executionTimeM, executionTimeL

def getPer(me):
    periodH = me[3]["per"]
    periodM = me[2]["per"]
    periodL = me[1]["per"]
    return periodH, periodM, periodL


# assumes that the taskset is of size 3 has (high, med, low) priorities
# assumes that metas are parsed and has associated id
def extractUtilization(metas):
    high = []
    med  = []
    low  = []
    for me in metas:
        h, m, l = getUtil(me)
        high.append(h)
        med.append(m)
        low.append(l)
    return high, med, low

def extractPeriod(metas):
    high = []
    med  = []
    low  = []
    for me in metas:
        h, m, l = getExe(me)
        high.append(h)
        med.append(m)
        low.append(l)

    return high, med, low

def extractPeriod(metas):
    high = []
    med  = []
    low  = []
    for me in metas:
        h, m, l = getPer(me)
        high.append(h)
        med.append(m)
        low.append(l)

    return high, med, low

# returns filtered metas with utility heavily distributed to H
def pickHeavyH(metas):
    result = []
    for me in metas:
        h, m, l = getUtil(me)
        if h > m + l:
            result.append(me)
    return result


# returns filtered metas with utility heavily distributed to H
def pickHeavyM(metas):
    result = []
    for me in metas:
        h, m, l = getUtil(me)
        if m > h + l:
            result.append(me)
    return result


# returns filtered metas with utility heavily distributed to H
def pickHeavyL(metas):
    result = []
    for me in metas:
        h, m, l = getUtil(me)
        if l > h + m:
            result.append(me)
    return result

def metaParser(filename):
    me = {}
    with open(filename) as f:
        content = f.readlines()
        for line in content:
            line = line.strip()
            if "TaskSet" in line:
                line = line.replace("("," ")
                line = line.replace(")"," ")
                line = line.replace(":","")
                line = line.strip()
                parts = line.split(" ")
                me["utility"]=float(parts[1])
            elif "Task-" in line:
                parts = line.split(" ")
                parts = parts[1:]
                pri = -1
                exe = -1
                per = -1
                offs= -1
                for e in parts:
                    e = re.sub(r'\W+', ' ', e)
                    ep = e.split(" ")
                    if ep[0] == "p":
                        per = int(ep[1])
                    elif ep[0] == "c":
                        exe = int(ep[1])
                    elif ep[0] == "pri":
                        pri = int(ep[1])
                    elif ep[0] == "offset":
                        offs = int(ep[1])
                me[pri] = {"exe":exe,"per":per,"off":offs}
    return me


if __name__ == "__main__":
    print("hello crule world")
    metaFiles = glob.glob("./lowMetas/*_meta.txt")
    lowMetas = []
    for mef in metaFiles:
        me = metaParser(mef)
        lowMetas.append(me)

    h, m, l = extractUtilization(lowMetas)

    heavyL = pickHeavyL(lowMetas)
    heavyM = pickHeavyM(lowMetas)
    heavyH = pickHeavyH(lowMetas)

    print("high heavy: "+ str(len(heavyH)))
    print("med heavy: "+ str(len(heavyM)))
    print("low heavy: "+ str(len(heavyL)))
