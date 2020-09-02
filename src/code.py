#!/usr/bin/env python
# coding: utf-8

# # Analysis of weapon types for violent crimes in NSW

# Python code to analyze weapon types for violent crimes in NSW based on data from the NSW Bureau of Crime Statistics and Research.

# # Loading libraries

# Let's load relevant Python libraries.

# In[1]:


import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 
import matplotlib as mpl
import squarify
import plotly.io as pio
import plotly.express as px
from IPython.display import display, Markdown
import warnings
warnings.filterwarnings("ignore")


# # Loading data

# The dataset was acquired from https://www.bocsar.nsw.gov.au/.

# In[2]:


print(pd.ExcelFile('Weapons Statistics.xls').sheet_names)


# There is only one sheet.

# In[3]:


data = pd.read_excel('Weapons Statistics.xls', 'Sheet1')


# In[4]:


data.head()


# The first four rows need to be skipped because they are part of a header.

# In[5]:


data = pd.read_excel('Weapons Statistics.xls', 'Sheet1', skiprows=4)


# We should be good to go.

# # Data pre-processing

# In[6]:


data.head()


# In[7]:


data.tail(10)


# Rows with IDs higher than 108 need to be removed because they are part of the footer of the excel file.

# In[8]:


data = data[data.index<=108]


# The 'Unnamed: 2' column is the offence subtype. We can just combined 'Offence type' and 'Unnamed: 2'.

# In[9]:


for i in range(len(data)):
    if str(data['Unnamed: 2'][i])!='nan':
        data['Offence type'][i] = data['Unnamed: 2'][i]
        data['Offence type'][i] = data['Offence type'][i].replace(' *', '')
data = data.drop(['Unnamed: 2'], axis=1)        
data.head()


# Now, we need to convert the dataframe into a multi-indexed dataframe. Before that, NaN values of 'Weapon type' needs to be replaced with the values of the respective previous roles. For example, 'Weapon type' of the the second row (id=1) shoould be 'Firearms' instead of 'NaN'.

# In[10]:


data.rename(columns={
    'Weapon type' : 'Weapon',
    'Offence type' : 'Offence',
    'Jan 2013 - Dec 2013' : '2013',
    'Jan 2014 - Dec 2014' : '2014',
    'Jan 2015 - Dec 2015' : '2015',
    'Jan 2016 - Dec 2016' : '2016',
    'Jan 2017 - Dec 2017' : '2017',
    'Jan 2018 - Dec 2018' : '2018',
    'Jan 2019 - Dec 2019' : '2019'    
}, inplace=True)
for i in range(1, len(data)):    
    if str(data.Weapon[i])=='nan':
        data.Weapon[i] = data.Weapon[i-1]
    data.Weapon[i] = data.Weapon[i].replace('\n', '')    
data.dropna(inplace=True)
data.set_index(['Weapon', 'Offence'], inplace=True)
data.head()


# We are good to go

# # Trend analysis of annual total crimes involving weapons

# In[11]:


trend = data.sum(axis = 0) 


# In[12]:


trend.plot(kind = 'line', color = 'blue', linewidth=3,alpha = 1,grid = True,linestyle = '-')
plt.title('Annual total crimes involving weapons')
plt.xlabel('Year')              
plt.ylabel('Number of cases')
plt.show()


# Interestingly, the total number of crimes involving weapons in NSW bottomed out in 2017 before rising again in 2018.

# # Overall analysis of weapons

# In[13]:


weapons = data.groupby(level=[0]).sum()
weapons.head()


# In[14]:


def Plot(weapon, color):
    weapon.plot(kind = 'line', color =color, linewidth=3,alpha = 1,grid = True,linestyle = '-')
    plt.title("")
    plt.xlabel('Year')              
    plt.ylabel('Number of cases')
    plt.show()


# In[15]:


np.random.seed(4)
colors = np.random.choice(list(mpl.colors.XKCD_COLORS.keys()), len(weapons.T.columns), replace=False)
for i, weapon in enumerate(weapons.T.columns):
    print("Trend of '" + weapon + "'")
    print()
    Plot(weapons.T[weapon], colors[i])


# In[16]:


overall = weapons.sum(axis=1).sort_values(ascending=False).copy()
print(overall)


# In[17]:


labels = []
for i in range(len(overall)):
    labels.append(overall.index[i].replace('/', '/\n'))
    
overall.index = labels


# In[18]:


count_html_output = 1
def SaveAsHTML(fig):
    global count_html_output
    #fig.show()
    #pio.write_html(fig, file='src/' + str(count_html_output) + '.html', auto_open=False)
    #print ('<iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="src/' + str(count_html_output) + '.html" height="100%" width="100%"></iframe>')
    fig.write_image("src/" + str(count_html_output) + ".png")
    display(Markdown("![png](src/" + str(count_html_output) + ".png)"))
    count_html_output = count_html_output + 1


# In[19]:


fig = px.treemap(overall.to_frame('Cases').reset_index(), 
                 path=['index'], 
                 values='Cases',      
                 hover_data=['Cases'],
                 color_continuous_scale='ice',
                 color='Cases'
                )
SaveAsHTML(fig)


# Knife and other stabbing weapons are mostly used in violent crimes. Interestingly, bows, arrows and boomerangs are also used.

# In[20]:


plt.figure(figsize=(10,15))
sns.barplot(x=overall, y=overall.index, orient='h', palette='inferno' )
plt.xticks(rotation=90)
plt.title('Types of weapons used')
plt.show()


# # Analysis of types of weapons for various crimes

# In[21]:


weaponoffence = data.sum(axis=1)
print(weaponoffence)


# ### Overall

# In[22]:


fig = px.treemap(weaponoffence.to_frame('Cases').reset_index(), 
                 path=['Offence', 'Weapon'], 
                 values='Cases',
                 hover_data=['Cases'],                 
                 color='Cases'
                )
SaveAsHTML(fig)


# In[23]:


unstacked = weaponoffence.unstack(level=1).fillna(0)
for crime in unstacked.columns:
    display(Markdown("### Weapons used for '" + crime + "'"))
    np.random.seed(9)
    
    values = []
    labels = []
    sorteddata = unstacked[crime].sort_values(ascending=False);
    for i, row in enumerate(sorteddata):
        if row==0:
            break;
        values.append(row)
        labels.append(sorteddata.index[i])
    
    df = pd.DataFrame(
     {'Cases': values,
     'Weapon': labels,     
    })
    
    print(df.set_index('Weapon'))
    
    fig.update_traces(textinfo='value')
    
    fig1 = px.treemap(df, 
                 path=['Weapon'], 
                 values='Cases',      
                 hover_data=['Cases'],                
                 color_continuous_scale='earth',
                 color='Cases'
                )
    SaveAsHTML(fig1)
    
    fig2 = px.pie(df, 
                  values='Cases', 
                  names='Weapon'               
                 )
    fig2.update_traces(textinfo='value')
    SaveAsHTML(fig2)
    
    print()
    print()
  
    


# # Analysis of crimes committed using various weapons

# ### Overall

# In[24]:


fig = px.treemap(weaponoffence.to_frame('Cases').reset_index(), 
                 path=['Weapon', 'Offence'], 
                 values='Cases',
                 color='Cases'
                )
SaveAsHTML(fig)


# In[25]:


unstacked = weaponoffence.unstack(level=0).fillna(0)
for weapon in unstacked.columns:
    display(Markdown("### Crimes committed using '" + weapon + "'"))
    np.random.seed(9)
    
    values = []
    labels = []
    sorteddata = unstacked[weapon].sort_values(ascending=False);
    for i, row in enumerate(sorteddata):
        if row==0:
            break;
        values.append(row)
        labels.append(sorteddata.index[i])
    
       
    df = pd.DataFrame(
     {'Cases': values,
     'Crime': labels,     
    })
    
    print(df.set_index('Crime'))
    
    fig.update_traces(textinfo='value')
    
    fig1 = px.treemap(df, 
                 path=['Crime'], 
                 values='Cases',      
                 hover_data=['Cases'],
                 color_continuous_scale='algae',
                 color='Cases'
                )
    SaveAsHTML(fig1)
    
    fig2 = px.pie(df, 
                  values='Cases', 
                  names='Crime',
                 color_discrete_sequence=px.colors.diverging.Portland
                 )
    fig2.update_traces(textinfo='value')
    SaveAsHTML(fig2)
    
    print()
    print()
   
    

