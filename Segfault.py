import pip,csv,os,sys,operator

def install(name): #function used to install missing libraries
    if hasattr(pip, 'main'):
        pip.main(['install', name])
    else:
        pip._internal.main(['install', name])

try:
    import mysql.connector
    from columnar import columnar
    from tabulate import tabulate
    import matplotlib.pyplot as plt
    from matplotlib_venn import venn3
except:
    install('matplotlib')
    install('mysql.connector')
    install('matplotlib_venn')
    install('columnar')
    install('tabulate')

def numberlocations():#Numbering the locations
    if os.path.isfile('Populationnumbered.csv'):
        return
    f=open('Dataset/Population.csv','r')
    f1=open('Dataset/Populationnumbered.csv','w',newline='')
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
    f1=open('Dataset/Populationnumbered.csv','r')
    csvr1=csv.reader(f1)
    zonedict={}
    for row in csvr1:
        if csvr1.line_num==1:
            continue
        t=(int(row[0]),int(row[1]))
        val=int(row[3])
        zonedict[t]=val
    f2=open("Dataset/COVID_Dataset.csv",'r')
    f3=open("Dataset/COVID_Dataset Zone.csv",'w',newline='')
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
    mycon=mysql.connector.connect(host="localhost",user="root",passwd='sql123')
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
    f1=open("Dataset/COVID_Dataset Zone.csv",'r')
    csvr1=csv.reader(f1)
    mycon=mysql.connector.connect(host="localhost",user="root",passwd=sqlpass,database="covid")
    cursor=mycon.cursor()
    for row in csvr1:
        if csvr1.line_num==1:
            continue
        cursor.execute("Insert into coviddataset values(%s,%s,%s,%s,%s,'%s','%s','%s','%s',%s)"%(int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),row[5],row[6],row[7],row[8],int(row[9])))
        mycon.commit()
    f1.close()
    f2=open("Dataset/Populationnumbered.csv",'r')
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
    cursor.execute("select xlocation, ylocation, Diabetes, Respiratoryillness, AbnormalBloodPressure, Outcome from coviddataset")
    record= cursor.fetchall()
    
    l=[["X","Y","Diabetes","Respiratory","BP"]]
    bplist,rlist,dblist=[],[],[]
    labels=[]
    dictionary={}
    
    for i in range(1,21):
        for j in range(1,21):
            a,b,c,d=0,0,0,0
            for item in record:
                if item[0]==i and item[1]==j and item[2]=='True': #diabetes
                    a+=1
                elif item[0]==i and item[1]==j and item[3]=='True': #Respiratoryillness
                    b+=1
                elif item[0]==i and item[1]==j and item[4]=='True': #BP
                    c+=1
                elif item[0]==i and item[1]==j and item[5]=='DEAD': #No. of dead ppl
                    d+=1
                
            l.append([i,j,a,b,c])
            dblist.append(a)
            rlist.append(b)
            bplist.append(c)
            labels.append(str(i)+','+str(j))
            
            score = a + 2*b + 2*c +d #this score will be used to dertermine necessity of vaccine(higher = greater need)
            dictionary[str(i)+','+str(j)] = score
    
    #tabulate the number of diseases per zone in a txt file
    table=tabulate(l)
    with open("Output_Files/Zone Comorbidities.txt",'w') as f:
        f.writelines(table)
    
    #represent the number of diseases per zone as a bar graph:
    width=0.5
    fig,ax=plt.subplots()
    ax.bar(labels,dblist,width, label="Diabetes")
    ax.bar(labels,rlist,width,label="Respiratory")
    ax.bar(labels,bplist,width,bottom=rlist, label="Blood Pressure")

    ax.set_xlabel('Co-morbidities')
    ax.set_ylabel('Number')
    ax.set_title('Co-morbidities per Zone')

    ax.legend()
    plt.show()

    #sorting the dictionary to put the highest score first
    sorted_dict = sorted(dictionary.items(), key=operator.itemgetter(1),reverse=True)
    table2=tabulate(sorted_dict)
    with open("Output_Files/vaccine_priority.txt",'w') as f:
        f.writelines(table2)

def zonewise(zone,tableordata):
        returnlist=[]
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
        cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and Respiratoryillness='TRUE'  and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            com1=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and   zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            com2=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and diabetes='TRUE' and  zone=%s"%(zone))
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
            comdeath1=i[0]
        cursor.execute("Select count(*) from coviddataset where Respiratoryillness='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath2=i[0]
        cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath3=i[0]
        comdeath4=comdeath1+comdeath2+comdeath3
        
        comdeath5=0
        comdeath6=0
        comdeath7=0
        comdeath8=0
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and diabetes='TRUE' and  Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath5=i[0]
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and Outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
            comdeath6=i[0]
        cursor.execute("Select count(*) from coviddataset where Diabetes='TRUE' and Respiratoryillness='TRUE' and Outcome='Dead' and zone=%s"%(zone))
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
        comdeath10=0
        cursor.execute("Select count(*) from coviddataset where AbnormalBloodPressure='FALSE' and Diabetes='FALSE' and Respiratoryillness='FALSE'and outcome='Dead' and zone=%s"%(zone))
        rec=cursor.fetchall()
        for i in rec:
                comdeath10=i[0]
       
       
       
        txt1="General Information of zone "+str(zone)+"\n"
        data1=[['Population',str(population)],['Number of cases',str(noofcases)],["Percentage of population infected",str(round(populationinfected,2))+"%"]]
        headers=['Particulars','Count']
        table1=columnar(data1,headers)
        
       
        txt2="Age wise analysis of cases of zone "+str(zone)+"\n"
        data2=[['Less than 15 years',str(age1)],['15 to 60 years',str(age2)],['Above 60 years',str(age3)]]
        table2=columnar(data2,headers)
        txt3="Analysis of cases of zone "+str(zone)+" based on comorbidities"+'\n'
        data3=[["Diabetes",str(dbcount)],["Respiratory disorders",str(respicount)],["Abnormal Blood Pressure",str(bpcount)],["Multiple comorbidities",str(com5)]]
        table3=columnar(data3,headers)
        txt4="Analysis of deaths of zone "+str(zone)+"\n"
        data4=[["Number of deaths",str(death)],["Death rate",str(round(deathrate,2))+"%"],["Deaths with single comorbidities",str(comdeath4)],["Deaths with multiple comorbidities",str(comdeath9)],["Deaths without comorbidities",str(comdeath10)],['Less than 15 years',str(aged1)],['Between 15 to 60 years',str(aged2)],['Above 60 years',str(aged3)]]
        
        table4=columnar(data4,headers)
        msg=txt1+table1+txt2+table2+txt3+table3+txt4+table4
       
        if tableordata==1:
                print(msg)
        if tableordata==0:
                return population,noofcases,populationinfectedp,age1,age2,age3,dbcount,respicount,bpcount,com5,death,deathperc,comdeath4,comdeath9,comdeath10,aged1,aged2,aged3
                      
def generatereportfor400zones():
        if os.path.isfile('Output_Files/zonewisereport.csv'):
                return
       
        f1=open("zonewisereport.csv",'w',newline='')
        csvw=csv.writer(f1)
        csvw.writerow(['Zone','Population','Number of cases','Percentage of  Population infected','Cases less than 15 years','Cases between 15 to 60 yrs','Cases above 60 years','Cases with diabetes','Cases with respiratory disorders','Cases with abnormal BP','Cases with multiple comorbidities','Number of deaths','Death Rate','Death with single comorbidity','Death with multiple comorbidities','Deaths without comorbidities','Death less than 15 years','Deaths between 15 to 60 years','Deaths above 60 years'])
        
        for z in range(1,401):
                
               
                a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r=zonewise(z,0)
                csvw.writerow([z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r])
                f1.flush()
        f1.close()

def intensitymap():
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cases=[]
    population=[]
    for i in range(1,401):
        cursor.execute("Select count(*) from coviddataset where zone=%s"%(i))
        rec=cursor.fetchall()
       
        for j in rec:
            cases.append(j[0])
        cursor.execute("Select population from population where zone='%s'"%(i))
        rec=cursor.fetchall()
        for k in rec:
            population.append(k[0])
   
    percdict={}
    for i in range(400):
        perc=(cases[i]/population[i])*100
        percdict[i+1]=perc
    descsort=dict(sorted(percdict.items(),key=lambda item:item[1],reverse=True))
    redzone=[]
    orangezone=[]
    
    yellowzone=[]
    lbzone=[]
    greenzone=[]
    for key in descsort:
        if descsort[key]>=60:
            redzone.append(key)
        if 40<=descsort[key]<60:
            orangezone.append(key)
        if 10<=descsort[key]<40:
            yellowzone.append(key)
       
        if descsort[key]<10:
            greenzone.append(key)
    
    redco=[]
    greenco=[]
    yellowco=[]
    orangeco=[]
   
    for i in redzone:
        cursor.execute("Select xlocation,ylocation from population where zone=%s"%(i))
        rec=cursor.fetchall()
        redco.append(rec[0])

    for i in orangezone:
        cursor.execute("Select xlocation,ylocation from population where zone=%s"%(i))
        rec=cursor.fetchall()
        orangeco.append(rec[0])
    for i in yellowzone:
        cursor.execute("Select xlocation,ylocation from population where zone=%s"%(i))
        rec=cursor.fetchall()
        yellowco.append(rec[0])
    for i in greenzone:
        cursor.execute("Select xlocation,ylocation from population where zone=%s"%(i))
        rec=cursor.fetchall()
        greenco.append(rec[0])

    # import package and making objects 
    import turtle 
    
    T=turtle.Turtle()
    T1=turtle.Turtle()
    T1.speed(0)
    T.speed(0)
    
    #initialized position 
    T.penup()
    T.setpos(-400,-400)
    T.pendown()
    T.hideturtle()
    T1.hideturtle()
    
    #grid
    for i in range(4):
        T.forward(800)
        T.left(90)
        
    for i in range(10):
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        T.forward(40)
        T.right(90)
    
    for i in range(10):
        T.forward(40)
        T.right(90)
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        
    T.left(90)
    
    def colour_grading():
        T.penup()
        T.setpos(-800,300)
        T.pendown()
        T.left(90)
        
        for i in range(30):
            T.pencolor("red")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
    
        T.write(" Greater than 60 % ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        
        
        for i in range(30):
            T.pencolor("orange")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
            
        T.write(" Between 40 % and 60 %  ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,100)
        T.pendown()
    
        for i in range(30):
            T.pencolor("gold")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
            
            
        T.write(" Between 10 % and 40 % ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,0)
        T.pendown()
    
        for i in range(30):
            T.pencolor("lightgreen")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
    
        T.write(" Less than 10 % ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        T.left(90)
    
        T.pencolor("black")    
        
    def red_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("red")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()
    
    def orange_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("orange")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()
    
    def yellow_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("yellow")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()
    
    def green_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("lightgreen")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()
    

    for i in redco:
        red_zone(i)
    for i in orangeco:
        orange_zone(i)
    for i in yellowco:
        yellow_zone(i)
    for i in greenco:
        green_zone(i)
    
    
    colour_grading()
    T.fillcolor('black')
    # writing x axis
    T.penup()
    T.setpos(-390,410)
    T.pendown()
    T.write("X",move=True,font=("Verdana", 20, "bold"))
    T.right(270)
    T.forward(200)
    T.showturtle()
    
    #writing Heading and  y axis
    T1.penup()
    T1.setpos(-100,450)
    T1.pendown()
    T1.pencolor("blue")
    T1.write("Covid Intensity Map ",move=True,font=("Verdana", 25, "bold"))
    T1.pencolor("black")
    
    T1.penup()
    T1.setpos(-425,360)
    T1.pendown()
    T1.write("Y",move=True,font=("Verdana", 20, "bold"))
    T1.penup()
    T1.setpos(-416,360)
    T1.pendown()
    T1.right(90)
    T1.forward(200)
    T1.showturtle()
    
def Basic_city_age():
    import csv
    from matplotlib import pyplot as plt

    f=open("Dataset/COVID_Dataset.csv",'r')
    data=csv.reader(f)
    count=-1 # to skip first line
    death=0
    for i in data:
        count=count+1
        if i[8]=='Dead':
            death=death+1   
    f.close()

    f=open("Output_Files/Basic-Age.txt","w")
    f.writelines(["Age \t","Coronavirus Cases \t","Deaths \t","Death Rate\t","Recovered\t","Recovery Rate\n"])
    f.close()

    def age_seperation(a,b):
        f=open("Dataset/COVID_Dataset.csv",'r')
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
        recovered=count-death
        drate=round(((death/count)*100),2)
        rrate=round(((recovered/count)*100),2)
        age=str(a)+'-'+str(b)
        f=open("Output_Files/Basic-Age.txt","a")
        f.writelines([age+'\t',str(count)+'\t\t',str(death)+'\t',str(drate)+'\t\t',str(recovered)+'\t\t',str(rrate)+'\n'])
        f.close()

        return count,death,recovered

    covid=[]
    dead=[]
    recover=[]

    data=age_seperation(0,9)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(10,19)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(20,29)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(30,39)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(40,49)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(50,59)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(60,69)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(70,79)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    data=age_seperation(80,89)
    covid.append(data[0])
    dead.append(data[1])
    recover.append(data[2])

    recovered=count-death      
    deathrate=round(((death/count)*100),2)
    recoveryrate=round(((recovered/count)*100),2)
    f=open("Output_Files/Basic-Age.txt","a")
    f.writelines(["\nTotal Coronavirus Cases : ",str(count)])
    f.writelines(["\nDeaths : ",str(death)])
    f.writelines(["\tDeath Rate : ",str(deathrate)])
    f.writelines(["\nRecovered : ",str(recovered)])
    f.writelines(["\tRecovery Rate : ",str(recoveryrate)])
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

def venncasescity():
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    a=b=c=d=e=f=g=h=0
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE'")
    rec=cursor.fetchall()
    for i in rec:
        a=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE'")
    rec=cursor.fetchall()
    for i in rec:
        c=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE'")
    rec=cursor.fetchall()
    for i in rec:
        g=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE'")
    rec=cursor.fetchall()
    for i in rec:
        b=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE'")
    rec=cursor.fetchall()
    for i in rec:
        d=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE'")
    rec=cursor.fetchall()
    for i in rec:
        f=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE'")
    rec=cursor.fetchall()
    for i in rec:
        e=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE'")
    rec=cursor.fetchall()
    for i in rec:
        h=i[0]
   
        
    
    
    
    v3=venn3(subsets={'100':a,'010':c,'110':b,'001':g,'101':d,'011':f,'111':e},set_labels=('Diabetes','AbnormalBloodPressure','Respiratory illness',))
    t="Analysis of Comorbidities of city "+"\n"+"Cases without comorbidities: "+str(h)
    plt.title(t)
    plt.show()
 
def venndeathscity():
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    a=b=c=d=e=f=g=h=0
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        a=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        c=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        g=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        b=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        d=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        f=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        e=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE' and outcome='Dead'")
    rec=cursor.fetchall()
    for i in rec:
        h=i[0]
   
        
    
    
    
    v3=venn3(subsets={'100':a,'010':c,'110':b,'001':g,'101':d,'011':f,'111':e},set_labels=('Diabetes','AbnormalBloodPressure','Respiratory illness',))
    t="Analysis of Deaths of city "+"\n"+"Deaths without comorbidities: "+str(h)
    plt.title(t)
    plt.show()

def venndeaths(zone):
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cursor.execute("Select count(*) from coviddataset where outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        if i[0]==0:
            print("No deaths reported in this zone")
            return
    a=b=c=d=e=f=g=h=0
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        a=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        c=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        g=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        b=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        d=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and outcome='Dead'and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        f=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        e=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE' and outcome='Dead' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        h=i[0]
   
        
    
    
    
    v3=venn3(subsets={'100':a,'010':c,'110':b,'001':g,'101':d,'011':f,'111':e},set_labels=('Diabetes','AbnormalBloodPressure','Respiratory illness',))
    
    t="Analysis of Deaths of zone "+str(zone)+"\n"+"Deaths without comorbidities: "+str(h)
    plt.title(t)
    plt.show()  
    
def venncases(zone):
    
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    a=b=c=d=e=f=g=h=0
    cursor.execute("Select count(*) from coviddataset where zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        if i[0]==0:
            print("No cases reported in this zone")
            return
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        a=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        c=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        g=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='TRUE' and Respiratoryillness='FALSE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        b=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE' and AbnormalBloodPressure='FALSE' and Respiratoryillness='TRUE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        d=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        f=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='TRUE'and AbnormalBloodPressure='TRUE' and Respiratoryillness='TRUE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        e=i[0]
    cursor.execute("Select count(*) from coviddataset where diabetes='FALSE'and AbnormalBloodPressure='FALSE' and Respiratoryillness='FALSE' and zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        h=i[0]
   
        
    
    
    
    v3=venn3(subsets={'100':a,'010':c,'110':b,'001':g,'101':d,'011':f,'111':e},set_labels=('Diabetes','AbnormalBloodPressure','Respiratory illness',))
    t="Analysis of Comorbidities of zone "+str(zone)+"\n"+"Cases without comorbidities: "+str(h)
    plt.title(t)
    plt.show()
    
def showgraphbasedoncasesreportedperday(zone): #Plot a graph based on daily cases in a zone
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cursor.execute("Select count(*) from coviddataset where zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        if i[0]==0:
            print('No cases')
            return
        
    x=[]
    y=[]
    for i in range(239):
        x.append(i)
        cursor.execute("select count(*) from coviddataset where zone=%s and Timeofinfection=%s"%(zone,i))
        rec=cursor.fetchall()
        for j in rec:
            y.append(j[0])
    plt.plot(x,y,color='blue')
        
    plt.xlabel('Day')
    plt.ylabel('Number of cases per day')
    t='Daywise cases of zone'+str(zone)
    plt.title(t)
    plt.show()

def zonewisedaywise():#Creating a table called zonewise daywise in mysql and inserting the zone,day and the number of cases in a day in a zone
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cursor.execute('Show tables')
    rec=cursor.fetchall()
    for i in rec:
        if i==(zonewisedaywise,):
            return
    cursor.execute("Select max(timeofinfection) from coviddataset")
    rec=cursor.fetchall()
    maxd=0
    for i in rec:
        maxd=i[0]
    cursor.execute("Create table if not exists zonewisedaywise(zone int(9),day int(9),cases int(9))")
    for zo in range(1,401):
        
        for da in range(0,maxd+1):
            cursor.execute("Select count(*) from coviddataset where zone=%s and timeofinfection=%s"%(zo,da))
            rec=cursor.fetchall()
            c=0
            for i in rec:
                c=i[0]
            cursor.execute("Insert into zonewisedaywise values (%s,%s,%s)"%(zo,da,c))
            mycon.commit()
          
def graphcumm(zone):#Graph which shows cumulative cases of a zone
    import mysql.connector
    import numpy as np
    import matplotlib.pyplot as plt
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cursor.execute("Select count(*) from coviddataset where zone=%s"%(zone))
    rec=cursor.fetchall()
    for i in rec:
        if i[0]==0:
            print('No Cases')
            return
    
    cummlist=[]
    
    time=[]
    for j in range(0,239):
        cursor.execute("select sum(cases) from zonewisedaywise where day<=%s and zone=%s"%(j,zone))
        rec=cursor.fetchall()
        time.append(int(j))
        for k in rec:
            cummlist.append(int(k[0]))
        
    plt.plot(time,cummlist)
    t="Cumulative Graph of cases for zone"+str(zone)
    plt.xlabel('Day')
    plt.ylabel('Number of cases')
    plt.title(t)
    plt.show()

def cummgraphofentirecity():#Cumulative graph of entire city
    import matplotlib.pyplot as plt
    import mysql.connector
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cummlist=[]
    gflist=[]
    time=[]
    for j in range(0,239):
        cursor.execute("select sum(cases) from zonewisedaywise where day<=%s "%(j))
        rec=cursor.fetchall()
        time.append(j)
        
        for k in rec:
            cummlist.append(int(k[0]))
    #for i in range(2,len(cummlist)):
       #try:
           #gf=int(cummlist[i]-cummlist[i-1])/int(cummlist[i-1]-cummlist[i-2])
           #gflist.append(gf)
       #except:
            #pass
   # print(cummlist)
    #print(gflist)
    #avggf=sum(gflist)/len(gflist)
   # print(avggf)
    plt.plot(time,cummlist)
    plt.xlabel("Day")
    plt.ylabel("Number of cases")
    plt.title("Cumulative cases of city")
    plt.show()        

def Deathratemap():
    # import package and making objects 
    import turtle
    import csv

    T=turtle.Turtle()
    T1=turtle.Turtle()
    T1.speed(0)
    T.speed(0)

    #initialized position
    T.penup()
    T.setpos(-400,-400)
    T.pendown()
    T.hideturtle()
    T1.hideturtle()

    #grid
    for i in range(4):
        T.forward(800)
        T.left(90)
    
    for i in range(10):
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        T.forward(40)
        T.right(90)

    for i in range(10):
        T.forward(40)
        T.right(90)
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
    
    T.left(90)
   
    def colour_grading():
        T.penup()
        T.setpos(-800,300)
        T.pendown()
        T.left(90)
    
        for i in range(30):
            T.pencolor("red")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write("Greater than 3% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
    
    
        for i in range(30):
            T.pencolor("orange")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        T.write(" Between 3% and 2%  ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,100)
        T.pendown()
   
        for i in range(30):
            T.pencolor("gold")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        
        T.write(" Between 2% and 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,0)
        T.pendown()
   
        for i in range(30):
            T.pencolor("lightgreen")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write(" 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        T.left(90)
   
        T.pencolor("black")    
     
    def red_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("red")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def orange_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("orange")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def yellow_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("yellow")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def green_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("lightgreen")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

        
    #Processing Data
    RL=[]
    OL=[]
    YL=[]
    GL=[]

    f1=open('zonewisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[12]) >= 3.0:
            for j in data2:
                if j[3]==i[0]:
                    RL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zonewisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)            
    for i in data1:
        if 3.0> float(i[12]) >= 2.0 :
            for j in data2:
                if j[3]==i[0]:
                    OL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zonewisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if 2.0> float(i[12]) > 0.0 :
            for j in data2:
                if j[3]==i[0]:
                    YL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()

    f1=open('zonewisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[12]) == 0.0   :
            for j in data2:
                if j[3]==i[0]:
                    GL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()
    

    for i in RL:
        red_zone(i)
    for i in OL:
        orange_zone(i)
    for i in YL:
        yellow_zone(i)
    for i in GL:
        green_zone(i)


    colour_grading()
    T.fillcolor('black')
    # writing x axis
    T.penup()
    T.setpos(-390,410)
    T.pendown()
    T.write("X",move=True,font=("Verdana", 20, "bold"))
    T.right(270)
    T.forward(200)
    T.showturtle()
 
    #writing Heading and  y axis
    T1.penup()
    T1.setpos(-100,450)
    T1.pendown()
    T1.pencolor("blue")
    T1.write("Death Rate Map ",move=True,font=("Verdana", 25, "bold"))
    T1.pencolor("black")

    T1.penup()
    T1.setpos(-425,360)
    T1.pendown()
    T1.write("Y",move=True,font=("Verdana", 20, "bold"))
    T1.penup()
    T1.setpos(-416,360)
    T1.pendown()
    T1.right(90)
    T1.forward(200)
    T1.showturtle()

def dailycasescity():
    
    import matplotlib.pyplot as plt
    import mysql.connector
    mycon=mysql.connector.connect(host="localhost",user="root",passwd="sql123",database="covid")
    cursor=mycon.cursor()
    cummlist=[]
    gflist=[]
    time=[]
    for j in range(0,239):
        cursor.execute("select sum(cases) from zonewisedaywise where day=%s "%(j))
        rec=cursor.fetchall()
        time.append(j)
        
        for k in rec:
            cummlist.append(int(k[0]))
   
    plt.plot(time,cummlist)
    plt.xlabel("Day")
    plt.ylabel("Number of cases")
    plt.title("Daily cases  of city")
    plt.show()

def Diabetes_covidmap():
    # import package and making objects 
    import turtle
    import csv

    T=turtle.Turtle()
    T1=turtle.Turtle()
    T1.speed(0)
    T.speed(0)

    #initialized position
    T.penup()
    T.setpos(-400,-400)
    T.pendown()
    T.hideturtle()
    T1.hideturtle()

    #grid
    for i in range(4):
        T.forward(800)
        T.left(90)
    
    for i in range(10):
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        T.forward(40)
        T.right(90)

    for i in range(10):
        T.forward(40)
        T.right(90)
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
    
    T.left(90)
   
    def colour_grading():
        T.penup()
        T.setpos(-800,300)
        T.pendown()
        T.left(90)
    
        for i in range(30):
            T.pencolor("red")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write("Greater than 55% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
    
    
        for i in range(30):
            T.pencolor("orange")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        T.write(" Between 55% and 50%  ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,100)
        T.pendown()
   
        for i in range(30):
            T.pencolor("gold")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        
        T.write(" Between 50% and 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,0)
        T.pendown()
   
        for i in range(30):
            T.pencolor("lightgreen")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write(" 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        T.left(90)
   
        T.pencolor("black")    
     
    def red_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("red")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def orange_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("orange")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def yellow_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("yellow")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def green_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("lightgreen")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

        
    #Processing Data
    RL=[]
    OL=[]
    YL=[]
    GL=[]

    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[19]) >= 55.0:
            for j in data2:
                if j[3]==i[0]:
                    RL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)            
    for i in data1:
        if 55.0> float(i[19]) >= 50.0 :
            for j in data2:
                if j[3]==i[0]:
                    OL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if 50.0> float(i[19]) > 0.0 :
            for j in data2:
                if j[3]==i[0]:
                    YL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()

    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[19]) == 0.0   :
            for j in data2:
                if j[3]==i[0]:
                    GL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()
    print(len(RL)+len(YL)+len(OL)+len(GL))

    for i in RL:
        red_zone(i)
    for i in OL:
        orange_zone(i)
    for i in YL:
        yellow_zone(i)
    for i in GL:
        green_zone(i)


    colour_grading()
    T.fillcolor('black')
    # writing x axis
    T.penup()
    T.setpos(-390,410)
    T.pendown()
    T.write("X",move=True,font=("Verdana", 20, "bold"))
    T.right(270)
    T.forward(200)
    T.showturtle()
 
    #writing Heading and  y axis
    T1.penup()
    T1.setpos(-300,450)
    T1.pendown()
    T1.pencolor("blue")
    T1.write("Covid patients with Diabetes ",move=True,font=("Verdana", 25, "bold"))
    T1.pencolor("black")

    T1.penup()
    T1.setpos(-425,360)
    T1.pendown()
    T1.write("Y",move=True,font=("Verdana", 20, "bold"))
    T1.penup()
    T1.setpos(-416,360)
    T1.pendown()
    T1.right(90)
    T1.forward(200)
    T1.showturtle()
    
def Respiratory_covidmap():
    # import package and making objects 
    import turtle
    import csv

    T=turtle.Turtle()
    T1=turtle.Turtle()
    T1.speed(0)
    T.speed(0)

    #initialized position
    T.penup()
    T.setpos(-400,-400)
    T.pendown()
    T.hideturtle()
    T1.hideturtle()

    #grid
    for i in range(4):
        T.forward(800)
        T.left(90)
    
    for i in range(10):
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        T.forward(40)
        T.right(90)

    for i in range(10):
        T.forward(40)
        T.right(90)
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
    
    T.left(90)
   
    def colour_grading():
        T.penup()
        T.setpos(-800,300)
        T.pendown()
        T.left(90)
    
        for i in range(30):
            T.pencolor("red")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write("Greater than 30% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
    
    
        for i in range(30):
            T.pencolor("orange")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        T.write(" Between 30% and 25%  ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,100)
        T.pendown()
   
        for i in range(30):
            T.pencolor("gold")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        
        T.write(" Between 25% and 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,0)
        T.pendown()
   
        for i in range(30):
            T.pencolor("lightgreen")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write(" 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        T.left(90)
   
        T.pencolor("black")    
     
    def red_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("red")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def orange_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("orange")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def yellow_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("yellow")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def green_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("lightgreen")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

        
    #Processing Data
    RL=[]
    OL=[]
    YL=[]
    GL=[]

    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[20]) >= 30.0:
            for j in data2:
                if j[3]==i[0]:
                    RL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)            
    for i in data1:
        if 30.0> float(i[20]) >= 25.0 :
            for j in data2:
                if j[3]==i[0]:
                    OL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if 25.0> float(i[20]) > 0.0 :
            for j in data2:
                if j[3]==i[0]:
                    YL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()

    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[20]) == 0.0   :
            for j in data2:
                if j[3]==i[0]:
                    GL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()
    print(len(RL)+len(YL)+len(OL)+len(GL))

    for i in RL:
        red_zone(i)
    for i in OL:
        orange_zone(i)
    for i in YL:
        yellow_zone(i)
    for i in GL:
        green_zone(i)


    colour_grading()
    T.fillcolor('black')
    # writing x axis
    T.penup()
    T.setpos(-390,410)
    T.pendown()
    T.write("X",move=True,font=("Verdana", 20, "bold"))
    T.right(270)
    T.forward(200)
    T.showturtle()
 
    #writing Heading and  y axis
    T1.penup()
    T1.setpos(-300,450)
    T1.pendown()
    T1.pencolor("blue")
    T1.write("Covid patients with Respiratory Disorder  ",move=True,font=("Verdana", 25, "bold"))
    T1.pencolor("black")

    T1.penup()
    T1.setpos(-425,360)
    T1.pendown()
    T1.write("Y",move=True,font=("Verdana", 20, "bold"))
    T1.penup()
    T1.setpos(-416,360)
    T1.pendown()
    T1.right(90)
    T1.forward(200)
    T1.showturtle()

def Bp_covidmap():
    # import package and making objects 
    import turtle
    import csv

    T=turtle.Turtle()
    T1=turtle.Turtle()
    T1.speed(0)
    T.speed(0)

    #initialized position
    T.penup()
    T.setpos(-400,-400)
    T.pendown()
    T.hideturtle()
    T1.hideturtle()

    #grid
    for i in range(4):
        T.forward(800)
        T.left(90)
    
    for i in range(10):
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        T.forward(40)
        T.right(90)

    for i in range(10):
        T.forward(40)
        T.right(90)
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
    
    T.left(90)
   
    def colour_grading():
        T.penup()
        T.setpos(-800,300)
        T.pendown()
        T.left(90)
    
        for i in range(30):
            T.pencolor("red")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write("Greater than 35% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()

        for i in range(30):
            T.pencolor("orange")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        T.write(" Between 35% and 30%  ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,100)
        T.pendown()
   
        for i in range(30):
            T.pencolor("gold")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        
        T.write(" Between 30% and 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,0)
        T.pendown()
   
        for i in range(30):
            T.pencolor("lightgreen")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write(" 0% ",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        T.left(90)
   
        T.pencolor("black")    
     
    def red_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("red")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def orange_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("orange")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def yellow_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("yellow")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def green_zone(A):
        x=A[0]
        y=A[1]
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("lightgreen")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

        
    #Processing Data
    RL=[]
    OL=[]
    YL=[]
    GL=[]

    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[21]) >= 35.0:
            for j in data2:
                if j[3]==i[0]:
                    RL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)            
    for i in data1:
        if 35.0> float(i[21]) >= 30.0 :
            for j in data2:
                if j[3]==i[0]:
                    OL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()


    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if 30.0> float(i[21]) > 0.0 :
            for j in data2:
                if j[3]==i[0]:
                    YL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()

    f1=open('zone_wisereport.csv','r')
    f2=open('Populationnumbered.csv','r')
    data1=csv.reader(f1)
    data2=csv.reader(f2)
    next(data1)
    next(data2)
    for i in data1:
        if float(i[21]) == 0.0   :
            for j in data2:
                if j[3]==i[0]:
                    GL.append((int(j[0]),int(j[1])))
                    break
    f1.close()
    f2.close()
    print(len(RL)+len(YL)+len(OL)+len(GL))

    for i in RL:
        red_zone(i)
    for i in OL:
        orange_zone(i)
    for i in YL:
        yellow_zone(i)
    for i in GL:
        green_zone(i)


    colour_grading()
    T.fillcolor('black')
    # writing x axis
    T.penup()
    T.setpos(-390,410)
    T.pendown()
    T.write("X",move=True,font=("Verdana", 20, "bold"))
    T.right(270)
    T.forward(200)
    T.showturtle()
 
    #writing Heading and  y axis
    T1.penup()
    T1.setpos(-300,450)
    T1.pendown()
    T1.pencolor("blue")
    T1.write("Covid patients with Abnormal BP  ",move=True,font=("Verdana", 25, "bold"))
    T1.pencolor("black")

    T1.penup()
    T1.setpos(-425,360)
    T1.pendown()
    T1.write("Y",move=True,font=("Verdana", 20, "bold"))
    T1.penup()
    T1.setpos(-416,360)
    T1.pendown()
    T1.right(90)
    T1.forward(200)
    T1.showturtle()
 
def alter_zonewisereport():
    import csv
    f1=open("zonewisereport.csv",'r')
    data=csv.reader(f1)
    f2=open("zone_wisereport.csv",'w',newline='')
    write=csv.writer(f2, delimiter=',')
    count=0
    for i in data:
        if count==0:
            write.writerow(i+["Percentage of cases with Diabetes","Percentage of cases with  respiratory disorders","Percentage of cases with abnormal BP"])
            count+=1
        else:
            try:
                Dp=round((int(i[7])/int(i[2]))*100,2)
            except ZeroDivisionError:
                Dp=0
            try:
                Rp=round((int(i[8])/int(i[2]))*100,2)
            except ZeroDivisionError:
                Rp=0
            try:
                Bp=round((int(i[9])/int(i[2]))*100,2)
            except ZeroDivisionError:
                Bp=0
            write.writerow(i+[Dp,Rp,Bp])
 def vaccine_priority_map():
    # import package and making objects 
    import turtle
    import csv

    T=turtle.Turtle()
    T1=turtle.Turtle()
    T1.speed(0)
    T.speed(0)

    #initialized position
    T.penup()
    T.setpos(-400,-400)
    T.pendown()
    T.hideturtle()
    T1.hideturtle()

    #grid
    for i in range(4):
        T.forward(800)
        T.left(90)
    
    for i in range(10):
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
        T.forward(40)
        T.right(90)

    for i in range(10):
        T.forward(40)
        T.right(90)
        T.forward(800)
        T.left(90)
        T.forward(40)
        T.left(90)
        T.forward(800)
        T.right(90)
    
    T.left(90)
   
    def colour_grading():
        T.penup()
        T.setpos(-800,300)
        T.pendown()
        T.left(90)
    
        for i in range(30):
            T.pencolor("red")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write("Top Priority",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
    
    
        for i in range(30):
            T.pencolor("orange")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        T.write("Moderate Priority",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,100)
        T.pendown()
   
        for i in range(30):
            T.pencolor("gold")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)
        
        
        T.write("Least Priority",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,0)
        T.pendown()
   
        for i in range(30):
            T.pencolor("lightgreen")
            T.forward(20)
            T.right(90)
            T.forward(1)
            T.right(90)
            T.forward(20)
            T.left(180)

        T.write("No Priority",move=True,font=("Verdana", 20, "normal"))
        T.penup()
        T.setpos(-800,200)
        T.pendown()
        T.left(90)
   
        T.pencolor("black")    
     
    def red_zone(A):
        x=int(A[0])
        y=int(A[1])
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("red")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def orange_zone(A):
        x=int(A[0])
        y=int(A[1])
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("orange")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def yellow_zone(A):
        x=int(A[0])
        y=int(A[1])
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("yellow")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

    def green_zone(A):
        x=int(A[0])
        y=int(A[1])
        x=40*x
        y=40*y
        T.penup()
        T.setpos(-400+x,400-y)
        T.pendown()
        T.fillcolor("lightgreen")
        T.begin_fill()
        for i in range(4):
            T.forward(40)
            T.left(90)
        T.end_fill()

        
    #Processing Data
    RL=[]
    OL=[]
    YL=[]
    GL=[]

    f=open("vaccine_priority.txt",'r')
    data=f.readlines()
    for i in data:
        i=i.split()
        if int(i[1]) >= 3000:
            RL.append(i[0].split(','))
            
        elif 3000> int(i[1]) >=1000:
            OL.append(i[0].split(','))
            
        elif 1000> int(i[1]) >0:
            YL.append(i[0].split(','))
            
        elif int(i[1]) == 0:
            GL.append(i[0].split(','))
    
    f.close()
    print("Top Priority ZONES : ",RL)


    for i in RL:
        red_zone(i)
    for i in OL:
        orange_zone(i)
    for i in YL:
        yellow_zone(i)
    for i in GL:
        green_zone(i)


    colour_grading()
    T.fillcolor('black')
    # writing x axis
    T.penup()
    T.setpos(-390,410)
    T.pendown()
    T.write("X",move=True,font=("Verdana", 20, "bold"))
    T.right(270)
    T.forward(200)
    T.showturtle()
 
    #writing Heading and  y axis
    T1.penup()
    T1.setpos(-300,450)
    T1.pendown()
    T1.pencolor("blue")
    T1.write("Covid Vaccine Priority ",move=True,font=("Verdana", 25, "bold"))
    T1.pencolor("black")

    T1.penup()
    T1.setpos(-425,360)
    T1.pendown()
    T1.write("Y",move=True,font=("Verdana", 20, "bold"))
    T1.penup()
    T1.setpos(-416,360)
    T1.pendown()
    T1.right(90)
    T1.forward(200)
    T1.showturtle()


def main():
    
    while True:
         print("COVID-19 DATA ANALYSIS")
         print("Main menu")
         print("1.Intensity maps")
         print("2.Zone wise plots")
         print("3.Overall Plots for the city")
         print("4.Exit")
        try:
            
             ch=int(input("Enter a choice"))
        except:
            print("An Error has occured")
            break
        if ch==1:
            intensitymaps()
        elif ch==2:
            zonewiseplots()
        elif ch==3:
            overallplots()
        elif ch==4:
            break
        else:
            print("Invalid choice")


def intensitymaps():
    
    while True:
        print("Types of intensity maps")
        print("1.Covid 19 Intensity map")
        print("2.Death rate map")
        print("3.Covid patients with diabetes")
        print("4.Covid patients with abnormal blood pressure")
        print("5.Covid patients with respiratory illness")
        print("6.Exit")
        try:
            ch=int(input("Enter Choice"))
        except:
            print("An error has occured")
            break
        if ch==1:
            intensitymap()
        elif ch==2:
            Deathratemap()
        elif ch==3:
             Diabetes_covidmap()
        elif ch==4:
            Bp_covidmap()
        elif ch==5:
            Respiratory_covidmap()
        elif ch==6:
            break
        else:
            print("Invalid choice")
def zonewiseplots():
   
    while True:
        print("Types of zonewise plots")
        print("1.Cumulative graph of a zone")
        print("2.Daily graph of a zone")
        print("3.Analysis of cases with comorbidities of a zone")
        print("4.Analysis of deaths with comorbidities of a zone")
        print("5.Exit")
        try:
            
           ch=int(input("Enter a choice"))
        except:
            print("An error has occured")
            break
        if ch==1:
            try:
               zone=int(input("Enter a zone"))
            except:
                 print("An error has occured")
                 break
                
            if zone<1 or zone>400:
                print("Zone does not exist")
            elif zone>=1 and zone<=400:
                 graphcumm(zone)
        elif ch==2:
            try:
               zone=int(input("Enter a zone"))
            except:
                 print("An error has occured")
                 break
             
            if zone<1 or zone>400:
                
                print("Zone does not exist")
            elif zone>=1 and zone<=400:
                showgraphbasedoncasesreportedperday(zone)
        elif ch==3:
            try:
              zone=int(input("Enter a zone"))
             
            except:
                 print("An error has occured")
                 break
            if zone<1 or zone>400:
                print("Zone does not exist")
            elif zone>=1 and zone<=400:
                venncases(zone)
        elif ch==4:
            try:
               zone=int(input("Enter a zone"))
             except:
                 print("An error has occured")
                 break
            
            if zone<1 or zone>400:
                print("Zone does not exist")
            elif zone>=1 and zone<=400:
                venndeaths(zone)
        elif ch==5:
            break
        else:
            print("Invalid choice")
            
def overallplots():
   
    while True:
         print("Overall plots for city")
         print("1.Cumulative graph of the city")
         print("2.Daily graph of the city")
         print("3.Analysis of cases with comorbidities of the city")
         print("4.Analysis of deaths with comorbidities of the city")
         print("5.Analysis of cases and deaths of city based on age")
         print("6.Vaccine priority map")
         print("7.Exit")
        try:
            ch=int(input("Enter your choice"))
        except:
            print("An error has occured")
            break
        if ch==1:
            cummgraphofentirecity()
        elif ch==2:
            dailycasescity()
        elif ch==3:
            venncasescity()
        elif ch==4:
            venndeathscity()
        elif ch==5:
             Basic_city_age()
        elif ch==6:
            vaccine_priority_map()
        elif ch==7:
            break
        else:
            print("Invalid choice")
        
            
#sqlpass = input("Enter SQL Password ")
numberlocations()
pushintosql()
zonewisedaywise()
generatereportfor400zones()
