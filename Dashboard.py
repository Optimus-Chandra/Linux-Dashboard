import time

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
    with open('/proc/stat' , 'r') as f :
        line = f.readline()
    parts = line.split()
    data = [int(x) for x in parts[1:]]
    idle_time = data[3] + data[4]
    total_time = sum(data)
    return total_time , idle_time
    
def get_net_stats():
    with open('/proc/net/dev' , 'r') as f :
        lines = f.readlines()
    Interfaces = [x.split()[0].strip(':') for x in lines[2:]]
    Down_speed = [x.split()[1].strip(':') for x in lines[2:]]
    Up_speed = [x.split()[9].strip(':') for x in lines[2:]]
    return Interfaces , Down_speed , Up_speed
    

# --- THE MAIN EXECUTION LOOP ---
try:
    # Initialize with None to handle first iteration
    print("\033c", end="")
    print("Initializing")
    prev_total_time, prev_idle_time = get_cpu_usage()
    Inter, PrevD_speed, PrevU_speed = get_net_stats()
    Delta_Dspeed = [0.0] * len(Inter)
    Delta_Uspeed = [0.0] * len(Inter)
    kernel_info = get_kernel_version()
    
    time.sleep(1)  # Initial sleep to get meaningful first reading
    
    while True:
        # Calculate CPU usage
        curr_total_time, curr_idle_time = get_cpu_usage()
        delta_total_time = curr_total_time - prev_total_time
        delta_idle_time = curr_idle_time - prev_idle_time
        cpu_percentage = ((delta_total_time - delta_idle_time) / delta_total_time) * 100 if delta_total_time > 0 else 0
        
        # Calculate network stats
        Inter, CurrD_speed, CurrU_speed = get_net_stats()
        for i in range(len(Inter)):
            Delta_Dspeed[i] = (float(CurrD_speed[i]) - float(PrevD_speed[i])) / 1024
            Delta_Uspeed[i] = (float(CurrU_speed[i]) - float(PrevU_speed[i])) / 1024
        
        # Display
        print("\033c", end="")
        print("=== LINUX RAW DASHBOARD v1.2 ===")
        print(f"Kernel:  {kernel_info}")
        print(f"Uptime:  {get_uptime()}")
        print(f"Load:    {get_load_avg()}")
        print(f"Memory:  {get_memory_usage()}")
        print(f"CPU Usage: {cpu_percentage:.2f}%")
        print("Network Stats:")
        print(f"{'Interface':<15} {'Download (KB/s)':>25} {'Upload (KB/s)':>20}")
        print("-" * 75)
        for k in range(len(Inter)):
            print(f"{Inter[k]:<12} {Delta_Dspeed[k]:>20.2f} {Delta_Uspeed[k]:>20.2f}")
        print("-" * 75)
        print("Press Ctrl+C to stop")
        
        # Update previous values
        prev_total_time, prev_idle_time = curr_total_time, curr_idle_time
        PrevD_speed, PrevU_speed = CurrD_speed, CurrU_speed
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopping dashboard...")
