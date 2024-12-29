from typing import List
import random, copy

class InstanceJSS():
    def __init__(self,taskSeq: List[List[List[int]]], T: List[List[int]]):
        self.taskSeq = taskSeq
        self.apt = 0
        self.T = T
        
    def __str__(self):
        resp = ""
        for m in range(len(self.taskSeq)):
            resp += f"Machine {m}: \n"
            for task in self.taskSeq[m]:
                resp += f" {task[0]}: [{task[1]} - {task[2]}] "
            resp += "\n"
        resp += "\nFitness: " + str(self.apt)
            
        return resp
    
    def rescheduleSolution(self, m: int):  #O(n^2)
        for k in range(len(self.taskSeq[m])):
            if k == 0:
                task = self.taskSeq[m][k]
                self.taskSeq[m][k][2] = task[1] + self.T[task[0]][m]
            else:
                currentTask = self.taskSeq[m][k]
                lastTask = self.taskSeq[m][k - 1]
                if currentTask[1] < lastTask[2]:
                    self.taskSeq[m][k][1] = lastTask[2]
                    self.taskSeq[m][k][2] = lastTask[2] + self.T[currentTask[0]][m]
                else:
                    self.taskSeq[m][k][2] = currentTask[1] + self.T[currentTask[0]][m]
                    
        
class ContextJSS():
    def __init__(self):
        #Numero de Jobs
        self.J : int = 0
        #Numero de Máquinas
        self.M : int = 0
        #Tempos de Processamento
        self.T : List[List[int]] = []
        #Ordem de Processamento
        self.O : List[List[int]] = []
        
        self.maxTimeUnits = 0
        
        self.mutationRate = 0.3
        
    def load(self, fileName: str):
        file = open(fileName, "r")
        self.J, self.M = list(map(int,file.readline().split()))
        
        self.T = [[0 for _ in range(self.M)] for _ in range(self.J)]
        self.O = [[0 for _ in range(self.M)] for _ in range(self.J)]
        
        for i in range(self.J):
            line = list(map(int, file.readline().split()))
            lastMachine = -1
            for j in range(self.M * 2):
                if j % 2 == 0:
                    self.O[i][j // 2] = line[j]
                    lastMachine = line[j]
                else:
                    self.T[i][lastMachine] = line[j]
        
        file.close()
        
        self.maxTimeUnits = sum(self.T[i][j] for i in range(self.J) for j in range(self.M))
        
    def __str__(self):
        resp = f"Number of Jobs: {self.J} x Number of Machines: {self.M}\n\n"
        resp += "Processing Times:\n"
        resp += "Machine: " + str(" ".join([str(i) for i in range(self.M)])) + "\n"
        for i in range(self.J):
            resp += f"Job {i}: {self.T[i]}\n"
        resp += "Order of Processing:\n"
        resp += "\nMachine: " + str(" ".join([str(i) for i in range(self.M)])) + "\n"
        for i in range(self.J):
            resp += f"Job {i}: {self.O[i]}\n"
        return resp
    
    def generateSolution(self) -> InstanceJSS:
        tasks = [i for i in range(self.J * self.M)]
        
        taskSeq = [[] for _ in range(self.M)]
        
        while tasks:
            task = random.choice(tasks)
            tasks.remove(task)
            job = task // self.M
            machine = task % self.M
            if not taskSeq[machine]:
                task = [job, 0, self.T[job][machine]]
            else:
                lastTask = taskSeq[machine][-1]
                task = [job, lastTask[2], lastTask[2] + self.T[job][machine]]
            taskSeq[machine].append(task)
                
        instance = InstanceJSS(taskSeq, self.T)
        return instance
    
    def evaluateInstance(self,instance: 'InstanceJSS'):
        penalty = 0
        
        tasks = []
        
        makespan = 0
        
        #Pra cada job, verifica pega a sua ordem de processamento e:
        # 1. Verifica se a ordem de processamento está de acordo com O[j]
        # 2. Verifica se o job está sendo processado em 2 máquinas ao mesmo tempo
        for j in range(self.J):
            for m in range(self.M):
                for i in range(self.J):
                    makespan = max(makespan, instance.taskSeq[m][i][2])
                    if instance.taskSeq[m][i][0] == j:
                        tasks.append({"t": instance.taskSeq[m][i], "m": m})
                        break
            tasks.sort(key = lambda x: x["t"][1])
            outOfOrder = False
            order = 0
            while tasks:
                task = tasks.pop(0)
                if not outOfOrder:
                    if self.O[j][order] == task["m"]:
                        order += 1
                    else:
                        outOfOrder = True
                        penalty += 100
                for i in range(len(tasks)):
                    if task["t"][2] > tasks[i]["t"][1]:
                        penalty += task["t"][2] - tasks[i]["t"][1]
                        break
                
        instance.apt = makespan + (penalty*10)

    
    def crossover(self,population: List[InstanceJSS],):
        population.sort(key = lambda x: x.apt)
        max = sum(1/x.apt for x in population)
        newPopulation = []
        while population:
            instance1 = population.pop(0)
            max -= instance1.apt
            instance2 = None
            current = 0
            pick = random.uniform(0,max)
            for i in range(len(population)):
                current += 1/population[i].apt
                if current >= pick:
                    instance2 = population.pop(i)
                    max -= instance2.apt
                    break
            newInstance1 = self.crossoverInstance(instance1,instance2)
            newInstance2 = self.crossoverInstance(instance2,instance1)
            
            newPopulation.append(newInstance1)
            newPopulation.append(newInstance2)
            newPopulation.append(instance1)
            newPopulation.append(instance2)
            
        return newPopulation
    
    def crossoverInstance(self,instance1: 'InstanceJSS',instance2: 'InstanceJSS') -> 'InstanceJSS':
        newGene = []
        for i in range(len(instance1.taskSeq)):
            if i % 2 == 0:
                newGene.append(copy.deepcopy(instance1.taskSeq[i]))
            else:
                newGene.append(copy.deepcopy(instance2.taskSeq[i]))
        instance = InstanceJSS(newGene, self.T)
        self.mutate(instance)
        return instance
        
    def mutate(self,instance: 'InstanceJSS'):
        if random.random() < self.mutationRate:
            mutation = random.randint(0,1)
            m = random.randint(0,self.M - 1)
            if mutation == 0:
                i = random.randint(0,len(instance.taskSeq[m]) - 1)
                j = random.randint(0,len(instance.taskSeq[m]) - 1)
                
                move = SwapMove(i,j,m)
                
                if move.canBeApplied(self,instance):
                    move.apply(self,instance)
                    
            else:
                i = random.randint(0,len(instance.taskSeq[m]) - 1)
                duration = self.T[instance.taskSeq[m][i][0]][m]
                t = instance.taskSeq[m][i][1] + random.randint(-duration,duration)
                
                move = RealocMove(i,t,m)
                
                if move.canBeApplied(self,instance):
                    move.apply(self,instance)
                    
            instance.rescheduleSolution(m)
            
    def selectNewPopulation(self, population: List[InstanceJSS]):
        newPopulation = []
        while population:
            instance1 = random.choice(population)
            population.remove(instance1)
            instance2 = random.choice(population)
            population.remove(instance2)
            if instance1.apt < instance2.apt:
                newPopulation.append(instance1)
            else:
                newPopulation.append(instance2)
        return newPopulation

class Move():
    def apply(self, problemCtx: 'ContextJSS', sol: InstanceJSS):
        pass
    def canBeApplied(self, problemCtx: 'ContextJSS', sol: InstanceJSS):
        pass
    def eq(self, problemCtx: 'ContextJSS', m2: 'Move'):
        pass

#Movimento de Troca I por J
class SwapMove(Move):
    def __init__(self, i: int, j: int, m: int):
        self.i = i
        self.j = j
        self.m = m
    def __str__(self):
        return f"SwapMove({self.i},{self.j},{self.m})"
    def apply(self, problemCtx: 'ContextJSS', sol: InstanceJSS):   
        TaskI = sol.taskSeq[self.m][self.i]
        TaskJ = sol.taskSeq[self.m][self.j]
        
        sol.taskSeq[self.m][self.i] = [TaskJ[0], TaskI[1], TaskJ[2]]
        sol.taskSeq[self.m][self.j] = [TaskI[0], TaskJ[1], TaskI[2]]
    def canBeApplied(self, problemCtx: 'ContextJSS', sol: 'InstanceJSS'):
        jobI = sol.taskSeq[self.m][self.i][0]
        jobJ = sol.taskSeq[self.m][self.j][0]
        
        iDuration = problemCtx.T[jobI][self.m]
        jDuration = problemCtx.T[jobJ][self.m]
        
        iStartingTime = sol.taskSeq[self.m][self.i][1]
        jStartingTime = sol.taskSeq[self.m][self.j][1]
        
        if iStartingTime + jDuration > problemCtx.maxTimeUnits or jStartingTime + iDuration > problemCtx.maxTimeUnits:
            return False
        return True

#Movimento de realocação, move o tempo inicial de uma tarefa i para um tempo t
#Verifica quem ocupa o tempo t e insere a tarefa i antes no taskSeq
class RealocMove(Move):
    def __init__(self, i: int, t: int, m: int):
        self.i = i
        self.t = t
        self.m = m
    def __str__(self):
        return f"RealocMove({self.i},{self.t},{self.m})"
    def apply(self, problemCtx: 'ContextJSS', sol: InstanceJSS):
        task = sol.taskSeq[self.m].pop(self.i)
        NewTask = [task[0], self.t, task[2]]
        taskBefore = 0
        while taskBefore < len(sol.taskSeq[self.m]) and sol.taskSeq[self.m][taskBefore][2] <= task[1]:
            taskBefore += 1
        
        if taskBefore == len(sol.taskSeq[self.m]):
            sol.taskSeq[self.m].append(NewTask)
        else:
            sol.taskSeq[self.m].insert(taskBefore, NewTask)         
    def canBeApplied(self, problemCtx, sol: 'InstanceJSS'):
        maxTimeUnits = problemCtx.maxTimeUnits
        task = sol.taskSeq[self.m][self.i]
        return self.t + problemCtx.T[task[0]][self.m] <= maxTimeUnits and self.t >= 0
           

        
        




context = ContextJSS()
context.load("job-shop.txt")

population : List[InstanceJSS] = []

bestInstance = None

populationSize = 100

for i in range(populationSize):
    population.append(context.generateSolution())

for i in range(populationSize):
    context.evaluateInstance(population[i])

bestInstance = population[0]
        

nGenerations = 10000
currentIteration = 0

population.sort(key = lambda x: x.apt)

while currentIteration < nGenerations:
    currentIteration += 1
    
    population = context.crossover(population)
    
    print(f"\nGeneration {currentIteration}")
    
    for i in range(populationSize*2):
        context.evaluateInstance(population[i])
        
    population.sort(key = lambda x: x.apt)
    population = context.selectNewPopulation(population)
    
    print("Best Fitness: ", population[0].apt)
    print("AVG Fitness: ", sum(x.apt for x in population)/populationSize)
    
    if population[0].apt < bestInstance.apt:
        bestInstance = population[0]

print(bestInstance)
