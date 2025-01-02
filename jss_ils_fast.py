import time
from typing import List
import multiprocessing, random


class SolutionJSS():
    def __init__(self, J: int, M: int, O: List[List[int]], T: List[List[int]]):
        self.processingOrder = []
        self.J = J
        self.M = M
        self.O = O
        self.T = T
        
    def __str__(self):
        solution = self.processingOrder
        
        currentOperation = [0 for _ in range(self.J)]
        machineTime = [0 for _ in range(self.M)]
        jobTime = [0 for _ in range(self.J)]
        
        taskSeq = [[] for _ in range(self.M)]
        
        resp = ""
        
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
        
        resp += f"\n{self.processingOrder}"
        for m in range(self.M):
            resp += f"\nMachine {m}: \n"
            for task in taskSeq[m]:
                resp += f"Job {task[0]}: [{task[1]} - {task[2]}] "
        resp += "\n"
        return resp
    
    def setSolution(self, solution: List[int]):
        self.processingOrder = solution.copy()

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
    
    def minimize(self, solution: SolutionJSS):
        processingOrder = solution.processingOrder
        
        #Guarda informações sobre o tempo atual de cada máquia e de cada job
        currentOperation = [0 for _ in range(self.J)]
        machineTime = [0 for _ in range(self.M)]
        jobTime = [0 for _ in range(self.J)]
        
        maxTime = 0
        
        for i in range(len(processingOrder)):
            job = processingOrder[i]
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
            
        return maxTime
    
    def generateInitialSolution(self):
        solution = SolutionJSS(self.J, self.M, self.O, self.T)
        
        solution.processingOrder = [i for i in range(0, self.J) for _ in range(self.M)]
        
        random.shuffle(solution.processingOrder)
        
        return solution
    
    def localSearch(self, solution: SolutionJSS):
        
        bestSolution = SolutionJSS(self.J, self.M, self.O, self.T)
        bestSolution.setSolution(solution.processingOrder)
        
        bestScore = self.minimize(bestSolution)
        
        iterator = NSIterator(0, 1)
        iterator.first()
            
        while not iterator.isDone(self):
            move = iterator.current()
                
            if move.canBeApplied(self, solution):
                returnMove = move.apply(self, solution)
                newScore = self.minimize(solution)
                
                if newScore < bestScore:
                    bestScore = newScore
                    bestSolution.setSolution(solution.processingOrder)
                    
                returnMove.apply(self, solution)    
                
            iterator.next(self)
                
        
        return bestSolution, bestScore
    
    def applyPertubation(self, solution: SolutionJSS, k: int):
        for _ in range(k):
            move = NSSwapMove.randomMove(self, solution)
            move.apply(self, solution)
            
    def runILS(self, ILSMaxIterations: int, rollbackChance: float, k: int, goal: int,return_dict: dict):
        kLinha = k
        
        s = self.generateInitialSolution()

        bestSolution, bestScore = self.localSearch(s)
        
        return_dict["best"] = bestSolution.processingOrder
        return_dict["bestScore"] = bestScore
        
        currentIteration = 0
        bestIteration = 0

        
        ILSMaxIterations = float("inf") if ILSMaxIterations == -1 else ILSMaxIterations

        k = 1

        solution = SolutionJSS(context.J, context.M, context.O, context.T)
        solution.setSolution(bestSolution.processingOrder)

        while(currentIteration - bestIteration < ILSMaxIterations):
            currentIteration += 1

            if random.random() < rollbackChance:
                solution.setSolution(bestSolution.processingOrder)

            self.applyPertubation(solution, k)

            localBestSolution, localBestScore = self.localSearch(solution)

            print(f"Iteration: {currentIteration} - NSScore: {localBestScore} - BestScore: {bestScore}")

            if localBestScore < bestScore:
                bestScore = localBestScore
                bestSolution.setSolution(localBestSolution.processingOrder)
                
                return_dict["best"] = bestSolution
                return_dict["bestScore"] = bestScore
                
                bestIteration = currentIteration
                k = kLinha
                
                if goal != -1 and bestScore <= goal:
                    break
                
            else:
                k = min(k + 1, (context.J * context.M) // 2) 
    
class Move():
    def apply(self, context: 'ContextJSS', sol: SolutionJSS):
        pass
    def canBeApplied(self, context: 'ContextJSS', sol: SolutionJSS):
        pass
    def eq(self, context: 'ContextJSS', m2: 'Move'):
        pass
    
class SwapMove(Move):
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j
    def __str__(self):
        return f"SwapMove({self.i},{self.j})"
    def apply(self, context: 'ContextJSS', sol: SolutionJSS):   
        jobI = sol.processingOrder[self.i]
        jobJ = sol.processingOrder[self.j]
        
        sol.processingOrder[self.i] = jobJ
        sol.processingOrder[self.j] = jobI
        
        return SwapMove(self.j, self.i)
    def canBeApplied(self, context: 'ContextJSS', sol: 'SolutionJSS'):
        return True
    def eq(self, context, m2: 'SwapMove'):
        return (self.i == m2.i) and (self.j == m2.j)
    
class NSSwapMove():
    @staticmethod
    def randomMove(context: 'ContextJSS', sol: SolutionJSS) -> SwapMove:
        solutionSize = len(sol.processingOrder) - 1
        i = random.randint(0, solutionSize)
        j = random.randint(0, solutionSize)
        
        while sol.processingOrder[i] == sol.processingOrder[j]:
            j = random.randint(0, solutionSize)
        
        return SwapMove(i, j)
    
class NSIterator():
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j
    def first(self):
        self.i = 0
        self.j = 1
    def next(self, context: ContextJSS):
        n = context.J * context.M
        if self.j < n - 1:
            self.j = self.j+1
        else:
            self.i = self.i + 1
            self.j = self.i + 1
    def isDone(self, context: ContextJSS):
        n = context.J * context.M
        return self.i >= n - 1
    def current(self):
        return SwapMove(self.i, self.j)
    

#Atributo criado por mim, não é nativo do ILS, mas me pareceu melhorar o algoritmo
rollbackChance = 0.1

#Nivel da pertubação padrão
k = 2

context = ContextJSS()
context.load("job-shop.txt")

timeLimit = int(input("Tempo limite em segundos: (-1 para sem limite)\n"))
ILSMaxIterations = int(input("Limite de Diferença entre Iterações: (-1 para sem limite)\n"))
scoreGoal = int(input("Makespan Objetivo: (-1 para sem objetivo)\n"))


#Overkill para garantir que seja feito por multiprocessamento
manager = multiprocessing.Manager()
return_dict = manager.dict()

p = multiprocessing.Process(target=context.runILS, name="GA", args=(ILSMaxIterations, rollbackChance, k, scoreGoal, return_dict))

tInicial = time.time()

p.start()

if timeLimit != -1:
    p.join(timeLimit)
else:
    p.join()

if p.is_alive():
    p.terminate()
    
tFinal = time.time()
    
bestSolution , bestScore = return_dict["best"], return_dict["bestScore"]

print(f"Best Solution: {bestSolution}")
print(f"Best Score: {bestScore}")
print(f"Time: {round(tFinal - tInicial,3)}s")
    


        
    

    
 
