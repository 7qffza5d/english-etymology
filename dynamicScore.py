import pandas as pd

INF = 2147483647

def floydWarshall(dist):
    V = len(dist)
    #intermediate node
    for k in range(V):
        #source node
        for i in range(V):
            #destination node
            for j in range(V):
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist

df = pd.read_excel('rawResult.xlsx')
dist = [
    [0,0.8,0.9,1,1,1],
    [0.8,0,0.6,1,0.4,0.3],
    [0.9,0.6,0,0.2,0.5,1],
    [1,1,0.2,0,1,1],
    [1,0.4,0.5,1,0,1],
    [1,0.3,1,1,1,0]
]
dis = floydWarshall(dist)
languages = ["Brittonic","Latin","Old English","Old Norse","Middle French","Greek"]
sum = 0

for i in range(len(df)):
    a = languages.index(df.loc[i]['Epitran-PanPhon estimated closest language'])
    b = languages.index(df.loc[i]['Actual Etymology'])
    sum += max(1 - dis[a][b],0)

print("Dynamic Score =",sum)
print("Dynamic Score Percentage =",sum / len(df))