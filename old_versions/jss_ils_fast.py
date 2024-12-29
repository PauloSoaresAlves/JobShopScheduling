from typing import List
import random

# Explicação do problema:
# O problema do job-shop scheduling consiste em alocar tarefas em máquinas, de forma a minimizar o tempo total de conclusão de todas as tarefas.

# Dados de entrada:
# J = número de jobs (Ex: 3)
# M = número de máquinas (Ex: 3)
# Tij = tempo de processamento do job i na máquina j (Ex: [[3, 2, 5], [4, 3, 2], [2, 1, 4], [3, 4, 2], [2, 3, 4]])
# Oij = ordem de processamento do job i (Ex: [[1, 2, 3], [2, 1, 3], [3, 1, 2], [2, 3, 1], [1, 3, 2]])

# Solução:
# taskSeq = sequência de tarefas por máquina (Ex: [[[0, 0, 3], [1, 3, 5]], [[2, 0, 2], [3, 2, 6]], [[4, 0, 2], [0, 3, 5]]])

#Restrições:
# 1. Cada job deve ser processado em cada máquina uma única vez
# 2. Cada tarefa de um job deve ser processado em ordem
# 3. Cada máquina deve processar uma tarefa por vez
# 4. Cada job só pode ser processado em uma máquina por vez


class SolutionJSS():
    def __init__(self):
        #taskSeq: List[List[List[int]]] = [[job, start, end]]
        self.taskSeq : List[List[List[int]]] = []
        
        #makespan: int = tempo total de conclusão de todas as tarefas
        self.makespan : int = 0
        
        #Util
        self.T : List[List[int]] = []
        self.maxTimeUnits : int = 0
    
    #setSolution: Define uma solução (Pra evitar deep copy)
    def setSolution(self, taskSeq: List[List[List[int]]], makespan: int = 0, maxTimeUnits: int = 0, T: List[List[int]] = []):
        self.taskSeq = []
        for m in range(len(taskSeq)):
            line = []
            for i in range(len(taskSeq[m])):
                line.append([taskSeq[m][i][0], taskSeq[m][i][1], taskSeq[m][i][2]])
            self.taskSeq.append(line)
        self.makespan = makespan
        self.maxTimeUnits = maxTimeUnits
        self.T = T
    
    #getSolution: Retorna a solução (Pra evitar deep copy)
    def getSolution(self):
        return self.taskSeq, self.makespan, self.maxTimeUnits, self.T
        
    def __str__(self):
        resp = ""
        for m in range(len(self.taskSeq)):
            resp += f"Machine {m}: \n"
            resp += "Task Sequence: \n"
            for task in self.taskSeq[m]:
                resp += f" {task[0]}: [{task[1]} - {task[2]}] "
            resp += "\n"
        resp += f"Makespan: {self.makespan}\n"
            
        return resp
    
    #rescheduleSolution: Reorganiza a solução de acordo com a mudança no tempo inicial das tarefas
    #Após mudanças de tempos iniciais, é necessário reorganizar a sequência de tarefas
    #Tarefas seguem a ordem do taskSeq, logo, se uma tarefa colide com outra, a mais pro final da lista é adiada
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
                    
        self.makespan = max([max([task[2] for task in self.taskSeq[k]]) for k in range(len(self.taskSeq))]) #O(n^2)
                    
#Contexto do Problema    
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
    
    #Gera uma solução inicial, escolhe aleatóriamente se um job vai ser escolhido por ordem de tamanho ou aleatóriamente
    # + ou - graps
    def generateSolution(problem: 'ContextJSS') -> SolutionJSS:
        solution = SolutionJSS()
        maxTimeUnits = sum([sum(problem.T[j]) for j in range(problem.J)])
        
        solution.taskSeq = [[] for _ in range(problem.M)]
        solution.T = problem.T
        solution.maxTimeUnits = maxTimeUnits
        
        tasks = [i for i in range(problem.J * problem.M)]
        tasks.sort(key = lambda x: problem.T[x // problem.M][x % problem.M], reverse = True)
        makespan = 0
        
        while tasks:
            if random.random() < 0.5:
                task = tasks.pop(0)
            else:
                task = random.choice(tasks)
                tasks.remove(task)
            job = task // problem.M
            machine = task % problem.M
            if not solution.taskSeq[machine]:
                task = [job, 0, problem.T[job][machine]]
            else:
                lastTask = solution.taskSeq[machine][-1]
                task = [job, lastTask[2], lastTask[2] + problem.T[job][machine]]
            solution.taskSeq[machine].append(task)
            makespan = max(makespan, task[2])
                
        solution.makespan = makespan
        return solution       
    
    #minimize: Função de avaliação da solução
    def minimize(self,solution: SolutionJSS) -> int: #~ N^3
        penalty = 0
        maxTimeUnits = solution.maxTimeUnits
        
        tasks = []
        #Se a solução for mais duradoura que a soma de todos os tempos, algo está bem errado
        if solution.makespan > maxTimeUnits:
            return solution.makespan + 1000000
        
        #Pra cada job, verifica pega a sua ordem de processamento e:
        # 1. Verifica se a ordem de processamento está de acordo com O[j]
        # 2. Verifica se o job está sendo processado em 2 máquinas ao mesmo tempo
        for j in range(self.J):
            for m in range(self.M):
                for i in range(self.J):
                    if solution.taskSeq[m][i][0] == j:
                        tasks.append({"t": solution.taskSeq[m][i], "m": m})
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
                        penalty += 1
                for i in range(len(tasks)):
                    if task["t"][2] > tasks[i]["t"][1]:
                        penalty += 1
                        break
                
        return solution.makespan + (penalty * 100)

class Move():
    def apply(self, problemCtx: 'ContextJSS', sol: SolutionJSS):
        pass
    def canBeApplied(self, problemCtx: 'ContextJSS', sol: SolutionJSS):
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
    def apply(self, problemCtx: 'ContextJSS', sol: SolutionJSS):   
        TaskI = sol.taskSeq[self.m][self.i]
        TaskJ = sol.taskSeq[self.m][self.j]
        
        sol.taskSeq[self.m][self.i] = [TaskJ[0], TaskI[1], TaskJ[2]]
        sol.taskSeq[self.m][self.j] = [TaskI[0], TaskJ[1], TaskI[2]]
        
        sol.rescheduleSolution(self.m)
    def canBeApplied(self, problemCtx: 'ContextJSS', sol: 'SolutionJSS'):
        jobI = sol.taskSeq[self.m][self.i][0]
        jobJ = sol.taskSeq[self.m][self.j][0]
        
        iDuration = problemCtx.T[jobI][self.m]
        jDuration = problemCtx.T[jobJ][self.m]
        
        iStartingTime = sol.taskSeq[self.m][self.i][1]
        jStartingTime = sol.taskSeq[self.m][self.j][1]
        
        if iStartingTime + jDuration > sol.maxTimeUnits or jStartingTime + iDuration > sol.maxTimeUnits:
            return False
        return True
    def eq(self, problemCtx, m2: 'SwapMove'):
        return (self.i == m2.i) and (self.j == m2.j) and (self.m == m2.m)

#Determina uma troca aleatória
class NSSwapMove():
    def randomMove(problemCtx: 'ContextJSS', sol: SolutionJSS) -> SwapMove:
        i = random.randint(0, problemCtx.J - 1)
        j = random.randint(0, problemCtx.J - 1)
        while i == j:
            j = random.randint(0, problemCtx.J - 1)
        m = random.randint(0, problemCtx.M - 1)
        return SwapMove(i, j, m)

#Movimento de realocação, move o tempo inicial de uma tarefa i para um tempo t
#Verifica quem ocupa o tempo t e insere a tarefa i antes no taskSeq
class RealocMove(Move):
    def __init__(self, i: int, t: int, m: int):
        self.i = i
        self.t = t
        self.m = m
    def __str__(self):
        return f"RealocMove({self.i},{self.t},{self.m})"
    def apply(self, problemCtx: 'ContextJSS', sol: SolutionJSS):
        task = sol.taskSeq[self.m].pop(self.i)
        NewTask = [task[0], self.t, task[2]]
        taskBefore = 0
        while taskBefore < len(sol.taskSeq[self.m]) and sol.taskSeq[self.m][taskBefore][2] <= task[1]:
            taskBefore += 1
        
        if taskBefore == len(sol.taskSeq[self.m]):
            sol.taskSeq[self.m].append(NewTask)
        else:
            sol.taskSeq[self.m].insert(taskBefore, NewTask)
        sol.rescheduleSolution(self.m)
            
    def canBeApplied(self, problemCtx, sol: 'SolutionJSS'):
        maxTimeUnits = sol.maxTimeUnits
        task = sol.taskSeq[self.m][self.i]
        return self.t + problemCtx.T[task[0]][self.m] <= maxTimeUnits
    def eq(self, problemCtx, m2: 'RealocMove'):
        return (self.i == m2.i) and (self.t == m2.t) and (self.m == m2.m)

#Determina uma realocação aleatória
class NSRealocMove():
    def randomMove(problemCtx: 'ContextJSS', sol: SolutionJSS) -> RealocMove:
        i = random.randint(0, problemCtx.J - 1)
        m = random.randint(0, problemCtx.M - 1)
        t = random.randint(0, sol.makespan)
        if sol.taskSeq[m][i][1] < t:
            t = random.randint(0, sol.makespan)
        return RealocMove(i, t, m)
    
#Iterador da vizinhança
class MoveIterator():
    def __init__(self, i: int, j: int, m: int, type: int):
        self.i = i
        self.j = j
        self.m = m
        self.type = type
    def first(self, problemCtx: 'ContextJSS'):
        self.i = 0
        self.j = 1
        self.m = 0
        self.type = 0
    def next(self, problemCtx: 'ContextJSS'):
        if self.type == 0:
            if self.j < problemCtx.J - 1:
                self.j += 1
            elif self.i < problemCtx.J - 2:
                self.i += 1
                self.j = self.i + 1
            elif self.m < problemCtx.M - 1:
                self.m += 1
                self.i = 0
                self.j = 1
            else:
                self.type = 1
                self.i = 0
                self.j = 0
                self.m = 0
        else:
            maxTimeUnits = sum([sum(problemCtx.T[j]) for j in range(problemCtx.J)])
            if self.j < maxTimeUnits - 1:
                self.j += 1
            elif self.i < problemCtx.J - 1:
                self.i += 1
                self.j = 0
            elif self.m < problemCtx.M - 1:
                self.m += 1
                self.i = 0
                self.j = 0
            else:
                self.type = 2
    def isDone(self, problemCtx: 'ContextJSS'):
        return self.type == 2
    def current(self, problemCtx: 'ContextJSS') -> Move:
        if self.type == 0:
            return SwapMove(self.i, self.j, self.m)
        else:
            return RealocMove(self.i, self.j, self.m)

#Classe de auxilio para movimentação
class NSSeqMove():
    def getIterator(problemCtx: 'ContextJSS', sol: SolutionJSS) -> MoveIterator:
        return MoveIterator(0, 1, 0, 0)
    
    def randomMove(problemCtx: 'ContextJSS', sol: SolutionJSS) -> Move:
        move = random.randint(0, 1)
        if move == 0:
            return NSSwapMove.randomMove(problemCtx, sol)
        else:
            return NSRealocMove.randomMove(problemCtx, sol)
               
#Initializes Problem
context = ContextJSS()
context.load("job-shop.txt")

#Generates and avaliates the Initial Solution
s = ContextJSS.generateSolution(context)

score = context.minimize(s)
print("First Score: \n",s, "\n")

best = SolutionJSS()

best.setSolution(*s.getSolution())
bestScore = score

#Initializes the counters to ILS
currentIteration = 0
globalBestIteration = currentIteration
nIterations = 100

sLinha = SolutionJSS()
sLocal = SolutionJSS()
sLinha.setSolution(*s.getSolution())
while currentIteration - globalBestIteration < nIterations:
    
    #random weight to decide if the current iteration will be based on the last solution or the best solution
    if random.random() < 0.1:
        sLinha.setSolution(*best.getSolution())
    
    #random weight to decide how many moves will be applied to the solution
    k = max(2, (((currentIteration-globalBestIteration+1)/nIterations) * 10))
    
    currentIteration += 1
    
    print("Iteration: ", currentIteration)
    
    #Applies the moves to the solution
    while k > 0:
        m = NSSeqMove.randomMove(context, sLinha)
        if m.canBeApplied(context, sLinha):
            m.apply(context, sLinha)
            k -= 1

    #Sees if the pertubed solution is better than the best solution
    score = context.minimize(sLinha)
    
    if score < bestScore:
        best.setSolution(*sLinha.getSolution())
        bestScore = score
        globalBestIteration = currentIteration
        print("New Best Score: ", bestScore, "Iteration: ", currentIteration)

    
    #Local Search
    sLocal.setSolution(*sLinha.getSolution())
    it = NSSeqMove.getIterator(context, sLocal)
    it.first(context)
    while not it.isDone(context):
        
        
        m = it.current(context)
    
        if not m.canBeApplied(context, sLocal):
            it.next(context)
            continue
        
        m.apply(context, sLocal)
        
        score = context.minimize(sLocal)
        
        #First Improvement for faster local search
        if score < bestScore:
            best.setSolution(*sLocal.getSolution())
            bestScore = score
            globalBestIteration = currentIteration
            print("New Best Score: ", bestScore, "Iteration: ", currentIteration)
            break
        
        sLocal.setSolution(*sLinha.getSolution())
        
        it.next(context)
        
print(best)
print("Best Score: ", bestScore)
print("Global Best Iteration: ", globalBestIteration)
    

    
 
