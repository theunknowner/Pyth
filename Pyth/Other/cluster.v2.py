#!/usr/bin/python
import numpy as np
import scipy as sp
import pandas as pd
from scipy.cluster.vq import kmeans, vq
from scipy import stats
import sys, getopt, pdb
#import argparse

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ht:i:c:")
    except getopt.GetoptError:
        print 'usage: ./kmeans2.py -t threshold -i inputfile -c concavity-parameter'
        sys.exit(2)
    ##fl = "../data/data.csv"
    thrs = 0.5
    theta = 0.01 # concavity-parameter
    for opt, arg in opts:
        if opt == '-h':
            print 'usage: ./clustering.py -t threshold -i inputfile -c concavity-parameter'
            sys.exit()
        elif opt == "-t":
            thrs = float(arg)
        elif opt == "-i":
            fl = arg
        elif opt == "-c":
            theta = float(arg)
    df = pd.read_csv(fl)
    #df.columns = ["time", "ad", "ht", "called-number", "calling-number", 
    #              "begin", "end", "descriptor"] + range(len(df.columns)-8)
    #df.columns = ["cn2", "interval", "ht"] + range(len(df.columns)-3)
    df.columns = ["ht"] + range(len(df.columns)-1)
    ## cn2 is called-number with last two digits removed
    #df["cn2"] = map(lambda i: str(i)[:-2], df["called-number"])
    #df["interval"] = map(lambda t0, t1: str(t0) + "-" + str(t1), df.begin, df.end) #time interval for which AD clustering is found
    fraud_dict = {} # key: first row in a fraud block of rows, value: tuple of (corresponding clusters, ht)
    #fl2 = open("./" + "fraud-"+fl.split("/")[-1], "w")
    rnd = lambda x: round(x, 3)
    for rows in get_rows(df):
        ht = np.array(df.ix[rows].ht)
        ht_ct = ht**theta # concave transformation of ht so distance(1000, 1100) < distance(100, 200)
        #clsts = opt_clustering(ht_ct, theta)
        #clsts = opt_clustering(ht, theta)
        clsts = clusters(ht)
        # for k in range(2,6):
        #     clsts = clusters(ht_ct, k)
        #     dnstyMax = clsts[0][0]
        #     if dnstyMax > thrs:
        #         break
        dnstyMax = clsts[0][0]
        if dnstyMax > thrs:
            fraud_dict[rows[0]] = (clsts, ht)
    print clsts
    np.savetxt("clusters.csv", clsts, "%f", ",")
    #write_output(df, fraud_dict, fl2, theta)
    #fl2.close()
    return None

def write_output(df, fraud_dict, fl, theta):
    theta = 1 ## ?? change it later
    rnd = lambda x: round(x, 3)
    for key in sorted(fraud_dict, 
                      key=lambda k: (df.ix[k]["descriptor"], df.ix[k]["begin"])):
        clsts, ht = fraud_dict[key]
        fl.write("time-interval: {} Descriptor: {} points: {}\n numbers: {}\n".format(df.ix[key]["interval"], 
                                                                                      df.ix[key]["descriptor"], 
                                                                                      len(ht),
                                                                                      (df.ix[key]["called-number"], df.ix[key]["calling-number"])))
        map(lambda tpl: fl.write("centroid: {} density: {} npoints: {} \n".format(rnd(tpl[1]**(1/theta)),
                                                                rnd(tpl[0]), tpl[2])), clsts)
        fl.write("\nht: {}".format(ht))
        fl.write("\n"*2)   
    return None

def get_rows(df):
    """
    returns [r1,..,rn], each ri corresponds to rows in df
    such that they belong to the same called number in an interval
    for which AD consistency is found.
    """
    nrow = df.shape[0]
    rows = []
    #for interval in set(df["interval"]):
    #    for num in set(df[df["interval"]==interval].cn2):
    #        rows.append(list(np.arange(nrow)[(df["interval"] == interval) & (df.cn2 == num)]))
    rows.append(list(np.arange(nrow)))
    return rows

def clusters(data, theta=0.1):
    clsts = sorted(opt_clustering(data, len(data), theta), 
                   key=lambda xs: xs[1]) ## opt clusters sorted according to centroids
    ans = [] ## ans will contain clsts some of which will be merged
    n = len(data)
    current = clsts[0]
    for i in range(1,len(clsts)):
        if mergep(current[1], clsts[i][1]):
            current = merge_clusters([current, clsts[i]], n)
        else:
            ans.append(current)
            current = clsts[i]
    ans.append(current)
    return sorted(ans, key=lambda xs: xs[0], reverse=True)

def opt_clustering(data, length, theta, recursion_depth=0):
    centroid = lambda data: sum(data) / float(len(data))
    if len(data) < 30 or \
       is_cv_small(data, min_cv = 0.1) or \
       is_normal(data, alpha = 0.05) or \
       recursion_depth > 5:
        return [(density(data, length, theta), centroid(data), min(data), max(data), len(data))]
    try:
        cl, cr = kmeans(np.array(data), 2)[0] ## cl: left-centroid and cr: right-centroid
    except ValueError: ## kmeans find only one cluster
        return [(density(data, length, theta), centroid(data), min(data), max(data), len(data))]
    dl = [d for d in data if abs(d - cl) < abs(d - cr)] ##dl: left-data
    dr = [d for d in data if d not in dl] ##dr: right-data
    # mus, sigs = gaussian_mixture(data)
    # dl = [d for d in data if dist(d, (mus[0], sigs[0])) < dist(d, (mus[1], sigs[1]))]
    # dr = [d for d in data if d not in dl]
    return opt_clustering(dl, length, theta, recursion_depth+1) + \
        opt_clustering(dr, length, theta, recursion_depth+1)

def mergep(c0, c1, prcnt_diff=0.30):
    "check if clusters with centroid c0, c1 (c0 < c1)should be merged"
    if c0 < 600:
        return False
    return c1/float(c0) - 1 < prcnt_diff

def merge_clusters(clsts, n):
    """
    Input:
         cltsts: [(density1, centroid1, n1), (density2, centroid2, n2),..]
         n: total points 
    algorithm: suppose there are k clusters to be merged (d1,c1,n1),..,(dk,ck,nk)
    by defination, di = sqrt(ni/n) / width_i => width_i = sqrt(ni/n) / di
    for the merged cluster, numerator is sqrt(n1+..+nk)/n and
    width is weighted sum of widhts, where weight of width_i is 
    ni/n.
    """
    ds = extract(0, clsts) ## densities
    cntrs = extract(1, clsts) ## centroids
    ns = extract(2, clsts) ## number of points in each cluster
    props = map(lambda ni: (ni/float(n))**0.5, ns) ## numerators of density for each cluster
    widths = map(lambda n_i, ro_i: 
                 ((n_i/float(n))**0.5)/float(ro_i), ns, ds) ## den of density for each cluster
    num = (sum(ns)/float(n))**0.5 ## numerator for merged cluster density
    den = sum(map(lambda n_i, width_i: 
                  n_i * width_i, ns, widths))/(float(sum(ns))) ## den for merged cluster density
    dnsty = num/den
    cntr = sum(map(lambda ci, ni: ci*ni, cntrs, ns)) / sum(ns)
    return (dnsty, cntr, sum(ns))

def extract(i, lsts):
    return map(lambda lst: lst[i] if lst[i] else 0.0001, lsts)


def gaussian_mixture(X):
    X = np.array(X)
    X.sort()
    n = len(X)
    Y = np.array([0] * (n/2) + [1] * (n - (n/2)))
    #pdb.set_trace()
    def assign_mu_sig():
        mu = map(lambda i: X[Y==i].mean(), [0, 1])
        sig = map(lambda i: np.sqrt(X[Y==i].var()), [0, 1])
        return mu, sig
    mu, sig = assign_mu_sig()
    for i in range(10):
        for j in range(n):
            if dist(X[j], (mu[0], sig[0])) < dist(X[j], (mu[1], sig[1])):
                Y[j] = 0
            else:
                Y[j] = 1
        mu, sig = assign_mu_sig()
    return mu, sig

def dist(x, (mu, sig)):
    return 2 * sp.stats.norm.cdf(abs(x - mu) / sig) - 1

def density(data, length, theta):
    """
    data correspond to one particula cluster, 
    length is a number of points in all the clusters.
    density = (proportion)**alpha / width, with alpha = 0.5

    sqrt of proportion is taken to decrease its influence
    on density (lower the value of alpha, lower its influence).
    To see why it is required consider the example 
    data = [500]*50 + [1500]*50, there are
    two dense clusters around 500 and 1500 but the density
    of any of these clustes is bounded by (1/2)**alpha, so
    if alpha = 1 then we won't be able to detect any of these.
    (note: taking alpha = 0 or very low gives many false-positive)

    Outliers are removed to calculate the width of the cluster,
    but if there is only one cluster (determided by len(data) == length)
    then outliers are not removed, this is a sort of a patch work
    but it removes false positives when there are apparently no
    dense clustering but normality test is not rejected.
    """
    nelts = len(data)
    if nelts < 5: return 0 ## patch
    data = sorted(data)
    low = data[int(0.1 * nelts)] #10th percentile
    high = data[int(0.9 * nelts)] #90th percentile
    if length == nelts: #don't remove outliers (patch)
        low, high = data[0], data[-1]
    proportion = nelts / float(length)
    width = 1 + high**theta - low**theta
    return proportion**0.5 / width

def is_normal(data, alpha=0.05):
    "apply the Jarque-Bera test to test for normality at \
    the significance level alpha to the data"
    #pdb.set_trace()
    n = len(data)
    data = np.array(data) 
    mean = data.mean()
    sd = np.sqrt(data.var())
    data_normalized = (data - mean) / sd
    S = (data_normalized**3).mean()
    K = (data_normalized**4).mean()
    JB = (n/6.0) * (S**2 + (1/4.0) * (K - 3)**2)
    p_value = 1 - stats.distributions.chi2.cdf(JB, 2)
    return p_value > alpha

def is_cv_small(data, min_cv=0.1):
    """
    cv is coffecient of variance if it is small then 
    even if there are more then one clusters, according
    to our interpretations their is only one and clustering
    algo should be terminated. For example if data = [500]*50 + [501]*50
    then their are two clusters at 500 and 501 but in our interpretation
    only one at 500.5
    """
    data = np.array(data) 
    return np.sqrt(data.var()) / data.mean() < min_cv

if __name__ == "__main__":
    rslt = main(sys.argv[1:])


