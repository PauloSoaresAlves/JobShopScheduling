from itertools import product
from mip import Model, BINARY

def load( fileName: str):
        file = open(fileName, "r")
        J, M = list(map(int,file.readline().split()))
        
        T = [[0 for _ in range(M)] for _ in range(J)]
        O = [[0 for _ in range(M)] for _ in range(J)]
        
        for i in range(J):
            line = list(map(int, file.readline().split()))
            lastMachine = -1
            for j in range(M * 2):
                if j % 2 == 0:
                    O[i][j // 2] = line[j]
                    lastMachine = line[j]
                else:
                    T[i][lastMachine] = line[j]
        
        file.close()
        
        return J, M, T, O


n, m, times, machines = load("job-shop.txt")

M = sum(times[i][j] for i in range(n) for j in range(m))

model = Model('JSSP')

c = model.add_var(name="C")
x = [[model.add_var(name='x({},{})'.format(j+1, i+1))
      for i in range(m)] for j in range(n)]
y = [[[model.add_var(var_type=BINARY, name='y({},{},{})'.format(j+1, k+1, i+1))
       for i in range(m)] for k in range(n)] for j in range(n)]

model.objective = c

for (j, i) in product(range(n), range(1, m)):
    model += x[j][machines[j][i]] - x[j][machines[j][i-1]] >= \
        times[j][machines[j][i-1]]

for (j, k) in product(range(n), range(n)):
    if k != j:
        for i in range(m):
            model += x[j][i] - x[k][i] + M*y[j][k][i] >= times[k][i]
            model += -x[j][i] + x[k][i] - M*y[j][k][i] >= times[j][i] - M

for j in range(n):
    model += c - x[j][machines[j][m - 1]] >= times[j][machines[j][m - 1]]

model.optimize()

print("Completion time: ", c.x)
for (j, i) in product(range(n), range(m)):
    print("task %d starts on machine %d at time %g " % (j+1, i+1, x[j][i].x))