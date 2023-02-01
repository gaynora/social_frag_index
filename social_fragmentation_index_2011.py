# -*- coding: utf-8 -*-
"""
Building a small area Social Fragmentaion Index 2011 for the UK, using Census data. 
Derived from;
Congdon, Peter (2013) Assessing the Impact of Socioeconomic Variables on Small Area Variations in Suicide Outcomes in England. Int J Environ Res Public Health. 10(1): 158–177. 
Python3 script
@author: G
"""

import numpy
import pandas
import geopandas

# Raw data Census 2011 data source: https://www.nomisweb.co.uk/query/select/getdatasetbytheme.asp?theme=75 
# the below tables have been extracted from the Nomis server with only the relevant fields for this analysis
# index columns 0 & 1 include the geography codes and 3 the denominator
not_couple = pandas.read_csv('oa_uk_qs108uk_living_arrangements_2011.csv', usecols=[0,1,2,3], header = 5, skiprows = [6], skipfooter = 7, index_col='mnemonic') # to calculate % residents not living as a couple, using field: 'Not living in a couple: Total'
new_add = pandas.read_csv('oa_uk_ukmig008_migration_2011.csv', usecols=[0,1,2,3], header = 5, skiprows = [6], skipfooter = 7, index_col='mnemonic') # to calculate % residents moved to their current address within the last year, using field: 'Lived at same address one year ago'
one_pers = pandas.read_csv('oa_uk_qs112uk_household_composition_people_2011.csv', usecols=[0,1,2,3], header = 5, skiprows = [6], skipfooter = 7, index_col='mnemonic') # to calculate % residents 1-person household, using field: 'One person household: Total'
priv_rent = pandas.read_csv('oa_uk_qs403uk_tenure_people_2011.csv', usecols=[0,1,2,3], header = 5, skiprows = [6], skipfooter = 7, index_col='mnemonic') # to calculate % residents renting privately, using field: 'Private rented: Total'

# derived percentage columns
not_couple['znotcouple'] = not_couple['Not living in a couple: Total'] / not_couple['All categories: Living arrangements'] * 100
new_add['znewadd'] = new_add['Lived at same address one year ago'] / new_add['All usual residents'] * 100
one_pers['zonepers'] = one_pers['One person household: Total']  / one_pers['All categories: Household composition'] * 100
priv_rent['zprivrent'] = priv_rent['Private rented: Total'] / priv_rent['All categories: Tenure'] * 100

# zscore calculations
def zscore (x):
    mean = x.mean() # calculate the mean of all values in the column
    stdev = x.std() # calculate the standard deviation of values in the column
    y = (x-mean)/stdev # calculate the zscores
    return y

not_couple['zsntcouple'] = zscore (not_couple['znotcouple']) 
new_add['zsnewadd'] = zscore (new_add['znewadd'])
one_pers['zsonepers'] = zscore (one_pers['zonepers'])
priv_rent['zsprivrent'] = zscore (priv_rent['zprivrent'])

#join the seperate dataframes into a single dataframe with percentages and z scores
join_df = pandas.merge(not_couple[['2011 output area','znotcouple','zsntcouple']], new_add[['znewadd','zsnewadd']], how='inner', on = 'mnemonic')
join_df2 = pandas.merge(join_df, one_pers[['zonepers','zsonepers']], how='inner', on = 'mnemonic')
join_df3 = pandas.merge(join_df2, priv_rent[['zprivrent','zsprivrent']], how='inner', on = 'mnemonic')

# add zscores and recalculate final z score
join_df3['addzscores'] = join_df3['zsntcouple'] + join_df3['zsnewadd'] + join_df3['zsonepers'] + join_df3['zsprivrent']
join_df3['SFI_score'] = zscore (join_df3['addzscores'])

# join index zscores to output area boundaries and export - rename index field to be the same in order to join using geopandas
oas = geopandas.read_file('infuse_oa_lyr_2011.shp') # data source: https://borders.ukdataservice.ac.uk/bds.html 'Infuse Output Areas and Small Areas 2011'
join_df3.rename(columns = {'2011 output area':'geo_code'}, inplace = True)
spatial_join = oas.merge(join_df3, on='geo_code')
spatial_join.to_file('oa_uk_social_fragmentation_index_household_2011.gpkg', driver='GPKG')

