import sys
import time
import matplotlib.pyplot as plt
from scipy.signal import lfilter
import subprocess
import threading
import csv
import os

# Read from .txt or .csv files
use_txt_files = False

# System Configured Constant used for calculations
clock_ticks = 100

# Time to run
run_time = float(sys.argv[1])

# Interval to measure each time
interval = float(sys.argv[2])

# Process IDs to investigate
# process_ids = [int(x) for x in sys.argv[3:]]

# List Docker containers and save to file
os.system("docker ps --all > /home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/containers.txt")
# Get lines from file
ps_file = open("/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/containers.txt", 'r')
lines = ps_file.readlines()
ps_file.close()
# Get Container IDs of SuS containers
container_IDs = []
for line in lines:
    if "wp-511:nginx-fpm" in line:
        container_IDs.append(line.split(" ")[0])

# Delete output of docker ps --all file
os.system("rm /home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/containers.txt")


#! Helper function to write out data to file at end of collection
def write_out_pid_data(pid, cpu_usages, memory_used, measurement_times):#, heap_sizes):

    if use_txt_files:
        #Write data to file
        data_file = open(f"process_{pid}_usage_data.txt", "w")
        for index in range(len(measurement_times)):
            data_file.write(f"{measurement_times[index]}\t{cpu_usages[index]}\t{memory_used[index]}\n")
        data_file.close()
    else:
        zipped_data = zip(*[measurement_times, cpu_usages, memory_used])
        data = [ list(x) for x in zipped_data ]
        file = open(f'process_{pid}_usage_data.csv', 'w+', newline='')
        with file:   
            write = csv.writer(file)
            write.writerow(['Time', 'CPU %', 'Memory (MB)'])
            write.writerows(data)
        file.close()

#! Thread process to collect and write out info on process <pid>
def process_measurements(pid, run_event):
    # Lists of collected data
    measurement_times = []
    cpu_usages = []
    memory_used = []
    #heap_sizes = []
    #print(f"Collecting process {pid} CPU and RAM usage data...")

    # Used to graph x-axis as time since experiment start (might change to just time.time() to 
    # match data points across multiple data sets)
    s_time = time.time()

    # Get initial utime, stime, and time of measurement
    stat_file = open(f"/proc/{pid}/stat", "r")
    info = stat_file.read()
    stat_file.close()

    info = info.split(" ")
    prev_utime = int(info[12])/clock_ticks
    prev_stime = int(info[13])/clock_ticks
    prev_measurement_time = time.time()

    # Sleep for a initial interval
    time.sleep(interval)

    # Collect data until terminated
    while run_event.is_set():

        try:
            # Get stat file from /proc pseudo filesystem
            stat_file = open(f"/proc/{pid}/stat", "r")
            info = stat_file.read()
            stat_file.close()
            info = info.split(" ")

            # Measure utime and stime
            measured_utime = int(info[12])/clock_ticks
            measured_stime = int(info[13])/clock_ticks

            # f = open(f"/proc/{pid}/maps", 'r')
            # lines = f.readlines()
            # f.close()
            # for line in lines:
            #     if "[heap]" in line:
            #         heap_addrs = line.split(" ")[0].split("-")
            #         size = int("0x" + heap_addrs[1], 16) - int("0x" + heap_addrs[0],16)
            #         break

            # Measure RAM usage
            memory_used.append(int(subprocess.check_output("pmap "+ str(pid)+" -x | tail -n 1 | awk '/[0-9] /{print $4}'", shell=True).strip())/1000)
            

            # Get time of measurement and record it
            measurement_time = time.time()

            # Get time using CPU over time of interval
            delta_utime = measured_utime - prev_utime
            delta_stime = measured_stime - prev_stime
            interval_time = measurement_time - prev_measurement_time

            # Record this interval's CPU usage, RAM usage, and time
            cpu_percentage = ((delta_utime + delta_stime) / interval_time) / 4 # normalize for 4 cores
            cpu_usages.append(cpu_percentage*100)
            measurement_times.append(measurement_time) #! Uncomment to measure time relative to experiment's start - s_time)
            # heap_sizes.append(size)

            # Update previous variables for the next measurement
            prev_utime = measured_utime
            prev_stime = measured_stime
            prev_measurement_time = measurement_time

            time.sleep(interval)

        # When either this program or the PID process is terminated, record data
        except (KeyboardInterrupt, FileNotFoundError):

            # If the file associated with the PID is gone, write data and return
            write_out_pid_data(pid, cpu_usages, memory_used, measurement_times) #, heap_sizes)
            return
    
    # If the run_event is unset, write out data and return
    write_out_pid_data(pid, cpu_usages, memory_used, measurement_times) #, heap_sizes)
    return

#! Thread to record system usage data
def system_measurements(run_event):

    times = []
    percentages = []
    memory_used = []

    # Used to graph x-axis as time since experiment start (might change to just time.time() to 
    # match data points across multiple data sets)
    starting_time = time.time()

    # Get starting total_cpu_time and idle_cpu_time
    stat_file = open("/proc/stat", "r")
    first_line = stat_file.readline()
    columns = [float(x.strip("\n")) for x in first_line.split("  ")[1].split(" ")]
    prev_interval_time = sum(columns)
    prev_idle_time = columns[3]
    stat_file.close()

    # Sleep for initial interval
    time.sleep(interval)

    # Continue until time runs out
    while run_event.is_set():

        # Get new total_cpu_time and new idle_cpu_time
        stat_file = open("/proc/stat", "r")
        first_line = stat_file.readline()
        stat_file.close()

        # Calculate total time of this interval and time CPU was idle during this interval
        columns = [float(x.strip("\n")) for x in first_line.split("  ")[1].split(" ")]

        # Use the previous values to calculate
        interval_time = sum(columns) - prev_interval_time
        idle_time = columns[3] - prev_idle_time

        # Turn to percentage of time spent working
        percentage = 100*(1-(idle_time/interval_time))

        # Record CPU %, RAM used, and time of measurement
        percentages.append(percentage)
        memory_used.append(int(subprocess.check_output("free -m | tail -n 2 | head -n 1 | awk '/[0-9] /{print $3}'", shell=True).strip()))
        times.append(time.time())

        # Update prev_time values for the next interval
        prev_interval_time = sum(columns)
        prev_idle_time = columns[3]

        # Wait the interval worth of time
        time.sleep(interval)

    if use_txt_files:
        data_file = open("system_usage_data.txt", "w")
        for index in range(len(times)):
            data_file.write(f"{times[index]}\t{percentages[index]}\t{memory_used[index]}\n")
        data_file.close()
    else:
        zipped_data = zip(*[times, percentages, memory_used])
        data = [ list(x) for x in zipped_data ]
        file = open('system_usage_data.csv', 'w+', newline='')
        with file:   
            write = csv.writer(file)
            write.writerow(['Time', 'CPU %', 'Memory (MB)'])
            write.writerows(data)
        file.close()
    avg_file = open("avg.txt", "w")
    avg_file.write(f"{sum(percentages)/len(percentages)}")
    avg_file.close()

#! Thread to record container CPU and memory usage
def container_measurements(run_event):

    # Dictionaries to separate each container's data

    # Time of measurement
    measurement_times = {}
    # CPU %
    cpu_usages = {}
    # Memory used
    memory_usages = {}
    # Unit of "Memory used"
    memory_units = {}

    # Set defaults in the dictionaries for each container ID we got at the beginning of this script
    for cID in container_IDs:
        measurement_times[cID] = []
        cpu_usages[cID] = []
        memory_usages[cID] = []
        memory_units[cID] = []

    # Run until the parent thread unsets run event
    while run_event.is_set():

        # Execute docker stats once, showing name, ID, CPU %, and Memory
        os.system('docker stats --format "{{.Name}}\t{{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" --no-stream > /home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/dockerStats.txt')
        stat_file = open("/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/dockerStats.txt", 'r')
        lines = stat_file.readlines()
        stat_file.close()

        # Collect data on each container (except the auth-container)
        for line in lines:
            if "auth-container" not in line:
                split_line = line.split()
                # Record measurement time
                measurement_times[split_line[1]].append(time.time())
                # Record CPU usage percentage
                cpu_usages[split_line[1]].append(split_line[2].strip('%'))
                # Get the memory reading and split it into the number and units
                mem_reading = split_line[3]
                mem_number = ""
                mem_unit = ""
                for i in range(len(mem_reading)):
                    if mem_reading[i].isdigit() or mem_reading[i] == ".":
                        mem_number += mem_reading[i]
                    else:
                        mem_unit = mem_reading[i:]
                        break
                # Record the memory number
                memory_usages[split_line[1]].append(mem_number)
                # Record the memory unit
                memory_units[split_line[1]].append(mem_unit)

        # Sleep for interval
        time.sleep(interval)

    # Delete stat file since we don't need it anymore
    os.system("rm /home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/dockerStats.txt")

    # Record data on each container in it's own file
    for cID in container_IDs:
        if use_txt_files:
            data_file = open(f"/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/{cID}_container_data.txt", "w")
            for i in range(len(measurement_times[cID])):
                # Format of Time - CPU % - Memory - Mem. Unit (tab delimited)
                data_file.write(f"{measurement_times[cID][i]}\t{cpu_usages[cID][i]}\t{memory_usages[cID][i]}\t{memory_units[cID][i]}\n")
            data_file.close()
        else:
            zipped_data = zip(*[measurement_times[cID], cpu_usages[cID], memory_usages[cID], memory_units[cID]])
            data = [ list(x) for x in zipped_data ]
            file = open(f'/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/testing/{cID}_container_data.csv', 'w+', newline='')
            with file:   
                write = csv.writer(file)
                write.writerow(['Time', 'CPU %', 'Memory (MB)'])
                write.writerows(data)
            file.close()

    return


#! Main function that spawns threads and gracefully terminates them when keyboard interrupt
def main():
    run_event = threading.Event()
    run_event.set()
    threads = []

    # for pid in process_ids:
    #     thread = threading.Thread(target=process_measurements, args=(pid, run_event))
    #     thread.start()
    #     threads.append(thread)
    #     print(f"Starting collection on PID: {pid}")
    
    # containers_thread = threading.Thread(target=container_measurements, args=(run_event,))
    # containers_thread.start()
    # threads.append(containers_thread)
    # print(f"Container data collection started")

    system_thread = threading.Thread(target=system_measurements, args=(run_event,))
    system_thread.start()
    threads.append(system_thread)
    print("Collecting system-wide CPU and RAM usage data...")

    print(f"All threads started.")

    s_time = time.time()

    while time.time() - s_time < run_time:
        try:
            time.sleep(10)
            print(f"Have run for {round(time.time() - s_time, 1)} / {run_time} seconds")
        except KeyboardInterrupt:
            print(f"Gracefully terminating all threads...")
            run_event.clear()

            for thread in threads:
                thread.join()
            
            print(f"All data collected, terminating...")
            
            exit(0)
    
    print(f"Gracefully terminating all threads...")
    run_event.clear()

    for thread in threads:
        thread.join()
    
    print(f"All data collected, terminating...")
    
    exit(0)


if __name__ == "__main__":
    main()