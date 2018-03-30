import matplotlib.pyplot as plt
import numpy as np
import extractor as ext
import glob

def plot(cnfs, metas, title):
    h, m, l = ext.extractUtilization(metas)
    hp, mp, lp = ext.extractPrecision(cnfs, metas)
    hr, mr, lr = ext.extractRecall(cnfs, metas)
    hf, mf, lf = ext.extractF1(cnfs, metas)

    f, ((ax00, ax10, ax20), (ax01, ax11, ax21), (ax02, ax12, ax22)) = plt.subplots(3, 3, sharex='col', sharey='row')
    f.suptitle(title)
    ax00.set_title('Per Task Precision vs Utility')
    ax00.scatter(h, hp, c='r', s=dotSize)
    ax00.scatter(m, mp, c='g', s=dotSize)
    ax00.scatter(l, lp, c='b', s=dotSize)

    ax01.set_title('Per Task Recall vs Utility')
    ax01.scatter(h, hr, c='r', s=dotSize)
    ax01.scatter(m, mr, c='g', s=dotSize)
    ax01.scatter(l, lr, c='b', s=dotSize)

    ax02.set_title('Per Task F1 vs Utility')
    ax02.scatter(h, hf, c='r', s=dotSize)
    ax02.scatter(m, mf, c='g', s=dotSize)
    ax02.scatter(l, lf, c='b', s=dotSize)


    h, m, l = ext.extractPeriod(metas)
    ax10.set_title('Per Task Precision vs Period')
    ax10.scatter(h, hp, c='r', s=dotSize)
    ax10.scatter(m, mp, c='g', s=dotSize)
    ax10.scatter(l, lp, c='b', s=dotSize)

    ax11.set_title('Per Task Recall vs Period')
    ax11.scatter(h, hr, c='r', s=dotSize)
    ax11.scatter(m, mr, c='g', s=dotSize)
    ax11.scatter(l, lr, c='b', s=dotSize)

    ax12.set_title('Per Task F1 vs Period')
    ax12.scatter(h, hf, c='r', s=dotSize)
    ax12.scatter(m, mf, c='g', s=dotSize)
    ax12.scatter(l, lf, c='b', s=dotSize)


    h, m, l = ext.extractExecution(metas)
    ax20.set_title('Per Task Precision vs Execution')
    ax20.scatter(h, hp, c='r', s=dotSize)
    ax20.scatter(m, mp, c='g', s=dotSize)
    ax20.scatter(l, lp, c='b', s=dotSize)

    ax21.set_title('Per Task Recall vs Execution')
    ax21.scatter(h, hr, c='r', s=dotSize)
    ax21.scatter(m, mr, c='g', s=dotSize)
    ax21.scatter(l, lr, c='b', s=dotSize)

    ax22.set_title('Per Task F1 vs Execution')
    ax22.scatter(h, hf, c='r', s=dotSize)
    ax22.scatter(m, mf, c='g', s=dotSize)
    ax22.scatter(l, lf, c='b', s=dotSize)

    plt.show()

if __name__ == "__main__":

    dotSize = 4

    # there are 3 primary group (high util, normal util, low util)
    # with in the group, there are three parts (h heavy, m heavy, l heavy)

    # first per utilization vs accuracy(collectively implying recall and precision)
    # second execution vs acc
    # third period vs acc

    utilNames = ["./medMetas_heavy"]
    resultNames = ["./medResults_heavy"]
    metas = []
    matrices = []

    # parse each metas in the folder name
    for name in utilNames:

        metaGroup = []

        metaFiles = glob.glob(name + "/*_meta.txt")
        for met in metaFiles:
            me = ext.metaParser(met)
            metaGroup.append(me)
        heavyH = ext.pickHeavyH(metaGroup)
        heavyM = ext.pickHeavyM(metaGroup)
        heavyL = ext.pickHeavyL(metaGroup)

        metas.append([heavyH, heavyM, heavyL])

    # create a dictionary of matrices
    for name in resultNames:
        group = {0:{}, 99:{}}
        matrixFiles = glob.glob(name + "/*.npy")
        for mf in matrixFiles:
            conf = ext.extractMatrixConf(mf)
            mId = ext.extractMatrixId(mf)
            group[conf][mId]=np.load(mf)
        matrices.append(group)

    heavyH = metas[0][0]
    heavyM = metas[0][1]
    heavyL = metas[0][2]

    heavyHMat0, heavyHMat99 = ext.getCorrespondingMatrix(matrices[0], heavyH)
    heavyMMat0, heavyMMat99 = ext.getCorrespondingMatrix(matrices[0], heavyM)
    heavyLMat0, heavyLMat99 = ext.getCorrespondingMatrix(matrices[0], heavyL)

    heavyHAccs = ext.extractOverallAcc(heavyHMat0)
    heavyMAccs = ext.extractOverallAcc(heavyMMat0)
    heavyLAccs = ext.extractOverallAcc(heavyLMat0)

    print("heavyH Average Acc: " + str(sum(heavyHAccs)/len(heavyHAccs)) )
    print("heavyM Average Acc: " + str(sum(heavyMAccs)/len(heavyMAccs)) )
    print("heavyL Average Acc: " + str(sum(heavyLAccs)/len(heavyLAccs)) )

    plot(heavyHMat0, heavyH, "Heavy High Priority Task Med Utilization")
    plot(heavyMMat0, heavyM, "Heavy Medium Priority Task Med Utilization")
    plot(heavyLMat0, heavyL, "Heavy Medium Priority Task Med Utilization")
