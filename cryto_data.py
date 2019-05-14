import pandas as pd
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from server.comparisoncom import ComparisonCom


def cal_density_real_data(_data, _bins='auto'):
    _frequency, _bins = np.histogram(_data, bins=_bins, density=True)
    return [_frequency, _bins]


start_date = pd.Timestamp(2014, 8, 1, 12)
end_date = pd.Timestamp(2018, 8, 1, 12)

baseline = 'USD'
data_limit = 9999

# symbol = ['BTC', 'ETC', 'XRP', 'BCH', 'EOS', 'LTC', 'ADA', 'XLM', 'IOT', 'NEO']

symbol = ['BTC']

pool = ComparisonCom()

data = pool.coin_list()

full_name = {}
for s in symbol:
    coin = data[s]
    full_name.update({s: coin['FullName']})
    
with open('savedata/coin_info.txt', 'w+') as f:
    for coin in full_name:
        f.writelines(coin+"\t"+full_name[coin]+'\n')

for s in full_name:
    file_name = s
    time_delta = 12
    # df = pool.minute_price_historical(file_name, 'USD', 9999, time_delta)
    # df = pool.hourly_price_historical(file_name, 'USD', 9999, time_delta)
    df = pool.daily_price_historical(file_name, 'USD', data_limit, time_delta)
    relative_change = df.close.pct_change()
    date = df.timestamp
    
    with open('savedata/coin/'+file_name+'.txt', 'w+') as f:
        for i in range(1, len(relative_change)):
            f.writelines(str(i-1)+"\t"+str(relative_change[i])+'\n')
    b = relative_change[1:]        
    with open('savedata/coin/'+file_name+'_stat.txt', 'w+') as f:
        f.writelines("number of samples: "+str(len(relative_change)-1)+'\n')
        f.writelines("time begin: "+str(df.timestamp[0])+'\n')
        f.writelines("time end: "+str(df.timestamp[len(df.timestamp)-1])+'\n')
        
        f.writelines('\n')
        f.writelines("++++++++++ empirical stat ++++++++++"+'\n')
        f.writelines("mean: "+str(b.mean())+'\n')
        f.writelines("var: "+str(b.var())+'\n')
        f.writelines("skewness: "+str(b.skew())+'\n')
        f.writelines("kurtosis: "+str(b.kurt())+'\n')
        f.writelines("=========== end stat ==========="+'\n')
        
        [dof,loc,sca]=stats.t.fit(b)
        f.writelines('\n')
        f.writelines("++++++++++ student t fit stat ++++++++++"+'\n')
        f.writelines("degree of freedom: "+str(dof)+'\n')
        f.writelines("loc parameter: "+str(loc)+'\n')
        f.writelines("scale parameter: "+str(sca)+'\n')
        f.writelines("========== end fit stat =========="+'\n')
        
#        bb = pd.concat([b]*2000)
#        [dof,loc,sca]=stats.t.fit(bb)
#        f.writelines("++++++++++ repeat student t fit stat ++++++++++"+'\n')
#        f.writelines("degree of freedom: "+str(dof)+'\n')
#        f.writelines("loc parameter: "+str(loc)+'\n')
#        f.writelines("scale parameter: "+str(sca)+'\n')
#        f.writelines("========== end fit stat =========="+'\n')
        
        [stat,p] = stats.shapiro(b)
        f.writelines('\n')
        f.writelines("++++++++++ normality of Shapiro-Wilk (SW) test ++++++++++"+'\n')
        f.writelines("statistic: "+str(stat)+'\n')
        f.writelines("p-value: "+str(p)+'\n')
        f.writelines("========== end SW test =========="+'\n')
                
        [stat,p] = stats.kstest(b, 'norm',stats.norm.fit(b))
        f.writelines('\n')
        f.writelines("++++++++++ normality of Kolmogrov-Smirnov (KS) test ++++++++++"+'\n')
        f.writelines("statistic: "+str(stat)+'\n')
        f.writelines("p-value: "+str(p)+'\n')
        f.writelines("========== end KS test =========="+'\n')

#        [stat,p] = stats.kstest(bb, 't',stats.t.fit(bb))
#        f.writelines("++++++++++ repeat student t of Kolmogrov-Smirnov (KS) test ++++++++++"+'\n')
#        f.writelines("statistic: "+str(stat)+'\n')
#        f.writelines("p-value: "+str(p)+'\n')
#        f.writelines("========== end KS test =========="+'\n')
        
        [stat,p] = stats.kstest(b, 't',stats.t.fit(b))
        f.writelines('\n')
        f.writelines("++++++++++ student t of Kolmogrov-Smirnov (KS) test ++++++++++"+'\n')
        f.writelines("statistic: "+str(stat)+'\n')
        f.writelines("p-value: "+str(p)+'\n')
        f.writelines("========== end KS test =========="+'\n')
        
        [stat,p] = stats.kstest(b+1, 'lognorm', stats.lognorm.fit(b+1))
        f.writelines('\n')
        f.writelines("++++++++++ lognorm of Kolmogrov-Smirnov (KS) test ++++++++++"+'\n')
        f.writelines("statistic: "+str(stat)+'\n')
        f.writelines("p-value: "+str(p)+'\n')
        f.writelines("========== end KS test =========="+'\n')

ret = []
for d in range(len(date)):
    if start_date.value <= date[d].value <= end_date.value:
        result = relative_change[d]
        if not np.isnan([result]).any():
            ret.append(result)

mu = np.mean(ret)
sigma = np.sqrt(np.var(ret))
data_normalized = (ret-mu)/sigma
[frequency, bins] = cal_density_real_data(data_normalized)
x = np.linspace(min(bins), max(bins), len(bins[1:]))

matplotlib.rcParams.update({'font.size': 14})
nasdaq, = plt.plot(bins[1:], frequency, 'b-', label='Bitcoin daily returns')
gau, = plt.plot(x, stats.norm.pdf(x), 'g--', label='Gaussian samples')
plt.legend(handles=[nasdaq, gau], loc='best', fontsize='small')
plt.savefig('1.png', bbox_inches='tight', dpi=300)
plt.show()
