#!/usr/bin/env python
import sys
import string
import math

'''
Classes
'''

class Rand48(object):
    def __init__(self, seed):
        self.n = seed
    def seed(self, seed):
        self.n = seed
    def srand(self, seed):
        self.n = (seed << 16) + 0x330e
    def next(self):
        self.n = (25214903917 * self.n + 11) & (2**48 - 1)
        return self.n
    def drand(self):
        return self.next() / 2**48
    def lrand(self):
        return self.next() >> 17
    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

'''class Burst(object):
    def __init__(self, _cpu=0, _burst=0):
        self.cpu = _cpu
        self.burst = _burst

class Process(object):
    def __init__(self, _name, _arr_time, _algo):
        self.name = _name
        self.arr_time = _arr_time
        self.burst_time = 0
        self.wait_time = 0
        self.algo = _algo
    # modifying burst and wait times
    def add_burst(self, btime):
        self.burst_time += btime
    def add_wait(self, wtime):
        self.wait_time += wtime
    # getting turnaround time
    def get_tt(self, endtime):
        return endtime - self.arr_time
    # for sorting
    def __lt__(self, other):
        if self.algo == "FCFS":
            if self.arr_time != other.arr_time:
                return self.arr_time < other.arr_time
            else:
                return self.name < other.name'''

'''
Functions for each algorithm
'''

def isfloat(string):
    for char in string:
        if not (char.isdigit() or char == '.'):
            return False
    return True

def log_lambda(number, info):
    return (-1 * math.log(number, math.e)) / info["lambda"]

def get_next_rand(info, r):
    next_rand = r.drand()
    next_rand_dist = log_lambda(next_rand, info)
    while next_rand_dist > info["upper-bound"]:
        next_rand = r.drand()
        next_rand_dist = log_lambda(next_rand, info)
    return(next_rand, next_rand_dist)

# Helper function to make the queue into a string for printing purposes
def q_to_str(q):

    if len(q) == 0:
        return "[Q <empty>]"
    temp = "[Q"
    for i in q:
        temp = temp + " " +i
    temp = temp +"]"
    return temp
def FCFS(info):
    time = 0
    q = []
    in_cpu = "*"
    in_io = []
    context_switch = info["switch-time"]/2
    rand_gen, proc_list = rand_nums(info,False)
    arrival_list = list(proc_list.keys())
    print("time 0ms: Simulator started for FCFS [Q <empty>]")
    finished = list(proc_list.keys())
    
    while(len(finished)!=0):
        ## CHECKING IF CURRENT BURST IS FINISHED
        if in_cpu != "*": 
            #print(in_cpu, proc_list[in_cpu][1])
            ## IF CURRENT PROCESS IS DONE
            if proc_list[in_cpu][1][0][0] <= 1:
                if proc_list[in_cpu][1][0][1] == -1:
                    print("time "+str(time)+"ms: Process "+in_cpu+" terminated "+q_to_str(q))
                    finished.remove(in_cpu)
                    in_cpu = "*"
                    context_switch =  info["switch-time"]
                else:
                    if len(proc_list[in_cpu][1]) ==1:
                        if(not time >999):
                            print("time "+str(time)+"ms: Process "+in_cpu+" completed a CPU burst; 1 burst to go "+q_to_str(q))
                    else:
                        if(not time >999):
                            print("time "+str(time)+"ms: Process "+in_cpu+" completed a CPU burst;"+str(len(proc_list[in_cpu][1]))+" bursts to go "+q_to_str(q))
                    if(not time >999):
                        print("time "+str(time)+"ms: Process "+in_cpu+" switching out of CPU; will block on I/O until time "+str(proc_list[in_cpu][1][0][1]+time)+"ms "+q_to_str(q))
                    context_switch = info["switch-time"]
                    in_io.append(in_cpu)
                    in_io.sort()
                    in_cpu = "*"
            ## IF CURRENT PROCESS IS NOT DONE
            else:
                proc_list[in_cpu][1][0][0] = proc_list[in_cpu][1][0][0] -1
        ## CHECKING FOR I/O 
        for i in in_io:
            if proc_list[i][1][0][1]<= 0:
                if(not time >999):
                    print("time "+str(time)+"ms: Process "+i+" completed I/O; added to ready queue "+q_to_str(q))
                proc_list[i][1].pop(0)
                #print(i,proc_list[i][1]) 
                in_io.remove(i)
                q.append(i)
            else:
                proc_list[i][1][0][1] = proc_list[i][1][0][1] - 1
                
        ### CHECKING ARRIVAL
        for arrival in arrival_list:
            if proc_list[arrival][0] == time:
                q.append(arrival)
                arrival_list.remove(arrival)
                if(not time >999):
                    print("time "+str(time)+"ms: Process "+arrival+" arrived; added to read queue "+q_to_str(q))
        ## DEALING WITH CONTEXT SWITCHING
        if in_cpu == "*":
            if len(q) != 0:
                if context_switch <= 0:
                    in_cpu = q[0]
                    if(not time >999):
                        print("time "+str(time)+"ms: Process "+q[0]+" started using the CPU for "+str(proc_list[q[0]][1][0][0])+"ms burst " + q_to_str(q))
                    q.remove(q[0])
                else: 
                    context_switch = context_switch -1
        time = time + 1
    print("time "+str(int(time-1+(info["switch-time"]/2)))+"ms: Simulator ended for FCFS [Q <empty>]")



def SRT(info, proc_list, burst_times):
    time = 0
    print()
    print()
    print("SRT")
    print("time: 0ms: Simulator started for SRT [Q <empty>]")

    n= 0;
    for i in proc_list:
        total_bursts = len(burst_times[i])//2

        print("Process {} [NEW] (arrival time {} ms) {} CPU bursts".format(i, burst_times[i][0], total_bursts))
        print("time 0ms: Simulator started for SRT [Q <empty>]")

        #print(i, proc_list[i])
        #print(burst_times[i])
        n += 1
        

## Calculates all random burst times returns a dictionary
## Key is a letter ie. A, B, C ...
## Value is [[arrival time][[burst time, io time], [burst time, io time], ...number of bursts... [burst time, -1]]
## Tau is if it to include tau in print time (Might need to rework it)
def rand_nums(info,tau):
    # Calculating process information
    # Initializing process info container
    proc_list = dict()

    # Initializing random number generator
    rand_gen = Rand48(0)
    rand_gen.srand(info["seed"])
    # Getting label for each process
    for i in range(info["n"]):
        proc_list[string.ascii_uppercase[i]] = []
    
    arrivals = []
    burst_times = []
    
    # Calculating arrival time, cpu bursts and cpu/io times for each process
    for proc_name in proc_list:
        # Calculating arrival time and number of bursts
        arrival = info["upper-bound"]+1
        while(arrival>info["upper-bound"]):
            arrival = math.floor(-math.log(rand_gen.drand())/info["lambda"])
        proc_list[proc_name].append(arrival)
        num_of_bursts = int(rand_gen.drand()*100)+1
        cpu_and_io = []
        for i in range(num_of_bursts):
            cpu = int(get_next_rand(info, rand_gen)[1]) + 1
            if i < num_of_bursts-1:
                io = int(get_next_rand(info, rand_gen)[1]) + 1
            else:
                io = -1
            cpu_and_io.append([cpu,io])
        proc_list[proc_name].append(cpu_and_io)
        if tau:
            print("Process "+proc_name+" [NEW] (arrival time "+str(arrival)+" ms) "+str(num_of_bursts)+" CPU bursts (tau "+str(1/info["lambda"])+"ms)")
        else:
            print("Process "+proc_name+" [NEW] (arrival time "+str(arrival)+" ms) "+str(num_of_bursts)+" CPU bursts")
    return (rand_gen,proc_list)


if __name__ == "__main__":
    ## Checking for correct arg len
    if(len(sys.argv) < 8 or len(sys.argv) > 9 ):
        sys.exit("Usage: seed lambda upper-bound n switch-time alpha time-slice [rr-add]")

    ## Sanity check of input
    # TODO
    for i in range(1,7):
        if not (isfloat(sys.argv[i])):
            sys.exit("ERROR: All required arguments must be valid numbers")
    if(len(sys.argv) == 9):
        if (sys.argv[8] not in ["BEGINNING", "END"]):
            sys.exit("ERROR: RR add argument must be 'BEGINNING' or 'END'")

    ## Setting globals
    # All in info dictionary
    # Key name is "seed", "lambda", etc.

    info = dict()
    info["seed"] = int(sys.argv[1])
    info["lambda"] = float(sys.argv[2])
    info["upper-bound"] = int(sys.argv[3])
    info["n"] = int(sys.argv[4])
    info["switch-time"] = int(sys.argv[5])
    info["alpha"] = float(sys.argv[6])
    info["time-slice"] = int(sys.argv[7])
    if(len(sys.argv) == 9):
        info["rr-add"] = sys.argv[8]
    else:
        info["rr-add"] = "END"

    FCFS(info)


    '''
    Simulations for each algorithm (stdout)
    '''
    '''
    # First-come, first-served
    #FCFS(info, proc_list)
    print(burst_times)

    print("STARTING SIMULATIONS")
    SRT(info, proc_list, burst_times)
    '''
    '''
    Stats for each algorithm (output file)
    '''

    ## Printing stats to output file