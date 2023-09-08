from utils.cpuexplorer import CpuExplorer

# Parameters
delay = 15

cmd_tsk = 'taskset -c {subset}'
cmd_load = 'stress-ng --cpu {core} -l {len} --timeout ' + str(delay)

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
    f.write('results=\'results-def\'\n')
    f.write('program=\'/usr/bin/python3 /usr/local/src/rapl-reader/rapl-reader.py\'\n')
    f.write('mkdir "$results"\n')
    for stress_level in range(10,101,10):
        f.write('#Stress level ' + str(stress_level) + '\n')
        f.write('$program &\n')
        f.write('app_pid=$!\n')
        for load_level in load_levels:
            req_core = round(1/(stress_level/100)*load_level)
            gen_cmd = cmd_load.replace('{core}', str(req_core)).replace('{len}', str(stress_level))
            f.write(gen_cmd + '\n')
        f.write('kill $app_pid\n')
        f.write('mv consumption.csv "$results"/consumption-' + str(stress_level) + '%\n')

tasksets = [x.get_cpu_id() for x in allocated_cpu]
duration = 0
with open("exp-smt.sh", "w") as f:
    f.write('#!/bin/bash\n')
    f.write('results=\'results-smt\'\n')
    f.write('program=\'/usr/bin/python3 /usr/local/src/rapl-reader/rapl-reader.py\'\n')
    f.write('mkdir "$results"\n')
    for stress_level in range(10,101,10):
        f.write('#Stress level ' + str(stress_level) + '\n')
        f.write('$program &\n')
        f.write('app_pid=$!\n')
        for load_level in load_levels:
            req_core = round(1/(stress_level/100)*load_level)
            duration+=delay
            subset = ''.join(str(core) + ',' for core in tasksets[:load_level])[:-1]
            gen_cmd = cmd_tsk.replace('{subset}', subset) + ' ' + cmd_load.replace('{core}', str(req_core)).replace('{len}', str(stress_level))
            f.write(gen_cmd + '\n')
        f.write('kill $app_pid\n')
        f.write('mv consumption.csv "$results"/consumption-' + str(stress_level) + '%\n')

print('Total duration', duration, 'sec i.e.', float(duration/60), 'mn')