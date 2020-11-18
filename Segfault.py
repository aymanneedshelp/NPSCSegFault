import csv
import mysql.connector
import os,sys
from columnar import columnar
from tabulate import tabulate
import matplotlib.pyplot as plt

def numberlocations():#Numbering the locations
    if os.path.isfile('Populationnumbered.csv'):
        return
    f=open('Population.csv','r')
    f1=open('Populationnumbered.csv','w',newline='')
    csvr=csv.reader(f)
    csvw=csv.writer(f1)
    csvw.writerow(['x location','y location','population','zonenumber'])
    i=1
    for row in csvr:
        if csvr.line_num==1:
            continue

        k=row
        k.append(i)
        csvw.writerow(k)
        i+=1
    f.close()
    f1.close()
    f1=open('Populationnumbered.csv','r')
    csvr1=csv.reader(f1)
    zonedict={}
    for row in csvr1:
        if csvr1.line_num==1:
            continue
        t=(int(row[0]),int(row[1]))
        val=int(row[3])
        zonedict[t]=val
    f2=open("COVID_Dataset.csv",'r')
    f3=open("COVID_Dataset Zone.csv",'w',newline='')
    csvr2=csv.reader(f2)
    csvw3=csv.writer(f3)
    csvw3.writerow(['Time of Infection','Time of reporting','x location','y location','Age','Diabetes','Respiratory Illnesses','Abnormal Blood Pressure','Outcome','zone'])
    for row in csvr2:
        if csvr2.line_num==1:
            continue
        k=row
        key=(int(row[2]),int(row[3]))
        k.append(zonedict[key])
        csvw3.writerow(k)
    f2.close()
    f3.close()
def pushintosql(sqlpass):
    mycon=mysql.connector.connect(host="localhost",user="root",passwd=sqlpass)
    cursor=mycon.cursor()
    cursor.execute("Show databases")
    rec=cursor.fetchall()
    for i in rec:
        if i==('covid',):
            print("Available")
            return
    cursor.execute("Create database if not exists covid")#DatabaseName:Covid
    mycon.close()
    mycon=mysql.connector.connect(host="localhost",user="root",passwd=sqlpass,database="covid")
    cursor=mycon.cursor()
    cursor.execute("Create table if not exists Coviddataset(TimeofInfection int(4),Timeofreporting int(4),xlocation int(3),ylocation int(3),Age int(3),Diabetes varchar(10),Respiratoryillness varchar(10),AbnormalBloodPressure Varchar(10),Outcome varchar(10),Zone int(4))")
    cursor.execute("Create table if not exists population(Xlocation int(3),ylocation int(3),population int(10),zone int(5))")
    mycon.close()
    f1=open("COVID_Dataset Zone.csv",'r')
    csvr1=csv.reader(f1)
    mycon=mysql.connector.connect(host="localhost",user="root",passwd=sqlpass,database="covid")
    cursor=mycon.cursor()
    for row in csvr1:
        if csvr1.line_num==1:
            continue
        cursor.execute("Insert into coviddataset values(%s,%s,%s,%s,%s,'%s','%s','%s','%s',%s)"%(int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),row[5],row[6],row[7],row[8],int(row[9])))
        mycon.commit()
    f1.close()
    f2=open("Populationnumbered.csv",'r')
    csvr2=csv.reader(f2)
    for row in csvr2:
        if csvr2.line_num==1:
            continue
        cursor.execute("Insert into population values(%s,%s,%s,%s)"%(int(row[0]),int(row[1]),int(row[2]),int(row[3])))
        mycon.commit()
    mycon.close()


def sortByDisease():
    mycursor=mysql.connector.connect(host="localhost",user="root",passwd=sqlpass, database="covid")
    cursor=mycursor.cursor()
    cursor.execute("select xlocation, ylocation, Diabetes, Respiratoryillness, AbnormalBloodPressure from coviddataset")
    record= cursor.fetchall()
    
    l=[["X","Y","Diabetes","Respiratory","BP"]]
    bplist,rlist,dblist=[],[],[]
    labels=[]
    
    for i in range(1,21):
        for j in range(1,21):
            a,b,c=0,0,0
            for item in record:
                if item[0]==i and item[1]==j and item[2]=='True': #diabetes
                    a+=1
                elif item[0]==i and item[1]==j and item[3]=='True': #Respiratoryillness
                    b+=1
                elif item[0]==i and item[1]==j and item[4]=='True': #BP
                    c+=1
            l.append([i,j,a,b,c])
            dblist.append(a)
            rlist.append(b)
            bplist.append(c)
            labels.append(str(i)+','+str(j))
    table=tabulate(l)
    with open("Zone Comorbidities.txt",'w') as f:
        f.writelines(table)
    
    
    width=0.5
    fig,ax=plt.subplots()
    ax.bar(labels,dblist,width, label="Diabetes")
    ax.bar(labels,rlist,width,label="Respiratory")
    ax.bar(labels,bplist,width,bottom=rlist, label="Blood Pressure")

    ax.set_xlabel('Comorbidities')
    ax.set_ylabel('Number')
    ax.set_title('Comorbidities per Zone')

    ax.legend()
    plt.show()

def zonewise(zone,tableordata):
        mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
        cursor=mycon.cursor()
        cursor.execute("Select count(*) from coviddataset where zone=%s"%(zone))
        rec=cursor.fetchall()
        noofcases=0
        for i in rec:
           noofcases=i[0]
        cursor.execute("Select count(*) from coviddataset where zone=%s and outcome='Dead'"%(zone))
        rec=cursor.fetchall()
        death=0
        for i in rec:
            death=i[0]
        population=0
        cursor.execute('Select population from population where zone=%s'%(zone))
        rec=cursor.fetchall()
        for i in rec:
            population=i[0]
        try:
                
            deathrate=((death/noofcases)*100)
        except:
                deathrate=0
        try:
                
            populationinfected=((noofcases/population)*100)
        except:
            populationinfected=0
        age1=0
        age2=0
        age3=0
        cursor.execute("Select count(*) from coviddataset where age<15 and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            age1=i[0]
        cursor.execute("Select count(*) from coviddataset where age>=15 and age<=60 and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            age2=i[0]
        cursor.execute("Select count(*) from coviddataset where age>60 and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            age3=i[0]
        dbcount=0
        bpcount=0
        respicount=0
        cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            dbcount=i[0]
        cursor.execute("Select count(*) from coviddataset where Respiratoryillness='TRUE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
           respicount=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            bpcount=i[0]
        com1=0
        com2=0
        com3=0
        com4=0
        com5=0
        cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and Respiratoryillness='TRUE' and AbnormalBloodPressure='FALSE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            com1=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and Diabetes='FALSE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            com2=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and diabetes='TRUE' and Respiratoryillness='FALSE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            com3=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE'and diabetes='TRUE' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            com4=i[0]
        com5=com1+com2+com3+com4
        comdeath1=0
        comdeath2=0
        comdeath3=0
        comdeath4=0
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath1=0
        cursor.execute("Select count(*) from coviddataset where Respiratoryillness='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath2=0
        cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath3=0
        comdeath4=comdeath1+comdeath2+comdeath3
        comdeath5=0
        comdeath6=0
        comdeath7=0
        comdeath8=0
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and diabetes='TRUE' and respiratoryillness='FALSE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath5=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and diabetes='FALSE'and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath6=i[0]
        cursor.execute("Select count(*) from coviddataset where Diabetes='TRUE' and Respiratoryillness='TRUE' and AbnormalBloodPressure='FALSE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath7=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and diabetes='TRUE'and Respiratoryillness='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath8=i[0]
        comdeath9=comdeath5+comdeath6+comdeath7+comdeath8
        aged1=0
        aged2=0
        aged3=0
        cursor.execute("Select count(*) from coviddataset where age<15 and outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            aged1=i[0]
        cursor.execute("Select count(*) from coviddataset where age>=15 and age<=60 and outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            aged2=i[0]
        cursor.execute("Select count(*) from coviddataset where age>60 and outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            aged3=i[0]
        populationinfectedp=round(populationinfected,2)
        deathperc=round(deathrate,2)
        comdeath10=death-(comdeath4+comdeath9)
        if tableordata==0:
               return population,noofcases,populationinfectedp,age1,age2,age3,dbcount,respicount,bpcount,com5,death,deathperc,comdeath4,comdeath9,comdeath10,aged1,aged2,aged3


        
        txt1="General Information of zone "+str(zone)+"\n"
        data1=[['Population',str(population)],['Number of cases',str(noofcases)],["Percentage of population infected",str(round(populationinfected,2))+"%"]]
        headers=['Particulars','Count']
        table1=columnar(data1,headers)
        #print(txt1)
        #print(table1)
       
        txt2="Age wise analysis of cases of zone "+str(zone)+"\n"
        data2=[['Less than 15 years',str(age1)],['15 to 60 years',str(age2)],['Above 60 years',str(age3)]]
        table2=columnar(data2,headers)
        txt3="Analysis of cases of "+str(zone)+" based on comorbities"+'\n'
        data3=[["Diabetes",str(dbcount)],["Respiratory disorders",str(respicount)],["Abnormal Blood Pressure",str(bpcount)],["Multiple comorbidities",str(com5)]]
        table3=columnar(data3,headers)
        txt4="Analysis of deaths of zone "+str(zone)+"\n"
        data4=[["Number of deaths",str(death)],["Death rate",str(round(deathrate,2))+"%"],["Deaths with single comorbidities",str(comdeath4)],["Deaths with multiple comorbidities",str(comdeath9)],["Deaths without comorbidities",str(death-(comdeath4+comdeath9))],['Less than 15 years',str(aged1)],['Between 15 to 60 years',str(aged2)],['Above 60 years',str(aged3)]]
        
        table4=columnar(data4,headers)
        msg=txt1+table1+txt2+table2+txt3+table3+txt4+table4
        if tableordata==1:
                print(msg)
                return
        
sqlpass = input("Enter SQL Password ")   


numberlocations()
pushintosql(sqlpass)
sortByDisease()
