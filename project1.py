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

# info is globals
# proc-info is process information
'''
def FCFS(info, proc_list):
    time = 0
    print("time: 0ms: Simulator started for FCFS [Q <empty>]")
    rand_gen = Rand48(0)
    rand_gen.srand(info["seed"])
    proc_info = dict()
    proc_objs = list()
    # generating arrival time and number of cpu bursts
    for proc_name in proc_list:
        # proc_info is dictionary where:
        # -- key: process name
        # -- value: [arrival_time, [(cpu, io), (cpu, io), ...]]
        proc_info[proc_name] = list()
        # Calculating arrival time and number of bursts
        arrival = get_next_rand(info, rand_gen)
        bursts = get_next_rand(info, rand_gen)
        arrival_time = int(arrival[1])
        # Making process object in proc_objs
        proc_objs.append(Process(proc_name, arrival_time, "FCFS"))
        # Recording arrival time in proc_info
        proc_info[proc_name].append(arrival_time)
        proc_info[proc_name].append([])
        # Number of bursts
        total_bursts = math.floor(bursts[0] * 100) + 1
        # Getting CPU and IO burst times for each CPU burst
        for i in range(total_bursts):
            cpu = int(get_next_rand(info, rand_gen)[1]) + 1
            io = 0
            if i < total_bursts-1:
                io = int(get_next_rand(info, rand_gen)[1]) + 1
            proc_info[proc_name][1].append(Burst(cpu, io))
    # Getting processes in order of arrival
    proc_objs.sort()
    for p in proc_objs:
        print("time {}ms: Process {} arrived and added to the ready queue".format(p.arr_time, p.name))
'''


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
def rand_nums(info):
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

    rand_gen, proc_list = rand_nums(info)


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