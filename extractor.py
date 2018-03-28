import matplotlib as plt
import re
import glob
import os

#  3 priorities: high med low
#  disproportionally distributed such that most utilization is on one of the
#  three
#  visualiza by the following:
#  per task utilization

def getId(me):
    return me[3]["id"], me[2]["id"], me[1]["id"]

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

# column accuracy
def getPrecision(cnf, me):
    hi, mi, li = getId(me)
    h = cnf[hi][hi]
    m = cnf[mi][mi]
    l = cnf[li][li]
    for i in range(4):
        ht += cnf[i][hi]
        mt += cnf[i][mi]
        lt += cnf[i][li]
    return h/ht, m/mt, l/lt

# row accuracy
def getRec(cnf, me):
    hi, mi, li = getId(me)
    h = cnf[hi][hi]
    m = cnf[mi][mi]
    l = cnf[li][li]
    for i in range(4):
        ht += cnf[hi][i]
        mt += cnf[mi][i]
        lt += cnf[li][i]
    return h/ht, m/mt, l/lt

def extractId(metas):
    high = []
    med  = []
    low  = []
    for me in metas:
        h, m, l = getId(me)
        high.append(h)
        med.append(m)
        low.append(l)
    return high, med, low

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

def extractRecall(cnfs, metas):
    ha = []
    ma = []
    ia = []
    for i in range(len(cnfs)):
        h, m, l = getRec(metas(i))
        ha.append(h)
        ma.append(m)
        la.append(l)
    return ha, ma, la

def extractPrecision(cnfs, metas):
    ha = []
    ma = []
    ia = []
    for i in range(len(cnfs)):
        h, m, l = getPrecision(metas(i))
        ha.append(h)
        ma.append(m)
        la.append(l)
    return ha, ma, la

def extractExecution(metas):
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
    me = {"name":filename}
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

                taskId = parts[0]
                taskId = re.sub(r'\W+', ' ', taskId)
                taskId = int(taskId.strip().split(" ")[1])

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
                me[pri] = {"id": taskId, "exe":exe,"per":per,"off":offs}
    return me


def plotAccVsTaskUtil(cnfs, metas):
    if len(cnfs) != len(metas):
        return None

    ha, ma, ia = extractAccuracy(cnfs, metas)
    hu, mu, iu = extractUtility(metas)

    plt.scatter(hu, ha, c='r')
    plt.scatter(mu, ma, c='g')
    plt.scatter(lu, la, c='b')
    plt.plot()

    return


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

    whiteList = []

    for me in heavyH:
        whiteList.append(me["name"])
        print(me["name"])
    for me in heavyM:
        whiteList.append(me["name"])
    for me in heavyL:
        whiteList.append(me["name"])



    '''
    blackList = set(metaFiles) - set(whiteList)
    for b in blackList:
        os.remove(b)
    '''

