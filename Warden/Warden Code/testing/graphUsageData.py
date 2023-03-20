import os
import sys
import matplotlib.pyplot as plt
from scipy.signal import lfilter
import subprocess
import glob
import csv

# Read from .txt or .csv files
use_txt_files = False

# For smoothing the curve, use smooth_XXXXX instead of normal data in plt.plot() lines
# the larger n is, the smoother curve will be
n = 2
b = [1.0 / n] * n
a = 1

# Change to smooth the graphs or not
smooth_curves = False

#! Helper function to graph all process data at end of collection
def graph_process_data(processes):

    for process in processes:

        pid = process.split("_")[1].split("_")[0]

        measurement_times = []
        cpu_usages = []
        memory_used = []

        if use_txt_files:
            data_file = open(process)
            data = [x.split("\t") for x in data_file.readlines()]
            data_file.close()
            for line in data:
                measurement_times.append(float(line[0].strip()))
                cpu_usages.append(float(line[1].strip()))
                memory_used.append(float(line[2].strip()))
        else:
            # opening the CSV file
            with open(process, mode ='r') as file:
            # reading the CSV file
                csvFile = csv.reader(file)
                # displaying the contents of the CSV file
                for line in csvFile:
                    if (line[0] == 'Time'):
                        continue
                    measurement_times.append(float(line[0].strip()))
                    cpu_usages.append(float(line[1].strip()))
                    memory_used.append(float(line[2].strip()))


        smooth_cpu_usages = lfilter(b,a,cpu_usages)
        smooth_memory_used = lfilter(b,a,memory_used)

        fig, cpu_axis = plt.subplots()
        ram_axis = cpu_axis.twinx()

        if smooth_curves:
            cpu_axis.plot(measurement_times[1:], smooth_cpu_usages[1:], linewidth=2, linestyle="-", c="r")
            ram_axis.plot(measurement_times[1:], smooth_memory_used[1:], linewidth=2, linestyle="-", c="b")
        else:
            cpu_axis.plot(measurement_times[1:], cpu_usages[1:], linewidth=2, linestyle="-", c="r")
            ram_axis.plot(measurement_times[1:], memory_used[1:], linewidth=2, linestyle="-", c="b")
        plt.xlabel("Time (s)")
        cpu_axis.set_ylabel("CPU Percentage (%)", color="r")
        ram_axis.set_ylabel("RAM Usage (MB)", color="b")
        plt.savefig(f"processUsage{pid}.png")
    
    # for process in processes:

    #     pid = process.split("_")[1].split("_")[0]

    #     heap_sizes = []
    #     measurement_times = []

    #     heap_file = open(f"process_{pid}_heap_sizes.txt")
    #     data = [x.split("\t") for x in heap_file.readlines()]
    #     heap_file.close()

    #     for line in data:
    #         measurement_times.append(float(line[0].strip()))
    #         heap_sizes.append(float(line[1].strip()))

    #     smooth_heap_sizes = lfilter(b,a,heap_sizes)

    #     fig, cpu_axis = plt.subplots()
    #     ram_axis = cpu_axis.twinx()

    #     if smooth_curves:
    #         cpu_axis.plot(measurement_times, smooth_heap_sizes, linewidth=2, linestyle="-", c="g")
    #         ram_axis.plot(measurement_times, smooth_heap_sizes, linewidth=2, linestyle="-", c="g")
    #     else:
    #         cpu_axis.plot(measurement_times, heap_sizes, linewidth=2, linestyle="-", c="g")
    #         ram_axis.plot(measurement_times, heap_sizes, linewidth=2, linestyle="-", c="g")
    #     plt.xlabel("Time (s)")
    #     cpu_axis.set_ylabel("Heap Size (MB)", color="r")
    #     plt.savefig(f"processHeap{pid}.png")


#! Helper to graph system data
def graph_system_data(sys_data):

    measurement_times = []
    cpu_usages = []
    memory_used = []

    if use_txt_files:
        data_file = open(sys_data)
        data = [x.split("\t") for x in data_file.readlines()]
        data_file.close()
        for line in data:
            measurement_times.append(float(line[0].strip()))
            cpu_usages.append(float(line[1].strip()))
            memory_used.append(float(line[2].strip()))
    else:
        # opening the CSV file
        with open(sys_data, mode ='r') as file:
        # reading the CSV file
            csvFile = csv.reader(file)
            # displaying the contents of the CSV file
            for line in csvFile:
                if (line[0] == 'Time'):
                    continue
                measurement_times.append(float(line[0].strip()))
                cpu_usages.append(float(line[1].strip()))
                memory_used.append(float(line[2].strip()))

    smooth_cpu_usages = lfilter(b,a,cpu_usages)
    smooth_memory_used = lfilter(b,a,memory_used)

    fig, cpu_axis = plt.subplots()
    ram_axis = cpu_axis.twinx()

    if smooth_curves:
            cpu_axis.plot(measurement_times[1:], smooth_cpu_usages[1:], linewidth=2, linestyle="-", c="r")
            ram_axis.plot(measurement_times[1:], smooth_memory_used[1:], linewidth=2, linestyle="-", c="b")
    else:
        cpu_axis.plot(measurement_times, cpu_usages, linewidth=2, linestyle="-", c="r")
        ram_axis.plot(measurement_times, memory_used, linewidth=2, linestyle="-", c="b")
    plt.xlabel("Time")
    cpu_axis.set_ylabel("CPU Percentage (%)", color="r")
    ram_axis.set_ylabel("RAM Usage (MB)", color="b")
    plt.savefig(f"systemUsage.png")


#! Helper to graph container data
def graph_container_data(containers):

    lists_of_times = []
    lists_of_cpu = []
    lists_of_memory = []

    for container in containers:

        id = container.split("_")[0]

        measurement_times = []
        cpu_usages = []
        memory_used = []

        if use_txt_files:
            data_file = open(container)
            data = [x.split("\t") for x in data_file.readlines()]
            data_file.close()
            for line in data:
                measurement_times.append(float(line[0].strip()))
                cpu_usages.append(float(line[1].strip()))
                # Measure in MB
                if(line[3].strip() == "GiB"):
                    memory_used.append(float(line[2].strip()) * 1024*1.04858) # GiB to MB
                elif(line[3].strip() == "MiB"):
                    memory_used.append(float(line[2].strip())*1.04858) # MiB to MB
                else:
                    print(f"Unexpected unit in container file: {container}, {line[3]}")
                    exit(1)

        else:
            # opening the CSV file
            with open(container, mode ='r') as file:
            # reading the CSV file
                csvFile = csv.reader(file)
                # displaying the contents of the CSV file
                for line in csvFile:
                    if (line[0] == 'Time'):
                        continue
                    measurement_times.append(float(line[0].strip()))
                    cpu_usages.append(float(line[1].strip()))
                    if(line[3].strip() == "GiB"):
                        memory_used.append(float(line[2].strip()) * 1024*1.04858) # GiB to MB
                    elif(line[3].strip() == "MiB"):
                        memory_used.append(float(line[2].strip())*1.04858) # MiB to MB
                    else:
                        print(f"Unexpected unit in container file: {container}, {line[3]}")
                        exit(1)

        lists_of_times.append(measurement_times)
        lists_of_cpu.append(cpu_usages)
        lists_of_memory.append(memory_used)
    
    # Average the lists
    time_pairings = zip(*lists_of_times)
    cpu_pairings = zip(*lists_of_cpu)
    memory_pairings = zip(*lists_of_memory)

    avg_times = [sum(x)/len(x) for x in time_pairings]
    avg_cpu = [sum(x)/len(x) for x in cpu_pairings]
    avg_mem = [sum(x)/len(x) for x in memory_pairings]
        
    smooth_cpu_usages = lfilter(b,a,avg_cpu)
    smooth_memory_used = lfilter(b,a,avg_mem)

    fig, cpu_axis = plt.subplots()
    ram_axis = cpu_axis.twinx()

    if smooth_curves:
        cpu_axis.plot(avg_times[1:], smooth_cpu_usages[1:], linewidth=2, linestyle="-", c="r")
        ram_axis.plot(avg_times[1:], smooth_memory_used[1:], linewidth=2, linestyle="-", c="b")
    else:
        cpu_axis.plot(avg_times, avg_cpu, linewidth=2, linestyle="-", c="r")
        ram_axis.plot(avg_times, avg_mem, linewidth=2, linestyle="-", c="b")
    plt.xlabel("Time (s)")
    cpu_axis.set_ylabel("CPU Percentage (%)", color="r")
    ram_axis.set_ylabel("RAM Usage (MB)", color="b")
    plt.savefig(f"containerUsage{id}.png")
    
    return


def main():
    if use_txt_files:
        #container_files = glob.glob('*_container_data.txt')
        process_files = glob.glob('process_*_usage_data.txt')
        system_file = 'system_usage_data.txt'
    else:
        #container_files = glob.glob('*_container_data.csv')
        process_files = glob.glob('process_*_usage_data.csv')
        system_file = 'system_usage_data.csv'
    #graph_container_data(container_files)
    graph_process_data(process_files)
    graph_system_data(system_file)


if __name__ == "__main__":
    main()


