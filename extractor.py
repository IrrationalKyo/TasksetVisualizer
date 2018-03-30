import numpy as np
import matplotlib.pyplot as plt
import re
import glob
import os

#  3 priorities: high med low
#  disproportionally distributed such that most utilization is on one of the
#  three
#  visualiza by the following:
#  per task utilization

def getRep(name):
    frontString = name.split('_')[0]
    rep = int(frontString.split('rep')[1])
    return rep

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
    ht = 0
    mt = 0
    lt = 0
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
    ht = 0
    mt = 0
    lt = 0
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

def getCorrespondingMatrix(cnfDict, metas):
    conf0List = []
    conf99List = []
    for me in metas:
        mId = getRep(me["name"])
        conf0List.append(cnfDict[0][mId])
        conf99List.append(cnfDict[99][mId])
    return conf0List, conf99List

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
    la = []
    for i in range(len(cnfs)):
        h, m, l = getRec(cnfs[i], metas[i])
        ha.append(h)
        ma.append(m)
        la.append(l)
    return ha, ma, la

def extractPrecision(cnfs, metas):
    ha = []
    ma = []
    la = []
    for i in range(len(cnfs)):
        h, m, l = getPrecision(cnfs[i],metas[i])
        ha.append(h)
        ma.append(m)
        la.append(l)
    return ha, ma, la

def extractF1(cnfs, metas):
    hp, mp, lp = extractPrecision(cnfs, metas)
    hr, mr, lr = extractRecall(cnfs, metas)
    hf = []
    mf = []
    lf = []

    for i in range(len(hp)):
        hf.append(2*hp[i]*hr[i]/(hp[i] + hr[i]))
        mf.append(2*mp[i]*mr[i]/(mp[i] + mr[i]))
        lf.append(2*lp[i]*lr[i]/(lp[i] + lr[i]))
    return hf, mf, lf

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

def getOverallAcc(cnf):
    total = 0
    correct = 0
    for i in range(len(cnf)):
        for j in range(len(cnf[0])):
            total += cnf[i][j]
            if i == j:
                correct += cnf[i][j]
    return correct/total

def extractOverallAcc(cnfs):
    output = []
    for cnf in cnfs:
        output.append(getOverallAcc(cnf))
    return output

def extractMatrixId(cnfFileName):
    parts = cnfFileName.split('/')[-1].split('.')
    return int(parts[0])
            
def extractMatrixConf(cnfFileName):
    parts = cnfFileName.split('/')[-1].split('.')
    if parts[1] == 'nnp':
        return 99
    elif parts[1] == 'np':
        return 0
    return -1

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


def plotRecallVsTaskUtil(cnfs, metas):
    if len(cnfs) != len(metas):
        return None

    ha, ma, ia = extractRecall(cnfs, metas)
    hu, mu, iu = extractUtility(metas)

    plt.scatter(hu, ha, c='r')
    plt.scatter(mu, ma, c='g')
    plt.scatter(lu, la, c='b')
    plt.plot()

    return


if __name__ == "__main__":

    dotSize = 4
    print("hello crule world")
    metaFiles = glob.glob("./metas/*_meta.txt")
    medMetas = []
    for mef in metaFiles:
        me = metaParser(mef)
        medMetas.append(me)

    # resultFiles = glob.glob("./medResults/*.npy")
    # group = {0:{}, 99:{}}
    # for mf in resultFiles:
    #     conf = extractMatrixConf(mf)
    #     mId = extractMatrixId(mf)
    #     group[conf][mId]=np.load(mf)
    #
    # conf0List = []
    # conf99List = []
    # for me in medMetas:
    #     mId = getRep(me["name"])
    #     conf0List.append(group[0][mId])
    #     conf99List.append(group[99][mId])
    #
    # h, m, l = extractUtilization(medMetas)
    # hp, mp, lp = extractPrecision(conf0List, medMetas)
    # hr, mr, lr = extractRecall(conf0List, medMetas)
    # hf, mf, lf = extractF1(conf0List, medMetas)
    #
    # f, ((ax00, ax10, ax20), (ax01, ax11, ax21), (ax02, ax12, ax22)) = plt.subplots(3, 3, sharex='col', sharey='row')
    # f.suptitle("Equally Heavy Medium Utility Group")
    # ax00.set_title('Per Task Precision vs Utility')
    # ax00.scatter(h, hp, c='r', s=dotSize)
    # ax00.scatter(m, mp, c='g', s=dotSize)
    # ax00.scatter(l, lp, c='b', s=dotSize)
    #
    # ax01.set_title('Per Task Recall vs Utility')
    # ax01.scatter(h, hr, c='r', s=dotSize)
    # ax01.scatter(m, mr, c='g', s=dotSize)
    # ax01.scatter(l, lr, c='b', s=dotSize)
    #
    # ax02.set_title('Per Task F1 vs Utility')
    # ax02.scatter(h, hf, c='r', s=dotSize)
    # ax02.scatter(m, mf, c='g', s=dotSize)
    # ax02.scatter(l, lf, c='b', s=dotSize)
    #
    #
    # h, m, l = extractPeriod(medMetas)
    # ax10.set_title('Per Task Precision vs Period')
    # ax10.scatter(h, hp, c='r', s=dotSize)
    # ax10.scatter(m, mp, c='g', s=dotSize)
    # ax10.scatter(l, lp, c='b', s=dotSize)
    #
    # ax11.set_title('Per Task Recall vs Period')
    # ax11.scatter(h, hr, c='r', s=dotSize)
    # ax11.scatter(m, mr, c='g', s=dotSize)
    # ax11.scatter(l, lr, c='b', s=dotSize)
    #
    # ax12.set_title('Per Task F1 vs Period')
    # ax12.scatter(h, hf, c='r', s=dotSize)
    # ax12.scatter(m, mf, c='g', s=dotSize)
    # ax12.scatter(l, lf, c='b', s=dotSize)
    #
    #
    # h, m, l = extractExecution(medMetas)
    # ax20.set_title('Per Task Precision vs Execution')
    # ax20.scatter(h, hp, c='r', s=dotSize)
    # ax20.scatter(m, mp, c='g', s=dotSize)
    # ax20.scatter(l, lp, c='b', s=dotSize)
    #
    # ax21.set_title('Per Task Recall vs Execution')
    # ax21.scatter(h, hr, c='r', s=dotSize)
    # ax21.scatter(m, mr, c='g', s=dotSize)
    # ax21.scatter(l, lr, c='b', s=dotSize)
    #
    # ax22.set_title('Per Task F1 vs Execution')
    # ax22.scatter(h, hf, c='r', s=dotSize)
    # ax22.scatter(m, mf, c='g', s=dotSize)
    # ax22.scatter(l, lf, c='b', s=dotSize)
    #
    # plt.show()

    heavyL = pickHeavyL(medMetas)
    print(heavyL)
    heavyM = pickHeavyM(medMetas)
    heavyH = pickHeavyH(medMetas)

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

    print(len(whiteList))


    blackList = set(metaFiles) - set(whiteList)
    for b in blackList:
        os.remove(b)

