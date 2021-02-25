import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

#current steps I'm going to do
#
#clean out non ms stars(binaries, wd, etc.)
### use stats to determine probability of each star is binary or not
#
# determine interval that causes the error within hubble
### use MS isochroners to determine where MS should be and compare from there

# if there's still time
# compare ages of stars, luminosity between different types of stars
# maybe use the other data set? (hugs)
# see if F425 has any cool stuff
# look at other categories

#So we did this, but the order of the values in the list are different now
#maybe see if theres a way to use numpy/pandas methods to do this
#all of the zeroes are at the end
#If we cannot get the np/pd array to work, then make sure to remove the values that are too high by their actual numbers


data_275, data_336, id_s, data_606, data_814, dx, dy = np.loadtxt('/Users/distantbeliefs/Cool/LESLIE/47tuc/hlsp_gcuvleg_hst_wfc3-uvis_ngc0104_v1_catalogue.txt', usecols = [2,3,17,20,21,24,25], unpack = True)
id_b = np.loadtxt('data/hlsp_hugs_hst_wfc3-uvis-acs-wfc_ngc0104_multi_v1_catalog-meth1.txt', dtype = str, usecols = 35)
datab_606, datab_814, mem_prob = np.loadtxt('data/hlsp_hugs_hst_wfc3-uvis-acs-wfc_ngc0104_multi_v1_catalog-meth1.txt', usecols = [20,26,32], unpack = True)

def remove_R(lst = id_b):
    new_lst = []
    for i in lst:
        new_lst.append(int(i[-6:]))
    return new_lst

df_small = pd.DataFrame({'ID':id_s, 'data_275':data_275, 'data_336': data_336, 'data_606':data_606, 'data_814':data_814, 'dx':dx, 'dy':dy})
df_big = pd.DataFrame({'ID': remove_R(id_b), 'Membership_probability':mem_prob})

df = pd.merge(left=df_small, right=df_big, how='left', left_on='ID', right_on='ID')
df = df[(df[['data_606','data_814']] <= 40).all(axis=1)]
df = df[(df[['data_275','data_336']] >= 12.5).all(axis=1)]


f275 = 13.35 +0.239
f336 = 13.35 + 0.203
f606 = 13.35 + .115
f814 = 13.35 + 0.075

#fehm10afep2
fehm10afep2_WFC3_points =  np.loadtxt(fname = "/Users/distantbeliefs/Cool/LESLIE/47tuc/Isochrones/fehm10afep4.HST_WFC3")
fehm10afep2_ACSWF_points = np.loadtxt(fname = "/Users/distantbeliefs/Cool/LESLIE/47tuc/Isochrones/fehm10afep4.HST_ACSWF")
iso_275 = fehm10afep2_WFC3_points[:,8] + f275
iso_336 = fehm10afep2_WFC3_points[:,11] + f336
iso_814 = fehm10afep2_ACSWF_points[:,15] +f814
iso_606 = fehm10afep2_ACSWF_points[:,10] +f606 



def hist_prob(x = mem_prob):
    short = [i for i in x if i > 0]
    plt.hist(short, bins = 100)
    plt.axvline(50, color='k', linestyle='dashed', linewidth=1)
    plt.title('Probability of Stars being in 47 Tuc')
    plt.xlabel('Probability of Star Being a Member', fontsize=20)
    plt.ylabel('Number of Stars', fontsize=20)
    plt.yscale('log')
    plt.show()

def sep_members(df):
    df2 = pd.DataFrame()
    
    rows = df.loc[df['Membership_probability'] > 50, :]
    df2 = df2.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)
    return df, df2

df1, df2 = sep_members(df)

def ms_difference(lst1 = iso_606, lst2 = iso_814, data1 = df1['data_606'], data2 = df1['data_814']): 
    iso_lst = np.asarray(lst1-lst2)
    data_lst = data1-data2
    
    lst = []
    for data in data_lst:
        idx = (np.abs(iso_lst - data)).argmin()
        lst.append(np.linalg.norm(iso_lst[idx] - data))
        df1['delta'] = np.linalg.norm(iso_lst[idx] - data)

    return np.asarray(lst)


df1['ms_delta_opt'] = ms_difference()
df1['ms_delta_UV'] = ms_difference(lst1 = iso_275, lst2 = iso_336, data1 = df1['data_275'], data2 = df1['data_336'])
df1['opt-UV'] = df1['ms_delta_opt']- df1['ms_delta_UV']


def sep_prob(df = df1):

    df_b = df.loc[~((df['opt-UV'] > -0.2817938716083204) & (df['opt-UV']< 0.24665511360750217))].reset_index(drop=True)
    df_g = df.loc[~((df['opt-UV'] < -0.2817938716083204) & (df['opt-UV']> 0.24665511360750217))].reset_index(drop=True)
    return df_g, df_b


df3, df4 = sep_prob()
def final_df(df_g = df3, df_b = df4):
    cond = df_g['opt-UV'].isin(df_b['opt-UV'])
    df_g.drop(df_g[cond].index, inplace = True)
    return df_g

def binary_hist(opt = df1['ms_delta_opt'], uv = df1['ms_delta_UV']):
    plt.hist((opt-uv), bins = 100)
    #99 confidence
    plt.axvline(-0.2817938716083204, color='k', linestyle='dashed', linewidth=1, label = 'Confidence interval = 0.99')
    plt.axvline(0.24665511360750217, color='k', linestyle='dashed', linewidth=1)
    plt.xlabel('Difference Between Optical and UV filters')
    plt.ylabel('Number of Stars')
    plt.yscale('log')
    plt.legend()
    plt.show()

def conf_int(op = df1['ms_delta_opt'], uv = df1['ms_delta_UV'], conf = 0.99):
    # (-0.21861938205432635, 0.18348062405350807) @95
    # (-0.2817938716083204, 0.24665511360750217) @99
    delta = op-uv
    mean, sigma = np.mean(delta), np.std(delta)
    inte = stats.norm.interval(conf, loc=mean, scale=sigma)
    return inte

def cmd275(filter1 = df1['data_275'], filter2 = df1['data_336'], filter1_b = df2['data_275'], filter2_b = df2['data_336'], iso1 = iso_275, iso2 = iso_336):
    
    plt.clf()
    
    plt.scatter(filter1-filter2, filter1, color= 'c', marker = '.', alpha = 0.5, label = 'MS stars')
    plt.plot(iso1-iso2, iso1, color = 'r', label = 'Main Sequence Model')
    #plt.scatter(filter1_b-filter2_b, filter1_b, color = 'k', marker = '.', alpha = 1, label = 'Non-singular stars')
    plt.axis([-1, 4, 15.5, 25.75])
    plt.gca().invert_yaxis()
    plt.title('Color-Magnitude Diagram in UV Filters')
    plt.xlabel('m${_{275}}$\N{MINUS SIGN}m${_{336}}$' , fontsize=20)
    plt.ylabel('m${_{275}}$', fontsize=20)
    plt.legend()
    plt.show()

def cmd814(filter1 = df1['data_606'], filter2 = df1['data_814'], filter1_b = df2['data_606'], filter2_b = df2['data_814'], iso1 = iso_606, iso2 = iso_814):
    
    plt.clf()
    plt.scatter(filter1-filter2, filter2, color= 'b', marker = '.', alpha = 0.5, label = 'MS stars')
    #plt.scatter(filter1_b-filter2_b, filter2_b, color = 'k', marker = '.', alpha = 1, label = 'Non-singular stars')
    
    plt.plot(iso1-iso2, iso2, color = 'r', label = 'Main Sequence model')
    plt.axis([-4, 4, 8.25, 27.5])
    plt.title('Color-Magnitude Diagram in Optical Filters')
    plt.xlabel('m${_{606}}$\N{MINUS SIGN}m${_{814}}$' , fontsize=20)
    plt.ylabel('m${_{814}}$', fontsize=20)
    plt.gca().invert_yaxis()
    plt.legend()
    plt.show()







ult_df = final_df()
ms = ms_difference(data1 = ult_df['data_606'], data2 = ult_df['data_814'])


plt.clf()
#cmd275(filter1 = ult_df['data_275'], filter2 = ult_df['data_336'])
#cmd814(filter1 = ult_df['data_606'], filter2 = ult_df['data_814'])
#binary_hist()
plt.hist(ms, bins = 100)
plt.yscale('log')
plt.xlabel('Distance From Isochrone')
plt.ylabel('Amount of Stars')
plt.show()
print(stats.ttest_1samp(ms, 0 ))
#print(df3)