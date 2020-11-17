import csv
from matplotlib import pyplot as plt

f=open("COVID_Dataset.csv",'r')
data=csv.reader(f)
count=-1 # to skip first line
death=0
for i in data:
    count=count+1
    if i[8]=='Dead':
        death=death+1   
f.close()

f=open("Seperation_age.txt","w")
f.writelines(["Age \t","Coronavirus Cases \t","Deaths \t","Death Rate\n"])
f.close()

def age_seperation(a,b):
    f=open("COVID_Dataset.csv",'r')
    data=csv.reader(f)
    count=0
    death=0
    next(data)#skip first line
    for i in data:
        if a<= int(i[4]) <=b:
            count=count+1
            if i[8]=='Dead':
                death=death+1   
    f.close()
    
    rate=round(((death/count)*100),2)
    age=str(a)+'-'+str(b)
    f=open("Seperation_age.txt","a")
    f.writelines([age+'\t',str(count)+'\t\t',str(death)+'\t',str(rate)+'\n'])
    f.close()

    return count,death

covid=[]
dead=[]

data=age_seperation(0,9)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(10,19)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(20,29)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(30,39)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(40,49)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(50,59)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(60,69)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(70,79)
covid.append(data[0])
dead.append(data[1])

data=age_seperation(80,89)
covid.append(data[0])
dead.append(data[1])
      
deathrate=round(((death/count)*100),2)
f=open("Seperation_age.txt","a")
f.writelines(["\nTotal Coronavirus Cases : ",str(count)])
f.writelines(["\nTotal Deaths : ",str(death)])
f.writelines(["\nDeath Rate : ",str(deathrate)])
f.close()
    
#pie plotter

age=['0 to 9','10 to 19','20 to 29','30 to 39','40 to 49','50 to 59','60 to 69','70 to 79','80 to 89',]
colors = ( "orange", "cyan", "blue","grey", "indigo", "beige","lightgreen","silver","yellow")
fig = plt.figure(figsize =(10, 7))
expand=(0.1,0.1,0.1,0.1,0.1,0,0.1,0.1,0.1)
plt.title("Coronavirus Cases - AGE ")
plt.pie(covid,labels=age,autopct='%1.1f%%',colors=colors,explode=expand,shadow=True)
plt.show()

fig = plt.figure(figsize =(10, 7))
expand=(0.1,0.1,0.1,0.1,0.1,0,0.1,0.1,0.1)
plt.title("Coronavirus Deaths - AGE ")
plt.pie(dead,labels=age,autopct='%1.1f%%',colors=colors,explode=expand,shadow=True)
plt.show()

