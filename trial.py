import pandas
import matplotlib
df =pandas.DataFrame([1,2,3,4],columns=['a'])
print(df.pct_change().mean())

