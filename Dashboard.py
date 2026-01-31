import time

def get_kernel_version():
    # METHOD: Reading a simple one-line file
    # 'r' means read mode. 'with' ensures the file closes automatically.
    with open('/proc/version', 'r') as f:
        content = f.read()
    
    # split() chops the long sentence into a list of words
    words = content.split()
    
    # We take the first 3 words (Index 0, 1, 2)
    return f"{words[0]} {words[1]} {words[2]}"

def get_uptime():
    # METHOD: Doing math on file data
    with open('/proc/uptime', 'r') as f:
        content = f.read()
    
    # The file looks like "3600.50 14400.20". We want the first number.
    uptime_seconds = float(content.split()[0])
    
    # // is integer division (no decimals). % is the remainder.
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    return f"{hours}h {minutes}m"

def get_load_avg():
    # METHOD: Simple string parsing
    with open('/proc/loadavg', 'r') as f:
        content = f.read()
    
    # We want the first 3 numbers (1min, 5min, 15min averages)
    data = content.split()
    return f"1m: {data[0]} | 5m: {data[1]} | 15m: {data[2]}"

def get_memory_usage():
    # METHOD: Parsing a multi-line file
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines() # readlines() gives us a LIST of lines
    
    # Line 0 is usually MemTotal, Line 2 is usually MemAvailable
    # Example line: "MemTotal:       16303020 kB"
    
    # 1. Parse Total Memory
    total_line_parts = lines[0].split()
    total_kb = int(total_line_parts[1]) # The number is the 2nd item
    
    # 2. Parse Available Memory (Check your file, sometimes it's index 2)
    avail_line_parts = lines[2].split() 
    avail_kb = int(avail_line_parts[1])
    
    # 3. Calculate Used
    used_kb = total_kb - avail_kb
    
    # 4. Convert to GB (1024 KB = 1 MB, 1024 MB = 1 GB)
    total_gb = total_kb / 1024 / 1024
    used_gb = used_kb / 1024 / 1024
    
    # .2f means "show only 2 decimal places"
    return f"{used_gb:.2f} GB / {total_gb:.2f} GB"

# --- THE MAIN EXECUTION LOOP ---
try:
    while True:
        # This magic string clears the terminal screen
        print("\033c", end="")
        cached_kernel_info = get_kernel_version()
        print("=== LINUX RAW DASHBOARD v1.0 ===")
        print(f"Kernel:  {cached_kernel_info}")
        print(f"Uptime:  {get_uptime()}")
        print(f"Load:    {get_load_avg()}")
        print(f"Memory:  {get_memory_usage()}")
        print("================================")
        print("Press Ctrl+C to stop")
        
        # Wait 1 second before updating again
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping dashboard...")
