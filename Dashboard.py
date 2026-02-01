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

# --- THE MAIN EXECUTION LOOP ---
try:
    cpu_percentage = 0
    while True:
        # This string clears the terminal screen
        print("\033c", end="")
        kernel_info = get_kernel_version()
        prev_total_time , prev_idle_time = get_cpu_usage()
        
        print("=== LINUX RAW DASHBOARD v1.1 ===")
        print(f"Kernel:  {kernel_info}")
        print(f"Uptime:  {get_uptime()}")
        print(f"Load:    {get_load_avg()}")
        print(f"Memory:  {get_memory_usage()}")
        print(f"CPU Usgae: {cpu_percentage:.2f}%")
        print("================================")
        print("Press Ctrl+C to stop")
        
        # Wait 1 second before updating again
        time.sleep(1)
        curr_total_time , curr_idle_time = get_cpu_usage()
        delta_total_time = curr_total_time - prev_total_time
        delta_idle_time = curr_idle_time - prev_idle_time
        cpu_percentage = ((delta_total_time - delta_idle_time) / delta_total_time) * 100
        prev_total_time = curr_total_time
        prev_idle_time = curr_idle_time
        

except KeyboardInterrupt:
    print("\nStopping dashboard...")
