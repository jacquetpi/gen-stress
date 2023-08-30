from utils.cpuexplorer import CpuExplorer

# Parameters
delay = 15

cmd_tsk = 'taskset -c {subset}'
cmd_load = 'stress-ng --cpu {core} --timeout ' + str(delay)

cpuset = CpuExplorer().build_cpuset()
allocated_cpu = [cpuset.get_cpu_list()[0]]
available_cpu = list(cpuset.get_cpu_list())
while len(allocated_cpu) != len(cpuset.get_cpu_list()):
    # find closest cpu
    cpu = cpuset.get_closest_available_cpus(available_list=available_cpu, allocated_list=allocated_cpu)
    allocated_cpu.append(cpu[0])
    available_cpu.remove(cpu[0])

load_levels = range(1,len(allocated_cpu)+1)
with open("exp-def.sh", "w") as f:
    f.write('#!/bin/bash\n')
    for level in load_levels:
        gen_cmd = cmd_load.replace('{core}', str(level))
        f.write(gen_cmd + '\n')

tasksets = [x.get_cpu_id() for x in allocated_cpu]
duration = 0
with open("exp-smt.sh", "w") as f:
    f.write('#!/bin/bash\n')
    for level in load_levels:
        duration+=delay
        subset = ''.join(str(core) + ',' for core in tasksets[:level])[:-1]
        gen_cmd = cmd_tsk.replace('{subset}', subset) + ' ' + cmd_load.replace('{core}', str(level))
        f.write(gen_cmd + '\n')

print('Total duration', duration, 'sec i.e.', float(duration/60), 'mn')