
# coding: utf-8

# In[1]:


from IPython.display import HTML


# In[2]:


# HTML('''<script>
# code_show=true; 
# function code_toggle() {
#  if (code_show){
#  $('div.input').hide();
#  } else {
#  $('div.input').show();
#  }
#  code_show = !code_show
# } 
# $( document ).ready(code_toggle);

# </script>
# The raw code for this IPython notebook is by default hidden for easier reading.
# To toggle on/off the raw code, click <a href="javascript:code_toggle()">here</a>.''')


# In[3]:


# I don't execute everything unless I am viewing in a notebook
IN_JUPYTER = 'get_ipython' in globals() and get_ipython().__class__.__name__ == "ZMQInteractiveShell"


# # Data Storytelling Project: SAT New York

# **Objectives:**
# * Analyse SAT scores + demographics and any other relevant information available
# * Check fairness of the [SAT](https://www.insidehighered.com/news/2010/06/21/sat)
# 
# **Summary:**
# * SAT correlation:
#     * 'SAT Math Avg. Score' and 'SAT Writing Avg. Score' strongly correlates with 'SAT_score'
#     * 'ell_percent' (% of students in each school who are learning English) correlates negatively with 'SAT_score'
#     * 'total_enrollment' correlates positively with 'SAT_score'
#     * It's possibile to identify some racial inequality in the data, with 'hispanic_per' and 'black_per' correlating negatively with 'SAT_score'
#     * 'female_per' correlates positively with 'SAT_score'
#     * 'male_per' correlates negatively with 'SAT_score'
# 

# In[4]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import folium
from folium.plugins import MarkerCluster, HeatMap
import json

import bokeh
from bokeh.charts import HeatMap, bins, output_file, show

# Allow modules and files to be loaded with relative paths
import os
cwd = os.getcwd() # make sure the work directory is correct
cwd
import glob
path = "../data/*.csv"

get_ipython().magic(u'matplotlib inline')
plt.rcParams['figure.figsize'] = (10.0, 8.0)


# ## Understanding the data

# ### Read data into dataframe, put each dataframe into a dictionary

# In[5]:


def load_files(path):
    """
    Takes csv files, convert them to data dictionary.
    Args:
        Data path
    Returns:
        data dictionary.
    """
    data = {}
    for file_ in glob.glob(path):
        file_name = os.path.splitext(os.path.basename(file_))[0]
        d = pd.read_csv("{}".format(file_))
        data[file_.replace(file_, file_name)] = d
    return data


# ### Check dictionary

# In[6]:


if IN_JUPYTER:
    data = load_files(path)
    for k,v in data.items():
        print("\n" + k + "\n")
        print(v.head())


# **Patterns/preliminary analysis:**

# * District Borough Number (DBN): Math_test_results, SAT_results, Demographics, AP_results, Graduation_outcomes, hsdirectory
# * School name: SAT_results, AP_results, Graduation_outcomes, Class_size, hsdirectory
# * Location1 field in hsdirectory can be used for maps

# ### Data unification  

# This makes working with all the data an easier process.
# DBN is a common column, it just doesnt appear in Class_size - unless School code is DBN.
# 
# I will check how DBN looks and compare against Class_size to try to recognize a pattern

# In[7]:


data["AP_results"]["DBN"].head()


# In[8]:


data["Class_size"].head()


# It looks like DBN is combination of CSD, BOROUGH, and SCHOOL CODE.

# from [string format](https://docs.python.org/2/library/stdtypes.html#str.format) [documentation](https://docs.python.org/3/library/string.html#format-string-syntax):
# 
# {:02d}
# 
# 02d formats an integer (d) to a field of minimum width 2 (2), with zero-padding on the left (leading 0)
# 

# In[9]:


data["Class_size"]["DBN"] = data["Class_size"].apply(lambda x: "{0:02d}{1}".format(x["CSD"], x["SCHOOL CODE"]), axis=1)
data["hsdirectory"].rename(columns={'dbn': 'DBN'}, inplace=True)


# In[10]:


data["Class_size"].head(3)


# I will now combine the survey data into one:

# In[11]:


def load_txt(path_to_file, filename):
    """
    Takes a txt, convert them to a dataframe.
    Args:
        Data path and file name
    Returns:
        data frame.
    """
    fp = os.path.join(path_to_file, filename)
    d = pd.read_csv(fp, delimiter = "\t")
    return d


# In[12]:


path_to_file = "../data/survey/"
s1 = "masterfile11_gened_final.txt"
s2 = "masterfile11_d75_final.txt"
survey1 = load_txt(path_to_file, s1)
survey2 = load_txt(path_to_file, s1)


# In[13]:


survey1.head(3)


# In[14]:


survey2.head(3)


# Add 'False' to the d75 field in survey one (which corresponds to all schools) and 'True' to survey2 (which corresponds to school district 75)

# In[15]:


survey1["d75"] = False
survey2["d75"] = True


# Concatenate survey1 and survey2 vertically

# In[16]:


survey = pd.concat([survey1, survey2], axis=0)


# In[17]:


survey.head()


# Check data dictionary file (Survey Data Dictionary.xls) to define which columns are relevant

# In[18]:


survey["DBN"] = survey["dbn"]
survey_fields = ["DBN", "rr_s", "rr_t", "rr_p", "N_s", "N_t", "N_p", "saf_p_11", "com_p_11", "eng_p_11", "aca_p_11", "saf_t_11", "com_t_11", "eng_t_10", "aca_t_11", "saf_s_11", "com_s_11", "eng_s_11", "aca_s_11", "saf_tot_11", "com_tot_11", "eng_tot_11", "aca_tot_11",]


# In[19]:


survey.head()


# In[20]:


# getting only the relevant fields
# note that '.loc' was used because it works on lables. If I was working on the positions in the index, I would use iloc
survey = survey.loc[:,survey_fields]


# In[21]:


survey.head()


# I need to add the survey to the data dictionary

# In[22]:


data["survey"] = survey
#survey.shape


# In[23]:


data['survey'].head()


# ### Checking the datasets

# In[24]:


if IN_JUPYTER:
    for k,v in data.items():
        print("\n" + k + "\n")
        print(v.head(3))


# Math_test_results, Demographics, Graduation_outcomes, Class_size have several rows for each high school (DBN and School name fields).
# 
# I will need to find a way to condensate the datasets above to "one row per high school". If that is not done, it won't be possible to compare the datasets.

# ** Class_size:**

# In[25]:


data["Class_size"].head()


# It looks like grade 9-12 corresponds to what I [want](https://www.justlanded.com/english/United-States/USA-Guide/Education/The-American-school-system).
# 
# From the dataset [description](https://data.cityofnewyork.us/Education/2010-2011-Class-Size-School-level-detail/urz7-pzb3), I've learnt that there are 3 program types:
# 
# "Average class sizes for each school, by grade and program type (General Education, Self-Contained Special Education, Collaborative Team Teaching (CTT)) for grades K-9 (where grade 9 is not reported by subject area), and for grades 5-9 (where available) and 9-12, aggregated by program type (General Education, CTT, and Self-Contained Special Education) and core course (e.g. English 9, Integrated Algebra, US History, etc.)."
# 
# I can focus on General Education for now.
# 
# To group the data, I will have to average the values. So I will group Class_size by DBN (so the data will be "one row per high school")  and average each column. I will get the average Class_size for each school
# 

# In[26]:


Class_size = data["Class_size"]
Class_size = Class_size[Class_size["GRADE "] == "09-12"]
Class_size = Class_size[Class_size["PROGRAM TYPE"] == "GEN ED"]
Class_size = Class_size.groupby("DBN").agg(np.mean)


# In[27]:


Class_size.head()


# DBN is now the index. It needs to be a "normal" column

# In[28]:


Class_size.reset_index(inplace=True)
data["Class_size"] = Class_size


# In[29]:


data["Class_size"].head()


# **Math_test_results:**

# DBN has been entered by Grade and by Year, as data was collected for multiple years for the same schools

# In[30]:


data["Math_test_results"]["Year"].max()


# The most recent year is 2011, which will be the one I will use then.

# In[31]:


data["Math_test_results"] = data["Math_test_results"][data["Math_test_results"]["Year"] == 2011]


# In[32]:


data["Math_test_results"].head()


# I will also need to select only one Grade, so I will pick the max one which is 8

# In[33]:


data["Math_test_results"]["Grade"].dtype


# This is an object type. From [stackoverflow](https://stackoverflow.com/questions/34881079/pandas-distinction-between-str-and-object-types):
# 
# "As a very brief explanation that isn't a full answer: If you use a string dtype in numpy, it's fundamentally a fixed-width c-like string. In pandas, they're "normal" python strings, thus the object type"
# 
# (That's why it was not working when in the code below I did  == 8)

# In[34]:


data["Math_test_results"] = data["Math_test_results"][data["Math_test_results"]["Grade"] == "8"]


# In[35]:


data["Math_test_results"].head()


# **Demographics:**

# In[36]:


data["Demographics"].head()


# Again data was collected for multiple years for the same school

# In[37]:


data["Demographics"]["schoolyear"].dtype


# In[38]:


data["Demographics"] = data["Demographics"][data["Demographics"]["schoolyear"] == 20112012]


# In[39]:


data["Demographics"].head(3)


# **Graduation_outcomes:**

# In[40]:


data["Graduation_outcomes"].head()


# I need to select Cohort == 2006

# In[41]:


(data["Graduation_outcomes"]['Cohort'] == '2006').any()


# In[42]:


data["Graduation_outcomes"]['Cohort'].dtype


# In[43]:


data["Graduation_outcomes"] = data["Graduation_outcomes"][data["Graduation_outcomes"]["Cohort"] == "2006"]
data["Graduation_outcomes"] = data["Graduation_outcomes"][data["Graduation_outcomes"]["Demographic"] == "Total Cohort"]


# Check data dictionary

# In[44]:


if IN_JUPYTER:
    for k,v in data.items():
        print("\n" + k + "\n")
        print(v.head(2))


# ### Computations

# **SAT score:**

# I will compute the _Total_ SAT score (SAT Math Avg. Score + SAT Critical Reading Avg. Score + SAT Writing Avg. Score) so I can compare the schools

# In[45]:


columns = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
for c in columns:
    data["SAT_Results"][c] = data["SAT_Results"][c].apply(pd.to_numeric, errors='coerce') #converting string to number

data['SAT_Results']['SAT_score'] = data['SAT_Results'][columns[0]] + data['SAT_Results'][columns[1]] + data['SAT_Results'][columns[2]]


# In[46]:


data["SAT_Results"].head()


# **Get schools coordinates for maps:**

# hsdirectory has a field 'Location 1' with the lat and lon of each school

# In[47]:


data["hsdirectory"]['Location 1'][0]


# Step by step:
# 1. I am creating a lambda function that will split by the string "\n"
# 2. I will them have 3 parts: '883 Classon Avenue', 'Brooklyn, NY 11225' and '(40.67029890700047, -73.96164787599963)'
# 3. I know I want the last bit. I can access it by either using [2] or [-1], as it is the last part
# 4. Then I need to remove both () in (40.67029890700047, -73.96164787599963)
# 5. I am left with 40.67029890700047, -73.96164787599963; so I will [0] to get lat and [1] to get lon ([-1] would also work for lon).

# In[48]:


data["hsdirectory"]['lat'] = data["hsdirectory"]['Location 1'].apply(lambda x: x.split("\n")[-1].replace("(", "").replace(")", "").split(", ")[0])
data["hsdirectory"]['lon'] = data["hsdirectory"]['Location 1'].apply(lambda x: x.split("\n")[-1].replace("(", "").replace(")", "").split(", ")[1])


# In[49]:


data["hsdirectory"].head()


# In[50]:


columns = ['lat', 'lon']
for c in columns:
    data["hsdirectory"][c] = data["hsdirectory"][c].apply(pd.to_numeric, errors='ignore')


# In[51]:


data["hsdirectory"].head()


# It worked!

# Check all the data:

# In[52]:


if IN_JUPYTER:
    for k,v in data.items():
        print(k)
        print(v.head(2))


# ### Use DBN to combine datasets

# In[53]:


# get the name of each data:
data_names = [k for k,v in data.items()]
# flat the data:
flat_data = [data[k] for k in data_names]
# get the 1st flat data as the base for the merge:
base_data = flat_data[0]


# In[54]:


len(base_data)


# In[55]:


print "# of DBN present in both is ", sum(data["SAT_Results"]["DBN"].isin(data["AP_results"]["DBN"]))
print "Length of DBN in SAT_results is ", len(data["SAT_Results"]["DBN"])
print "Length of DBN in AP_results is ",len(data["AP_results"]["DBN"])


# AP results dataset is missing high schools that exist in the SAT_results dataset

# In[56]:


print "# of DBN present in both is ", sum(data["SAT_Results"]["DBN"].isin(data["Graduation_outcomes"]["DBN"]))
print "Length of DBN in Graduation_outcomes is ",len(data["Graduation_outcomes"]["DBN"])


# AP_results dataset is missing high schools that exist in the SAT_results dataset

# In[57]:


print "# of DBN present in both is ", sum(data["SAT_Results"]["DBN"].isin(data["Math_test_results"]["DBN"]))
print "Length of DBN in Math_test_results is ",len(data["Math_test_results"]["DBN"])


# In[58]:


# this works too:
# len(set(data["SAT_results"]["DBN"]) & set(data["Graduation_outcomes"]["DBN"]))


# [Inner join produces only the set of records that match in both Table A and Table B.](https://blog.codinghorror.com/a-visual-explanation-of-sql-joins/)
# 
# [Outer join produces the set of all records in Table A and Table B, with matching records from both sides where available. If there is no match, the missing side will contain null.](https://blog.codinghorror.com/a-visual-explanation-of-sql-joins/)

# I will use 'outer' to join SAT_results, Graduation_outcomes and AP_results. So missing values will be filled with null.
# 
# Then I will use inner to join the above with Math_test_results.

# In[59]:


for i, f in enumerate(flat_data[1:]):
    # i is 0 to n
    # f is the data
    name = data_names[i+1] # I am using [0] as base_data
    print "%s length is %d " % (name, len(name))
    # find out the number of non-unique DBNs: get len of DBN - len unique DBN
    print "non-unique: ", (len(f["DBN"]) - len(f["DBN"].unique()))
    join_type = "inner" 
    if name in ["SAT_Results", "AP_results", "Graduation_outcomes"]:
        join_type = "outer"
    if name not in ["Math_test_results"]:
        base_data = base_data.merge(f, on="DBN", how=join_type)
        print join_type


# In[60]:


base_data.head()


# ### More convertions

# I need to convert the [AP](https://apscore.collegeboard.org/scores/about-ap-scores/) score to number

# In[61]:


cols = ['AP Test Takers ', 'Total Exams Taken', 'Number of Exams with scores 3 4 or 5']
for col in cols:
    base_data[col] = base_data[col].apply(pd.to_numeric, errors='coerce')

base_data[cols] = base_data[cols].fillna(value=0)


# ** get the district number from DBN**

# In[62]:


base_data["school_dist"] = base_data["DBN"].apply(lambda x: x[:2])


# In[63]:


#base_data.columns[base_data.isnull().any()].tolist()


# ** missing values**
# I will fill with the [mean](https://stats.stackexchange.com/questions/167829/how-do-we-decide-on-how-to-fill-missing-
# values-in-data)
# 
# [Good read](http://www.stat.columbia.edu/~gelman/arm/missing.pdf)

# In[64]:


base_data = base_data.fillna(base_data.mean())

#base_data = base_data.groupby(base_data.columns, axis = 1).transform(lambda x: x.fillna(x.mean()))


# In[65]:


base_data.head()


# ## Exploring data

# ### Correlations

# To check relationship or connection between columns

# **All data:**

# In[323]:


if IN_JUPYTER:
    corr = base_data.corr(method="pearson")
    sns.heatmap(corr)


# In[324]:


corr.head()


# **SAT_score:**

# In[67]:


base_data.corr()['SAT_score']


# **Correlation [coefficient](http://www.sjsu.edu/faculty/gerstman/StatPrimer/correlation.pdf):**
# 
# 0 < |r| < 0.3 weak correlation
# 
# 0.3 < |r| < 0.7 moderate correlation
# 
# |r| > 0.7 strong correlation

# From 'SAT_score' correlation above, 
# 
# * 'SAT Math Avg. Score' and 'SAT Writing Avg. Score' strongly correlates with 'SAT_score'
# * 'ell_percent' correlates negatively with 'SAT_score'
# * 'total_enrollment' correlates positively with 'SAT_score'
#     * smaller schools are not necessarily having better scores than big ones
# * It's possibile to identify some racial inequality in the data, with 'hispanic_per' and 'black_per' correlating negatively with 'SAT_score'
# * 'female_per' correlates positively with 'SAT_score'
# * 'male_per' correlates negatively with 'SAT_score'

# In[68]:


data2 = base_data[['SAT_score', 'SAT Math Avg. Score','SAT Writing Avg. Score',                   'ell_percent' ,'total_enrollment', 'white_per', 'asian_per', 'black_per',                   'hispanic_per', 'female_per', 'male_per']].copy()
corr2 = data2.corr()
if IN_JUPYTER:
    sns.heatmap(corr2)


# In[69]:


corr2


# In[70]:


data2.corr()['SAT_score']


# ### Maps

# **Schools:**

# In[217]:


schools_map = folium.Map(location=[base_data['lat'].mean(), base_data['lon'].mean()], zoom_start=10)
marker_cluster = MarkerCluster().add_to(schools_map)
for name, row in base_data.iterrows():
    # need to uncomment popupname, then run, then comment and run again - still dont know why
    #popupname = "{0}: {1}".format(row["DBN"], row["school_name"])
    
    folium.Marker([row["lat"], row["lon"]], popup = popupname).add_to(marker_cluster) 
    # if I dont want cluster (containing many markers)
    #folium.Marker([row["lat"], row["lon"]], popup = popupname).add_to(school_map) 

schools_map.save('schools.html')


# In[301]:


get_ipython().run_cell_magic(u'HTML', u'', u'<iframe width = "100%" height = 500 src = "./schools.html"></iframe>')


# In[219]:


schools_heatmap = folium.Map(location=[base_data['lat'].mean(), base_data['lon'].mean()], zoom_start=10)
schools_heatmap.add_child(HeatMap([[row["lat"], row["lon"]] for name, row in base_data.iterrows()]))
schools_heatmap.save("heatmap.html")


# In[300]:


get_ipython().run_cell_magic(u'HTML', u'', u'<iframe width = "100%" height = 500 src = "./heatmap.html"></iframe>')


# **SAT score by school district:**

# I will group the data by school district. Then I will compute the average of each column for each school district.

# In[146]:


mean_district_data = base_data.groupby("school_dist").agg(np.mean)
mean_district_data.reset_index(inplace=True)
mean_district_data["school_dist"] = district_data["school_dist"].apply(lambda x: str(int(x))) #removes 0 from beginning


# https://www.mapbox.com/api-documentation/#retrieve-a-static-map-from-a-style

# In[253]:


from folium.features import GeoJson
import json
def show_district_map(col, save_name, data_stat):
    geo_path = 'SchoolDistricts.geojson'
    districts = folium.Map(location=[base_data['lat'].mean(), base_data['lon'].mean()], zoom_start=10)
    districts.choropleth(
        geo_data = geo_path,
        data=data_stat,
        columns=['school_dist', col],
        key_on='feature.properties.school_dist',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
    )
    districts.save(save_name)
    #return districts


# In[254]:


show_district_map('SAT_score', 'Average_districts.html', mean_district_data )


# In[299]:


get_ipython().run_cell_magic(u'HTML', u'', u'<iframe width = "100%" height = 500 src = "./Average_districts.html"></iframe>')


# Above I can see now average of SAT_score by district. Max SAT_score (2010) is 2400, which would be a perfect score.
# Darker green represents the districts with higher average of SAT_score.
# Best SAT_score average:
# * Brooklyn: District 22 has the highest overall average.
# * Queens: Districts 26, 26 and 28 
# * Staten Island 

# I prefer to look at min, max and median values, rather than average:

# In[150]:


min_district_data = base_data.groupby("school_dist").agg(np.min)
min_district_data.reset_index(inplace=True)
min_district_data["school_dist"] = district_data["school_dist"].apply(lambda x: str(int(x))) 


# In[151]:


show_district_map('SAT_score', 'Min_districts.html', min_district_data )


# In[298]:


get_ipython().run_cell_magic(u'HTML', u'', u'<iframe width = "100%" height = 500 src = "./Min_districts.html"></iframe>')


# In[153]:


max_district_data = base_data.groupby("school_dist").agg(np.max)
max_district_data.reset_index(inplace=True)
max_district_data["school_dist"] = district_data["school_dist"].apply(lambda x: str(int(x)))
show_district_map('SAT_score', 'Max_districts.html', max_district_data )


# In[297]:


get_ipython().run_cell_magic(u'HTML', u'', u'<iframe width = "100%" height = 500 src = "./Max_districts.html"></iframe>')


# In[296]:


median_district_data = base_data.groupby("school_dist").agg(np.median)
median_district_data.reset_index(inplace=True)
median_district_data["school_dist"] = district_data["school_dist"].apply(lambda x: str(int(x)))
show_district_map('SAT_score', 'Median_districts.html', median_district_data )


# %%HTML
# <iframe width = "100%" height = 500 src = "./Median_districts.html"></iframe>

# * Brooklyn has the highest minimum SAT_score. But it also has the lowest SAT_score, alongside with Bronx.
# * Staten Island, Manhattan and Bronx have the highest SAT_score
# * Brooklyn and Queens presented the highest central tendency

# ### Scatter plots

# I will generate scatter plot of SAT_score against: 
# * SAT Math Avg. Score       
# * SAT Writing Avg. Score    
# * ell_percent              
# * total_enrollment          
# * white_per                 
# * asian_per                 
# * black_per                
# * hispanic_per             
# * female_per                
# * male_per                 

# In[264]:


if IN_JUPYTER:
    fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(15,20))
    base_data.plot.scatter(ax=axes[0,0], x='SAT Math Avg. Score', y='SAT_score').set_title('SAT score x SAT Math Avg. score')
    base_data.plot.scatter(ax=axes[0,1], x='SAT Writing Avg. Score', y='SAT_score').set_title('SAT score x SAT Writing Avg. Score')
    base_data.plot.scatter(ax=axes[1,0], x='ell_percent', y='SAT_score').set_title('SAT score x % of students who are learning English')
    base_data.plot.scatter(ax=axes[1,1], x='total_enrollment', y='SAT_score').set_title('SAT score x Total enrollment')
    base_data.plot.scatter(ax=axes[2,0], x='white_per', y='SAT_score').set_title('SAT score x White %')
    base_data.plot.scatter(ax=axes[2,1], x='asian_per', y='SAT_score').set_title('SAT score x Asian %')
    base_data.plot.scatter(ax=axes[3,0], x='black_per', y='SAT_score').set_title('SAT score x Black %')
    base_data.plot.scatter(ax=axes[3,1], x='hispanic_per', y='SAT_score').set_title('SAT score x Hispanic %')
    base_data.plot.scatter(ax=axes[4,0], x='female_per', y='SAT_score').set_title('SAT score x Female %')
    base_data.plot.scatter(ax=axes[4,1], x='male_per', y='SAT_score').set_title('SAT score x Male %')
    fig.subplots_adjust(hspace=1.5)
    plt.tight_layout()


# **% of students learning english:**

# In[255]:


show_district_map('ell_percent', 'ell_Median_districts.html', meadian_district_data )
show_district_map('ell_percent', 'ell_Max_districts.html', max_district_data )
show_district_map('ell_percent', 'ell_Mean_districts.html', median_district_data )


# In[295]:


get_ipython().run_cell_magic(u'HTML', u'', u'<table class="tg" width="100%">\n  <tr>\n    <th>% Students learning english (Median values)</th>\n    <th>SAT score (Median values)</th>\n  </tr>\n      <tr>\n    <th><iframe width = "100%" height = 500 src = "./ell_Median_districts.html"></iframe></th>\n    <th><iframe width = "100%" height = 500 src = "./Median_districts.html"></iframe></th>\n  </tr>\n  <tr>\n    <th>% Students learning english (Max values)</th>\n    <th>SAT score (Max values)</th>\n  </tr>\n      <tr>\n    <th><iframe width = "100%" height = 500 src = "./ell_Max_districts.html"></iframe></th>\n    <th><iframe width = "100%" height = 500 src = "./Max_districts.html"></iframe></th>\n  </tr>\n  <tr>\n    <th>% Students learning english (Mean values)</th>\n    <th>SAT score (Mean values)</th>\n  </tr>\n      <tr>\n    <th><iframe width = "100%" height = 500 src = "./ell_Mean_districts.html"></iframe></th>\n    <th><iframe width = "100%" height = 500 src = "./Average_districts.html"></iframe></th>\n  </tr>\n</table>')


# Districts with a high proportion of english learners tend to have low SAT scores. Districts with low proportion of english learners tend to have high SAT scores.
# More info about english learners can be found [here](https://nces.ed.gov/programs/coe/indicator_cgf.asp). The page states that "Students who are English language learners (ELLs) participate in language assistance programs to help ensure that they attain English proficiency and meet the same academic content and achievement standards that all students are expected to meet."

# **Total enrollment**

# Remarkable low total enrollment and low SAT scores. As seen above, districts with a high proportion of english learners tend to have low SAT scores.

# In[261]:


x = base_data[(base_data["total_enrollment"] < 1000) & (base_data["SAT_score"] < 1000)]["School Name"]
y = base_data[(base_data["total_enrollment"] < 1000) & (base_data["SAT_score"] < 1000)]["lat"]
z = base_data[(base_data["total_enrollment"] < 1000) & (base_data["SAT_score"] < 1000)]["lon"]
low_enroll = pd.concat([x,y,z], axis = 1)
low_enroll


# In[257]:


def show_low_enroll_map(col, save_name, data_stat):
    geo_path = 'SchoolDistricts.geojson'
    districts = folium.Map(location=[low_enroll['lat'].mean(), low_enroll['lon'].mean()], zoom_start=10)
    marker_cluster = MarkerCluster().add_to(districts)
    for name, row in low_enroll.iterrows():
        folium.Marker([row["lat"], row["lon"]], popup = popupname).add_to(marker_cluster)
    
    districts.choropleth(
        geo_data = geo_path,
        data=data_stat,
        columns=['school_dist', col],
        key_on='feature.properties.school_dist',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
    )
    districts.save(save_name)


# In[258]:


show_low_enroll_map('SAT_score', 'median_SAT_ell.html', median_district_data )
show_low_enroll_map('total_enrollment', 'median_enroll_ell.html', median_district_data )


# In[294]:


get_ipython().run_cell_magic(u'HTML', u'', u'<table class="tg" width="100%">\n  <tr>\n    <th>% SAT score (Median values)</th>\n    <th>Total enrollment (Median values)</th>\n  </tr>\n      <tr>\n    <th><iframe width = "100%" height = 500 src = "./median_SAT_ell.html"></iframe></th>\n    <th><iframe width = "100%" height = 500 src = "./median_enroll_ell.html"></iframe></th>\n  </tr>')


# The total enrollment is not correlated to SAT score. What is correlated is whether students are learning english as 2nd language. Most of the schools are for learning english, resulting in low enrollment.

# **Race and SAT scores**

# In[280]:


race = base_data[['SAT_score', 'white_per', 'asian_per', 'black_per',                  'hispanic_per']].copy()
corr = race.corr()
race_corr = base_data.corr()["SAT_score"][["white_per", "asian_per", "black_per", "hispanic_per"]]

if IN_JUPYTER:
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20,5))
    sns.heatmap(corr, ax=axes[0]).set_title('Heatmap - Correlation')
    race_corr.plot.bar(ax=axes[1]).set_title('Bar plot - Correlation')


# Higher % of white and asian students correlate with higher SAT scores. Higher % of black and hispanic students correlate with lower SAT scores. 

# In[291]:


show_low_enroll_map('black_per', 'black_districts.html', max_district_data )
show_low_enroll_map('hispanic_per', 'hispanic_districts.html', max_district_data )


# In[306]:


get_ipython().run_cell_magic(u'HTML', u'', u'<table class="tg" width="100%">\n  <tr>\n    <th>% Black students</th>\n    <th>SAT score(Max values)</th>\n  </tr>\n      <tr>\n    <th><iframe width = "100%" height = 500 src = "./black_districts.html"></iframe></th>\n    <th><iframe width = "100%" height = 500 src = "./Max_districts.html"></iframe></th>\n  </tr>\n  <tr>\n    <th>% Hispanic students</th>\n    <th>SAT score(Max values)</th>\n  </tr>\n      <tr>\n    <th><iframe width = "100%" height = 500 src = "./hispanic_districts.html"></iframe></th>\n    <th><iframe width = "100%" height = 500 src = "./Max_districts.html"></iframe></th>\n  </tr>')


# % of Balck students is higher in districts where SAT scores are low. I can identify the same patter for hispanic students with one difference, there's also a proportion of hispanic students learing english.
# 
# This [article](https://www.brookings.edu/research/race-gaps-in-sat-scores-highlight-inequality-and-hinder-upward-mobility/) provides a great discussion about both race and gender.

# **AP Score**

# Is there a relationship  between Advanced Placement exams and higher SAT scores?

# In[312]:


base_data["AP_proportion"] = (base_data["AP Test Takers "] / base_data["total_enrollment"])*100

base_data.plot.scatter(x='AP_proportion', y='SAT_score', title='SAT score by AP proportion')
plt.xlabel('% AP')
plt.ylabel('SAT score')


# Generally speaking, higher proportion of students taking the AP exam higher the SAT score.
# a strong correlation between the two. An interesting cluster of schools is the one at the top right, which has high SAT scores and a high proportion of students that take the AP exams:

# In[313]:


base_data[(base_data["AP_proportion"] > .3) & (base_data["SAT_score"] > 1700)]["School Name"]


# These schools above are  mostly highly selective school. From wikipedia:
# * ELEANOR ROOSEVELT HIGH SCHOOL: "Every year, the school selects 125 to 140 students out of over 6,000 applicants (...) Eleanor Roosevelt High School offers a comprehensive college preparatory program with Advanced Placement (AP) offerings, electives, and opportunities for college credit"
# * STUYVESANT HIGH SCHOOL: "is the most selective school of the nine specialized high schools in New York City, United States. (...) Admission to Stuyvesant involves passing the Specialized High Schools Admissions Test"
# * BEACON HIGH SCHOOL: "The Beacon School is a selective college-preparatory public high school. (...) Beacon also offers several Advanced Placement courses"
# 
# etc
