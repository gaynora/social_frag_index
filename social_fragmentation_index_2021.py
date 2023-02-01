# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 20:24:51 2023
Building a small area Social Fragmentaion Index 2021 for England and Wales, using Census data. 
Derived from;
Congdon, Peter (2013) Assessing the Impact of Socioeconomic Variables on Small Area Variations in Suicide Outcomes in England. Int J Environ Res Public Health. 10(1): 158–177. 
Python3 script
@author: G
"""

import numpy
import pandas
import geopandas

# Raw data Census 2021 data source: https://www.nomisweb.co.uk/sources/census_2021_bulk
not_couple = pandas.read_csv('census2021-ts003-oa.csv', header = 0, index_col='geography', usecols=[1,2,3,9,13]) # to calculate % residents not living as a couple
new_add = pandas.read_csv('census2021-ts019-oa.csv', header = 0, index_col='geography', usecols=[1,2,3,4]) # to calculate % residents moved to their current address within the last year
one_pers = pandas.read_csv('census2021-ts017-oa.csv', header = 0, index_col='geography', usecols=[1,2,3,5]) # to calculate % residents 1-person household
priv_rent = pandas.read_csv('census2021-ts054-oa.csv', header = 0, index_col='geography', usecols=[1,2,3,12]) # to calculate % residents renting privately

# derived percentage columns
not_couple['znotcouple'] = (not_couple['Household composition: Total; measures: Value']-(not_couple['Household composition: Single family household: Married or civil partnership couple; measures: Value'] + not_couple['Household composition: Single family household: Cohabiting couple family; measures: Value'])) / not_couple['Household composition: Total; measures: Value'] * 100
new_add['znewadd'] = (new_add['Migrant indicator: Total: All usual residents; measures: Value'] - new_add['Migrant indicator: Address one year ago is the same as the address of enumeration; measures: Value']) / new_add['Migrant indicator: Total: All usual residents; measures: Value'] * 100
one_pers['zonepers'] = (one_pers['Household size: Total: All household spaces; measures: Value'] - one_pers['Household size: 1 person in household; measures: Value']) / one_pers['Household size: Total: All household spaces; measures: Value'] * 100
priv_rent['zprivrent'] = (priv_rent['Tenure of household: Total: All households'] - priv_rent['Tenure of household: Private rented']) / priv_rent['Tenure of household: Total: All households'] * 100

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
join_df = pandas.merge(not_couple[['geography code','znotcouple','zsntcouple']], new_add[['znewadd','zsnewadd']], how='inner', on = 'geography')
join_df2 = pandas.merge(join_df, one_pers[['zonepers','zsonepers']], how='inner', on = 'geography')
join_df3 = pandas.merge(join_df2, priv_rent[['zprivrent','zsprivrent']], how='inner', on = 'geography')
print(join_df3)

# add zscores and recalculate final z score
join_df3['addzscores'] = join_df3['zsntcouple'] + join_df3['zsnewadd'] + join_df3['zsonepers'] + join_df3['zsprivrent']
join_df3['SFI_score'] = zscore (join_df3['addzscores'])

# join index zscores to output area boundaries and export - rename index field to be the same in order to join using geopandas
oas = geopandas.read_file('Output_Areas_(Dec_2021)_Boundaries_Generalised_Clipped_EW_(BGC).geojson')
join_df3.rename(columns = {'geography code':'OA21CD'}, inplace = True)
spatial_join = oas.merge(join_df3, on='OA21CD')
spatial_join.to_file('oa_ew_social_fragmentation_index_household_2021.gpkg', driver='GPKG')

