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
    total_line_parts = lines[0].split()
    total_kb = int(total_line_parts[1])
    avail_line_parts = lines[2].split() 
    avail_kb = int(avail_line_parts[1])

    used_kb = total_kb - avail_kb

    total_gb = total_kb / 1024 / 1024
    used_gb = used_kb / 1024 / 1024

    return f"{used_gb:.2f} GB / {total_gb:.2f} GB"

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
    print("\033[2J\033[H", end="")
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
    
# --- THE MAIN EXECUTION LOOP ---
try:
    # Initialize
    hide_cursor()
    clear_screen()
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
        # Calculate CPU usage
        curr_total_time, curr_idle_time = get_cpu_usage()
        proc_counts = get_proc_counts()
        proc_counts_values = list(proc_counts.values())
        for n in range(0,4):
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
        output_lines.append(f"Memory: {get_memory_usage()}")
        output_lines.append(f"CPU: Avg {cpu_percentage[0]:.1f}%")
        output_lines.append(f"     CPU1 {get_cpu_bar(cpu_percentage[1])}{cpu_percentage[1]:>5.1f}%")
        output_lines.append(f"     CPU2 {get_cpu_bar(cpu_percentage[2])}{cpu_percentage[2]:>5.1f}%")
        output_lines.append(f"     CPU3 {get_cpu_bar(cpu_percentage[3])}{cpu_percentage[3]:>5.1f}%")
        output_lines.append(f"     CPU4 {get_cpu_bar(cpu_percentage[4])}{cpu_percentage[4]:>5.1f}%")
        output_lines.append(f"Network Stats:")
        output_lines.append(f"     {'Interface':<12} {'Down(KB/s)':>12} {'Up(KB/s)':>12}")
        for k in range(len(Inter)):
            output_lines.append(f"     {Inter[k]:<12} {Delta_Dspeed[k]:>12.2f} {Delta_Uspeed[k]:>12.2f}")
        output_lines.append(f"Processes:")
        output_lines.append(f"     Total {proc_counts['Total']} | Run {proc_counts_values[0]} | Sleep {proc_counts_values[1]} | Disk {proc_counts_values[2]} | Zombie {proc_counts_values[3]} | Stop {proc_counts_values[4]}")
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
