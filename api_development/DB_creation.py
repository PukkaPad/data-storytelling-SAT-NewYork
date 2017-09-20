
# coding: utf-8

# In[13]:


get_ipython().magic(u"run '../utils/DataStorytelling-SAT-NewYork.ipynb'")


# In[14]:


corr2.reset_index(inplace=True)
corr2.rename(columns={'index': 'name'}, inplace=True)


# In[15]:


#list(base_data) 


# In[16]:


base_data.rename(columns={'SCHOOL NAME': 'SCHOOLNAME1'}, inplace=True)


# In[17]:


import sqlite3
connex = sqlite3.connect("SAT_NewYork_DB.db")  # Opens file if exists, else creates file
connex.text_factory = lambda x: unicode(x, "utf-8", "ignore")
cur = connex.cursor()  # This object lets us actually send messages to DB and receive results


# In[18]:


base_data.to_sql(name="AllData", con=connex, if_exists="append", index=False)  #"name" is name of table 
corr2.to_sql(name="SAT_Correlation", con=connex, if_exists="append", index=False)


# In[19]:


connex.commit()
connex.close()


# In[ ]:




