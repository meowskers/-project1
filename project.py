#!/usr/bin/env python
import sys
import string
import math

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
    wait_time = 0
    turnaround_time = 0
    switches = 1
    preemptions = 0
    full = False
    context_switch = int(info["switch-time"]/2)
    rand_gen, proc_list = rand_nums(info,False)
    arrival_list = list(proc_list.keys())
    turn = dict() 
    n_bursts = 0
    total_burst_time = 0
    for i in proc_list:
        for j in proc_list[i][1]:
            total_burst_time = total_burst_time + j[0]
        n_bursts = n_bursts+ len(proc_list[i][1])
    
    print("time 0ms: Simulator started for FCFS [Q <empty>]")
    finished = list(proc_list.keys())
    while(len(finished)!=0):
        wait_time = wait_time + len(q)
        ## CHECKING IF CURRENT BURST IS FINISHED
        if in_cpu != "*" and in_cpu != "@": 
            ## IF CURRENT PROCESS IS DONE
            if proc_list[in_cpu][1][0][0] <= 1:
                # LAST BURST
                if proc_list[in_cpu][1][0][1] == -1:
                    print("time "+str(time)+"ms: Process "+in_cpu+" terminated "+q_to_str(q))
                    turn[in_cpu] = time
                    finished.remove(in_cpu)
                    in_cpu = "@"
                    context_switch =  int(info["switch-time"]/2)
                else:
                    if len(proc_list[in_cpu][1]) ==1:
                        if(not time >999 or full):
                            print("time "+str(time)+"ms: Process "+in_cpu+" completed a CPU burst; 1 burst to go "+q_to_str(q))
                    else:
                        if(not time >999 or full):
                            print("time "+str(time)+"ms: Process "+in_cpu+" completed a CPU burst;"+str(len(proc_list[in_cpu][1])-1)+" bursts to go "+q_to_str(q))
                    temp = proc_list[in_cpu][1][0][1]+time+int(info["switch-time"]/2)
                    if(not time >999 or full):
                        print("time "+str(time)+"ms: Process "+in_cpu+" switching out of CPU; will block on I/O until time "+str(temp)+"ms "+q_to_str(q))
                    proc_list[in_cpu][1][0][1] =  temp
                    in_io.append(in_cpu)
                    in_io.sort()
                    in_cpu = "@"
                    context_switch =  int(info["switch-time"]/2)
            ## IF CURRENT PROCESS IS NOT DONE
            else:
                proc_list[in_cpu][1][0][0] = proc_list[in_cpu][1][0][0] -1
        ## CHECKING FOR I/O 
        for i in in_io:
            ##print("##",i,"##",proc_list[i][1][0][1])
            if proc_list[i][1][0][1]== time:
                q.append(i)
                if(not time >999 or full):
                    print("time "+str(time)+"ms: Process "+i+" completed I/O; added to ready queue "+q_to_str(q))
                proc_list[i][1].pop(0)
                in_io.remove(i)
                
        ### CHECKING ARRIVAL
        for arrival in arrival_list:
            if proc_list[arrival][0] == time:
                q.append(arrival)
                arrival_list.remove(arrival)
                if(not time >999):
                    print("time "+str(time)+"ms: Process "+arrival+" arrived; added to ready queue "+q_to_str(q))
        ## DEALING WITH CONTEXT SWITCHING
        if in_cpu == "*":
            if len(q) != 0:
                if context_switch <= 0:
                    in_cpu = q[0]
                    q.remove(q[0])
                    context_switch = int(info["switch-time"]/2)
                    if(not time >999 or full):
                        print("time "+str(time)+"ms: Process "+in_cpu+" started using the CPU for "+str(proc_list[in_cpu][1][0][0])+"ms burst " + q_to_str(q))
                else: 
                    context_switch = context_switch -1
        if in_cpu == "@":
            if context_switch <= 1:
                in_cpu = "*"
                switches = switches+1
                context_switch = int(info["switch-time"]/2)
            else:
                context_switch = context_switch -1
        time = time + 1
    print("time "+str(int(time-1+(info["switch-time"]/2)))+"ms: Simulator ended for FCFS [Q <empty>]")
    print("##",n_bursts)
    cpu_burst_time = total_burst_time/n_bursts
    wait_time = (wait_time - (switches*2))/n_bursts
    turnaround_time = 0
    for i in turn:
        turnaround_time = turnaround_time + (turn[i]-proc_list[i][0])
    turnaround_time = turnaround_time/n_bursts
    return cpu_burst_time,wait_time, turnaround_time, switches, preemptions
# ~~~~~~~~~~~~~~
def RR(info):
    time = 0
    q = []
    in_cpu = "*"
    in_io = []
    wait_time = 0
    turnaround_time = 0
    switches = 1
    preemptions = 0
    full = True
    context_switch = int(info["switch-time"]/2)
    rand_gen, proc_list = rand_nums(info,False)
    arrival_list = list(proc_list.keys())
    turn = dict() 
    n_bursts = 0
    special = "*"
    total_burst_time = 0
    for i in proc_list:
        for j in proc_list[i][1]:
            total_burst_time = total_burst_time + j[0]
        n_bursts = n_bursts+ len(proc_list[i][1])
    rr = info["time-slice"]
    print("time 0ms: Simulator started for RR [Q <empty>]")
    finished = list(proc_list.keys())
    while(len(finished)!=0):
        wait_time = wait_time + len(q)
        ## CHECKING IF CURRENT BURST IS FINISHED
        if in_cpu != "*" and in_cpu != "@": 
            ## IF CURRENT PROCESS IS DONE
            if proc_list[in_cpu][1][0][0] <= 1:
                # LAST BURST
                if proc_list[in_cpu][1][0][1] == -1:
                    print("time "+str(time)+"ms: Process "+in_cpu+" terminated "+q_to_str(q))
                    turn[in_cpu] = time
                    finished.remove(in_cpu)
                    in_cpu = "@"
                    context_switch =  int(info["switch-time"]/2)
                    rr = info["time-slice"]
                else:
                    if len(proc_list[in_cpu][1]) ==1:
                        if(not time >999 or full):
                            print("time "+str(time)+"ms: Process "+in_cpu+" completed a CPU burst; 1 burst to go "+q_to_str(q))
                    else:
                        if(not time >999 or full):
                            print("time "+str(time)+"ms: Process "+in_cpu+" completed a CPU burst;"+str(len(proc_list[in_cpu][1])-1)+" bursts to go "+q_to_str(q))
                    temp = proc_list[in_cpu][1][0][1]+time+int(info["switch-time"]/2)
                    if(not time > 999 or full):
                        print("time "+str(time)+"ms: Process "+in_cpu+" switching out of CPU; will block on I/O until time "+str(temp)+"ms "+q_to_str(q))
                    proc_list[in_cpu][1][0][1] =  temp
                    in_io.append(in_cpu)
                    in_io.sort()
                    in_cpu = "@"
                    rr = info["time-slice"]
                    context_switch =  int(info["switch-time"]/2)
            ## IF TIME SLICE IS DONE
            elif rr <= 1 and len(q) != 0:
                proc_list[in_cpu][1][0][0] = proc_list[in_cpu][1][0][0] -1
                preemptions = preemptions + 1
                if(not time > 999 or full):
                    print("time "+str(time)+"ms: Time slice expired; Process "+in_cpu+" preempted with "+str(proc_list[in_cpu][1][0][0])+"ms to go "+q_to_str(q))
                rr = info["time-slice"]
                special = in_cpu
                in_cpu = "@"
            ## IF TIME SLICE IS DONE BUT HAS AN EMPTY QUEUE
            elif rr<= 1 and len(q) == 0:
                if(not time > 999 or full):
                    print("time "+str(time)+"ms: Time slice expired; no preemption because ready queue is empty "+q_to_str(q))
                rr = info["time-slice"]
                proc_list[in_cpu][1][0][0] = proc_list[in_cpu][1][0][0] -1
            else:
                proc_list[in_cpu][1][0][0] = proc_list[in_cpu][1][0][0] -1
                rr = rr - 1
        ## CHECKING FOR I/O 
        
        for i in in_io:
            if proc_list[i][1][0][1]<= time:
                if info["rr-add"]=="END":
                    q.append(i)
                else:
                    q.insert(0,i)
                if(not time >999 or full):
                    print("time "+str(time)+"ms: Process "+i+" completed I/O; added to ready queue "+q_to_str(q))
                proc_list[i][1].pop(0)
                in_io.remove(i)
                
        ### CHECKING ARRIVAL
        for arrival in arrival_list:
            if proc_list[arrival][0] == time:
                if info["rr-add"]=="END":
                    q.append(arrival)
                else:
                    q.insert(0,arrival)
                arrival_list.remove(arrival)
                if(not time >999):
                    print("time "+str(time)+"ms: Process "+arrival+" arrived; added to ready queue "+q_to_str(q))
        ## DEALING WITH CONTEXT SWITCHING
        if in_cpu == "*":
            if len(q) != 0:
                if context_switch <= 0:
                    in_cpu = q[0]
                    q.remove(q[0])
                    context_switch = int(info["switch-time"]/2)
                    if(not time >999 or full):
                        print("time "+str(time)+"ms: Process "+in_cpu+" started using the CPU for "+str(proc_list[in_cpu][1][0][0])+"ms burst " + q_to_str(q))
                else: 
                    context_switch = context_switch -1
        if in_cpu == "@":
            if context_switch <= 1:
                in_cpu = "*"
                switches = switches+1
                if special != "*":
                    q.append(special)
                    special = "*"
                context_switch = int(info["switch-time"]/2)
            else:
                context_switch = context_switch -1
        time = time + 1
    print("time "+str(int(time-1+(info["switch-time"]/2)))+"ms: Simulator ended for RR [Q <empty>]")
    print("##",n_bursts)
    cpu_burst_time = total_burst_time/n_bursts
    wait_time = (wait_time - (switches*2))/n_bursts
    turnaround_time = 0
    for i in turn:
        turnaround_time = turnaround_time + (turn[i]-proc_list[i][0])
    turnaround_time = turnaround_time/n_bursts
    return cpu_burst_time,wait_time, turnaround_time, switches, preemptions
# ~~~~~~~~~
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
        

## Calculates all random burst times returns random number generator and a dictionary containing values
## Key is a letter ie. A, B, C ...
## Value is [[arrival time],[[burst time, io time], [burst time, io time], ...number of bursts... [burst time, -1]]
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

    burst_time,FCFS_wait, FCFS_turnaround, FCFS_switches, FCFS_preemptions = FCFS(info)
    print("Algo FCFS")
    print("CPU burst",round(burst_time,3))
    print("average wait",round(FCFS_wait,3))
    print("turnaround",round(FCFS_turnaround,3))
    print("switches",FCFS_switches)
    print("preemptions",FCFS_preemptions)
    burst_time,RR_wait,RR_turnaround, RR_switches, RR_preemptions = RR(info)
    print("Algo RR")
    print("CPU burst",round(burst_time,3))
    print("average wait",round(RR_wait,3))
    print("turnaround",round(RR_turnaround,3))
    print("switches",RR_switches)
    print("preemptions",RR_preemptions)
