from typing import List
import random

# Explicação do problema:
# O problema do job-shop scheduling consiste em alocar tarefas em máquinas, de forma a minimizar o tempo total de conclusão de todas as tarefas.

# Dados de entrada:
# J = número de jobs (Ex: 3)
# M = número de máquinas (Ex: 3)
# Tij = tempo de processamento do job i na máquina j (Ex: [[3, 2, 5], [4, 3, 2], [2, 1, 4], [3, 4, 2], [2, 3, 4]])
# Oij = ordem de processamento do job i (Ex: [[1, 2, 3], [2, 1, 3], [3, 1, 2], [2, 3, 1], [1, 3, 2]])

class Task():
    def __init__(self, jobId: int, Tinicial: int, Tfinal: int):
        self.jobId = jobId
        self.Tinicial = Tinicial
        self.Tfinal = Tfinal
        
    def __str__(self):
        return f"Task({self.jobId}, {self.Tinicial}, {self.Tfinal})"

class SolutionJSS():
    def __init__(self):
        self.taskSeq : List[List[Task]] = []
        self.T : List[List[int]] = []
        self.makespan : int = 0
        self.maxTimeUnits : int = 0
        
    def setSolution(self, taskSeq: List[List[Task]], makespan: int = 0, maxTimeUnits: int = 0, T: List[List[int]] = []):
        self.taskSeq = []
        for m in range(len(taskSeq)):
            line = []
            for i in range(len(taskSeq[m])):
                line.append(Task(taskSeq[m][i][0], taskSeq[m][i][1], taskSeq[m][i][2]))
            self.taskSeq.append(line)
        self.makespan = makespan
        self.maxTimeUnits = maxTimeUnits
        self.T = T
        
    def getSolution(self):
        tasksLite = []
        for m in range(len(self.taskSeq)):
            line = []
            for i in range(len(self.taskSeq[m])):
                line.append([self.taskSeq[m][i].jobId, self.taskSeq[m][i].Tinicial, self.taskSeq[m][i].Tfinal])
            tasksLite.append(line)
            
        return tasksLite, self.makespan, self.maxTimeUnits, self.T
        
    def __str__(self):
        resp = ""
        for m in range(len(self.taskSeq)):
            resp += f"Machine {m}: \n"
            resp += "Task Sequence: \n"
            for task in self.taskSeq[m]:
                resp += f" {task.jobId} "
            resp += "\n"
            resp += "Timeline: \n"
            for i in range(self.makespan+2):
                resp += f" {i} "
            resp += "\n"
            for i in range(self.makespan+2):
                hasCurrentTask = False
                for task in self.taskSeq[m]:
                    if task.Tinicial <= i and i < task.Tfinal:
                        resp += f" {task.jobId} "
                        hasCurrentTask = True
                        break
                if not hasCurrentTask:
                    resp += " - "
                    
            resp += "\n"
        resp += f"Makespan: {self.makespan}\n"
            
        return resp
    
    def rescheduleSolution(self, m: int): 
        for k in range(len(self.taskSeq[m])):
            if k == 0:
                oldTask = self.taskSeq[m][k]
                newTask = Task(oldTask.jobId, oldTask.Tinicial, oldTask.Tinicial + self.T[oldTask.jobId][m])
                self.taskSeq[m][k] = newTask
            else:
                oldTask = self.taskSeq[m][k]
                lastTask = self.taskSeq[m][k - 1]
                if oldTask.Tinicial < lastTask.Tfinal:
                    newTask = Task(oldTask.jobId, lastTask.Tfinal, lastTask.Tfinal + self.T[oldTask.jobId][m])
                    self.taskSeq[m][k] = newTask
                else:
                    newTask = Task(oldTask.jobId, oldTask.Tinicial, oldTask.Tinicial + self.T[oldTask.jobId][m])
                    self.taskSeq[m][k] = newTask
                    
        self.makespan = max([max([task.Tfinal for task in self.taskSeq[k]]) for k in range(len(self.taskSeq))])
                    
    
class ContextJSS():
    def __init__(self):
        self.J : int = 0
        self.M : int = 0
        self.T : List[List[int]] = []
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
                task = Task(job, 0, problem.T[job][machine])
            else:
                lastTask = solution.taskSeq[machine][-1]
                task = Task(job, lastTask.Tfinal, lastTask.Tfinal + problem.T[job][machine])
            solution.taskSeq[machine].append(task)
            makespan = max(makespan, task.Tfinal)
                
        solution.makespan = makespan
        return solution       
    
    def minimize(self,solution: SolutionJSS) -> int: #~ N^3
        penalty = 0
        maxTimeUnits = solution.maxTimeUnits
        
        tasks = []
        
        if solution.makespan > maxTimeUnits:
            return solution.makespan + 1000000
        
        for j in range(self.J):
            for m in range(self.M):
                for i in range(self.J):
                    if solution.taskSeq[m][i].jobId == j:
                        tasks.append({"t": solution.taskSeq[m][i], "m": m})
                        break
            tasks.sort(key = lambda x: x["t"].Tinicial)
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
                    if task["t"].Tfinal > tasks[i]["t"].Tinicial:
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

class SwapMove(Move):
    def __init__(self, i: int, j: int, m: int):
        self.i = i
        self.j = j
        self.m = m
    def __str__(self):
        return f"SwapMove({self.i},{self.j},{self.m})"
    def apply(self, problemCtx: 'ContextJSS', sol: SolutionJSS):   
        AuxI = sol.taskSeq[self.m][self.i]
        AuxJ = sol.taskSeq[self.m][self.j]
        TaskI = Task(AuxI.jobId, AuxJ.Tinicial, AuxI.Tfinal)
        TaskJ = Task(AuxJ.jobId, AuxI.Tinicial, AuxJ.Tfinal)
        
        sol.taskSeq[self.m][self.i] = TaskJ
        sol.taskSeq[self.m][self.j] = TaskI
        
        sol.rescheduleSolution(self.m)
    def canBeApplied(self, problemCtx: 'ContextJSS', sol: 'SolutionJSS'):
        
        iDuration = problemCtx.T[sol.taskSeq[self.m][self.i].jobId][self.m]
        jDuration = problemCtx.T[sol.taskSeq[self.m][self.j].jobId][self.m]
        
        iStartingTime = sol.taskSeq[self.m][self.i].Tinicial
        jStartingTime = sol.taskSeq[self.m][self.j].Tinicial
        
        if iStartingTime + jDuration > sol.maxTimeUnits or jStartingTime + iDuration > sol.maxTimeUnits:
            return False
        return True
    def eq(self, problemCtx, m2: 'SwapMove'):
        return (self.i == m2.i) and (self.j == m2.j) and (self.m == m2.m)
    
class NSSwapMove():
    def randomMove(problemCtx: 'ContextJSS', sol: SolutionJSS) -> SwapMove:
        i = random.randint(0, problemCtx.J - 1)
        j = random.randint(0, problemCtx.J - 1)
        while i == j:
            j = random.randint(0, problemCtx.J - 1)
        m = random.randint(0, problemCtx.M - 1)
        return SwapMove(i, j, m)
    
class RealocMove(Move):
    def __init__(self, i: int, t: int, m: int):
        self.i = i
        self.t = t
        self.m = m
    def __str__(self):
        return f"RealocMove({self.i},{self.t},{self.m})"
    def apply(self, problemCtx: 'ContextJSS', sol: SolutionJSS):
        task = sol.taskSeq[self.m].pop(self.i)
        NewTask = Task(task.jobId, self.t, task.Tfinal)
        taskBefore = 0
        while taskBefore < len(sol.taskSeq[self.m]) and sol.taskSeq[self.m][taskBefore].Tfinal <= task.Tinicial:
            taskBefore += 1
        
        if taskBefore == len(sol.taskSeq[self.m]):
            sol.taskSeq[self.m].append(NewTask)
        else:
            sol.taskSeq[self.m].insert(taskBefore, NewTask)
        sol.rescheduleSolution(self.m)
            
    def canBeApplied(self, problemCtx, sol: 'SolutionJSS'):
        maxTimeUnits = sol.maxTimeUnits
        task = sol.taskSeq[self.m][self.i]
        return self.t + problemCtx.T[task.jobId][self.m] <= maxTimeUnits
    def eq(self, problemCtx, m2: 'RealocMove'):
        return (self.i == m2.i) and (self.t == m2.t) and (self.m == m2.m)
    
class NSRealocMove():
    def randomMove(problemCtx: 'ContextJSS', sol: SolutionJSS) -> RealocMove:
        i = random.randint(0, problemCtx.J - 1)
        m = random.randint(0, problemCtx.M - 1)
        t = random.randint(0, sol.makespan)
        if sol.taskSeq[m][i].Tinicial < t:
            t = random.randint(0, sol.makespan)
        return RealocMove(i, t, m)
    
    
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
        
class NSSeqMove():
    @staticmethod
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

""" s = SolutionJSS()
s.setSolution(
    [
        [[0, 0, 2], [2, 2, 6], [1, 6, 9]],
        [[1, 0, 2], [0, 2, 6], [2, 6, 9]],
        [[2, 0, 2], [1, 2, 3], [0, 6, 9]]
    ]
    ,9
    ,24
    ,[[2, 4, 3], [3, 2, 1], [4, 3, 2]]
)

print(s)
score = context.minimize(s)
print(score) """

#Generates and avaliates the Initial Solution
s = ContextJSS.generateSolution(context)

score = context.minimize(s)
print("First Score: ", score,"\n",s, "\n")

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
    

    
 
