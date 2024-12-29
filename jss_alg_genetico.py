from typing import List
import multiprocessing, time, random

#Classe que representa um indivíduo da população
class InstanceJSS():
    def __init__(self,solution: List[int]):
        self.solution = solution
        self.apt = 0
        
    def __str__(self):
        return f"Solution: {self.solution} - APT: {self.apt}"
    
    def mutate(self):
        i = random.randint(0, len(self.solution) - 1)
        j = random.randint(0, len(self.solution) - 1)
        while self.solution[i] == self.solution[j]:
            j = random.randint(0, len(self.solution) - 1)
        self.solution[i], self.solution[j] = self.solution[j], self.solution[i]
                    
#Classe geral, que representa o contexto do problema      
class ContextJSS():
    def __init__(self, mutationRate: 0.1, populationSize: 10):
        #Numero de Jobs
        self.J : int = 0
        #Numero de Máquinas
        self.M : int = 0
        #Tempos de Processamento
        self.T : List[List[int]] = []
        #Ordem de Processamento
        self.O : List[List[int]] = []
        #Taxa de Mutação
        self.mutationRate = mutationRate
        #Tamanho da População
        self.populationSize = populationSize
        
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
    
    #Cria a população inicial
    #Cada indivídio é um vetor de tamanho J*M, onde cada job é repetido M vezes, representando a ordem lógica de execução
    def createInitialPopulation(self):
        population = []
        for _ in range(self.populationSize):
            newSolution = [i for i in range(0, self.J) for _ in range(self.M)]
            random.shuffle(newSolution)
            population.append(InstanceJSS(newSolution))
    
        return population
    
    def evaluateSolution(self, instance: InstanceJSS):
        solution = instance.solution
        
        #Guarda informações sobre o tempo atual de cada máquia e de cada job
        currentOperation = [0 for _ in range(self.J)]
        machineTime = [0 for _ in range(self.M)]
        jobTime = [0 for _ in range(self.J)]
        
        maxTime = 0
        
        for i in range(len(solution)):
            job = solution[i]
            machine = self.O[job][currentOperation[job]]
            time = self.T[job][machine]
            
            if machineTime[machine] > jobTime[job]:
                machineTime[machine] += time
                jobTime[job] = machineTime[machine]
            else:
                jobTime[job] += time
                machineTime[machine] = jobTime[job]
                
                
            maxTime = max(maxTime, machineTime[machine])
            
            currentOperation[job] += 1
            
        instance.apt = maxTime
        
    def printDetailedSolution(self, instance: InstanceJSS):
        solution = instance.solution
        currentOperation = [0 for _ in range(self.J)]
        machineTime = [0 for _ in range(self.M)]
        jobTime = [0 for _ in range(self.J)]
        
        
        #Guarda a sequencia de tarefas em cada maquina
        taskSeq = [[] for _ in range(self.M)]
        
        for i in range(len(solution)):
            job = solution[i]
            machine = self.O[job][currentOperation[job]]
            time = self.T[job][machine]
            
            if machineTime[machine] > jobTime[job]:
                taskSeq[machine].append([job, machineTime[machine], machineTime[machine] + time])
                
                machineTime[machine] += time
                jobTime[job] = machineTime[machine]
            else:
                taskSeq[machine].append([job, jobTime[job], jobTime[job] + time])
                
                jobTime[job] += time
                machineTime[machine] = jobTime[job]
            
            currentOperation[job] += 1
        
        print(f"\n{instance}")
        for m in range(self.M):
            print(f"\nMachine {m}: ")
            for task in taskSeq[m]:
                print(f"Job {task[0]}: [{task[1]} - {task[2]}]", end = " ")
        print()
    
    #Crossover utilizando Precedence Preservative Crossover (PPX)
    def crossoverInstances(self, instance1: InstanceJSS, instance2: InstanceJSS):
        newSolution = []
        instance1Cpy = instance1.solution.copy()
        instance2Cpy = instance2.solution.copy()
        crossGene = [random.randint(0,1) for _ in range(len(instance1Cpy))]
        
        for i in range(len(crossGene)):
            if crossGene[i] == 0:
                gene = instance1Cpy.pop(0)
                newSolution.append(gene)
                instance2Cpy.remove(gene)
            else:
                gene = instance2Cpy.pop(0)
                newSolution.append(gene)
                instance1Cpy.remove(gene)
                
        childInstance = InstanceJSS(newSolution)
        
        if random.uniform(0,1) < self.mutationRate:
            childInstance.mutate()
        
        return childInstance
    
    #Crossover da população, sempre gera o dobro de indivíduos  
    def crossover(self, population: List[InstanceJSS]):
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
            
            newInstances = [self.crossoverInstances(instance1, instance2) for _ in range(2)]
            newPopulation.extend(newInstances)
            newPopulation.append(instance1)
            newPopulation.append(instance2)
            
        return newPopulation
    
    #Seleção de indivíduos a partir de torneio
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
    
    def runGA(self, generationLimit: int, return_dict: dict):
        population : List[InstanceJSS] = []

        population = context.createInitialPopulation()

        for instance in population:
            context.evaluateSolution(instance)
            
        population.sort(key = lambda x: x.apt)
        bestInstance = population[0]
        worstInstance = population[-1]

        nGenerations = float("inf") if generationLimit == -1 else generationLimit
            
        currentIteration = 0

        while currentIteration < nGenerations:
            currentIteration += 1
            
            population = context.crossover(population)
            
            print(f"\nGeneration {currentIteration}")
            
            for i in range(populationSize*2):
                context.evaluateSolution(population[i])
                
            population = context.selectNewPopulation(population)
            population.sort(key = lambda x: x.apt)
            
            print("Best Fitness: ", population[0].apt)
            print("AVG Fitness: ", sum(x.apt for x in population)/populationSize)
            
            if population[0].apt < bestInstance.apt:
                bestInstance = population[0]
            if population[-1].apt > worstInstance.apt:
                worstInstance = population[-1]
                
            return_dict["best"] = bestInstance
            return_dict["worst"] = worstInstance
            
        
                     
    
mutationRate = 0.15
populationSize = 20

context = ContextJSS(mutationRate, populationSize)

context.load("job-shop.txt")

time_limit = int(input("Tempo limite em segundos: (-1 para sem limite)\n"))
generationLimit = int(input("Limite de gerações: (-1 para sem limite)\n"))

#Overkill para garantir que seja feito por multiprocessamento
manager = multiprocessing.Manager()
return_dict = manager.dict()

p = multiprocessing.Process(target=context.runGA, name="GA", args=(generationLimit,return_dict))
p.start()

if time_limit != -1:
    p.join(time_limit)
else:
    p.join()

if p.is_alive():
    p.terminate()
    
bestInstance, worstInstance = return_dict["best"], return_dict["worst"]

print("\nBest Solution: ")  
context.printDetailedSolution(bestInstance)

print("\nWorse Solution: ")
context.printDetailedSolution(worstInstance)
