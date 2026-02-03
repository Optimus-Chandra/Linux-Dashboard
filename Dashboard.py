import time
import os
import sys

def get_kernel_version():
    with open('/proc/version', 'r') as f:
        content = f.read()
    words = content.split()
    return f"{words[0]} {words[1]} {words[2]}"

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        content = f.read()
    uptime_seconds = float(content.split()[0])
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    return f"{hours}h {minutes}m"

def get_load_avg():
    with open('/proc/loadavg', 'r') as f:
        content = f.read()
    data = content.split()
    return f"1m: {data[0]} | 5m: {data[1]} | 15m: {data[2]}"

def get_memory_usage():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
    # Line 0 is usually MemTotal, Line 2 is usually MemAvailable
    total_mem_line_parts = lines[0].split()
    total_mem_kb = int(total_mem_line_parts[1])
    avail_mem_line_parts = lines[2].split() 
    avail_mem_kb = int(avail_mem_line_parts[1])
    total_swap_line_parts = lines[14].split()
    total_swap_kb = int(total_swap_line_parts[1])
    free_swap_line_parts = lines[15].split()
    free_swap_kb = int(free_swap_line_parts[1])

    used_mem_kb = total_mem_kb - avail_mem_kb
    used_swap_kb = total_swap_kb - free_swap_kb

    total_mem_gb = total_mem_kb / 1024 / 1024
    used_mem_gb = used_mem_kb / 1024 / 1024
    total_swap_gb = total_swap_kb / 1024 / 1024
    used_swap_gb = used_swap_kb / 1024 / 1024

    return f"{used_mem_gb:.2f} GB / {total_mem_gb:.2f} GB" , f"{used_swap_gb:.2f} GB / {total_swap_gb:.2f} GB" 

def get_cpu_usage():
    idle_time = [] 
    total_time = [] 
    with open('/proc/stat' , 'r') as f :
        lines = [f.readline() for o in range(5)]
        for line in lines:
            parts = str(line).split()
            data = [int(x) for x in parts[1:]]
            idle = data[3] + data[4]
            total = sum(data)
            idle_time.append(idle)
            total_time.append(total)
    return total_time , idle_time
    
def get_net_stats():
    with open('/proc/net/dev' , 'r') as f :
        lines = f.readlines()
    Interfaces = [x.split()[0].strip(':') for x in lines[2:]]
    Down_speed = [x.split()[1].strip(':') for x in lines[2:]]
    Up_speed = [x.split()[9].strip(':') for x in lines[2:]]
    return Interfaces , Down_speed , Up_speed
    
def get_proc_counts():
    counts = {'R': 0, 'S': 0, 'D': 0, 'Z': 0, 'T': 0, 'Total': 0}
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    counts['Total'] = len(pids)
    for pid in pids :
        try:
            with open(f'/proc/{pid}/stat' , 'r') as f :
                content = f.read()
            parts = content.split()
            state = parts[2]
            if state in counts:
                counts[state] += 1
        except (OSError, ValueError):
            continue
        except IndexError :
            pass
    return counts
    
def get_cpu_bar(percentage):
    filled = int(percentage / 10)  # Number of bars to fill (0-10)
    filled = min(filled, 10)  # Cap at 10
    empty = 10 - filled
    bar = '[' + ('|' * filled) + (' ' * empty) + ']'
    return bar

def clear_screen():
    """Clear screen once at the start"""
    print("\033c", end="")
    sys.stdout.flush()

def move_cursor_home():
    """Move cursor to home position without clearing"""
    print("\033[H", end="")
    sys.stdout.flush()

def hide_cursor():
    """Hide the cursor"""
    print("\033[?25l", end="")
    sys.stdout.flush()

def show_cursor():
    """Show the cursor"""
    print("\033[?25h", end="")
    sys.stdout.flush()
    
def get_sys_status(RAM , Swap , Load , CPU ):
    swap_used = float(Swap.split('/')[0].strip(" GB"))
    ram_used = float(RAM.split('/')[0].strip(" GB"))
    swap_total = float(Swap.split('/')[1].strip(" GB"))
    ram_total = float(RAM.split('/')[1].strip(" GB"))
    carry = Load.split()
    load = float(carry[1])
    status = "System is Heavy (High Load, Medium CPU)"
    if ( swap_used >= swap_total * 0.5 and ram_used >= ram_total * 0.95 ) :
        status = "Memory Leak , System is Thrashing"
    elif ( load > 4) :
        if ( CPU <  10.0 ):
            status = "I/O Bottleneck"
        if ( CPU > 90.0 ):
            status = "System is Overloaded and Busy"
    else :
        status = "System is Healthy"   
    
    return status
    
# --- THE MAIN EXECUTION LOOP ---
try:
    # Initialize
    clear_screen()
    hide_cursor()
    print("Initializing...")
    
    prev_total_time, prev_idle_time = get_cpu_usage()
    Inter, PrevD_speed, PrevU_speed = get_net_stats()
    Delta_Dspeed = [0.0] * len(Inter)
    Delta_Uspeed = [0.0] * len(Inter)
    kernel_info = get_kernel_version()
    proc_types = ['Running' , 'Sleeping' , 'Disk-Sleep' , 'Zombie' , 'Stopped']
    delta_idle_time = [0] * len(prev_total_time)
    delta_total_time = [0] * len(prev_total_time)
    cpu_percentage = [0] * len(prev_total_time)
    
    time.sleep(1)  # Initial sleep to get meaningful first reading
    
    while True:
    
        mem_info , swap_info = get_memory_usage()
        
        # Calculate CPU usage
        curr_total_time, curr_idle_time = get_cpu_usage()
        proc_counts = get_proc_counts()
        proc_counts_values = list(proc_counts.values())
        for n in range(0,len(prev_total_time)):
            delta_total_time[n] = curr_total_time[n] - prev_total_time[n]
            delta_idle_time[n] = curr_idle_time[n] - prev_idle_time[n]
            cpu_percentage[n] = ((delta_total_time[n] - delta_idle_time[n]) / delta_total_time[n]) * 100 if delta_total_time[n] > 0 else 0
        
        # Calculate network stats
        Inter, CurrD_speed, CurrU_speed = get_net_stats()
        for i in range(len(Inter)):
            Delta_Dspeed[i] = (float(CurrD_speed[i]) - float(PrevD_speed[i])) / 1024
            Delta_Uspeed[i] = (float(CurrU_speed[i]) - float(PrevU_speed[i])) / 1024
        
        # Move cursor to home and display (no screen clear!)
        move_cursor_home()
        
        # Build output as a single string to minimize flicker
        output_lines = []
        output_lines.append("=== LINUX DASHBOARD ===")
        output_lines.append(f"Kernel: {kernel_info}")
        output_lines.append(f"Uptime:  {get_uptime()}")
        output_lines.append(f"Load:    {get_load_avg()}")
        output_lines.append(f"Memory: {mem_info}")
        output_lines.append(f"Swap Memory: {swap_info}")
        output_lines.append(f"CPU: Avg {cpu_percentage[0]:.1f}%")
        for i in range(1, len(cpu_percentage)):
            output_lines.append(f"     CPU{i} {get_cpu_bar(cpu_percentage[i])}{cpu_percentage[i]:>5.1f}%")
        output_lines.append(f"Network Stats:")
        output_lines.append(f"     {'Interface':<12} {'Down(KB/s)':>12} {'Up(KB/s)':>12}")
        for k in range(len(Inter)):
            output_lines.append(f"     {Inter[k]:<12} {Delta_Dspeed[k]:>12.2f} {Delta_Uspeed[k]:>12.2f}")
        output_lines.append(f"Processes:")
        output_lines.append(f"     Total {proc_counts['Total']} | Run {proc_counts_values[0]} | Sleep {proc_counts_values[1]} | Disk {proc_counts_values[2]} | Zombie {proc_counts_values[3]} | Stop {proc_counts_values[4]}")
        output_lines.append("")
        output_lines.append(f"{get_sys_status(mem_info , swap_info , get_load_avg() , cpu_percentage[0])}")
        output_lines.append("")
        output_lines.append("Press Ctrl+C to stop")
        
        # Print all lines at once with padding to clear any leftover text
        for line in output_lines:
            # Pad each line to 80 characters to clear any previous longer content
            print(f"{line:<80}")
        
        sys.stdout.flush()
        
        # Update previous values
        prev_total_time, prev_idle_time = curr_total_time, curr_idle_time
        PrevD_speed, PrevU_speed = CurrD_speed, CurrU_speed
        
        time.sleep(1)
        
except KeyboardInterrupt:
    show_cursor()
    print("\nStopping dashboard...")
finally:
    show_cursor()
