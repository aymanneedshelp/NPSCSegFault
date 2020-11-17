import csv
import mysql.connector
import os,sys
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
def pushintosql():
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


sqlpass = input("Enter SQL Password ")

numberlocations()
pushintosql()

