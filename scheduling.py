def calculate_avg(processes):
    n = len(processes)
    avg_wt = sum(p['wt'] for p in processes) / n
    avg_tat = sum(p['tat'] for p in processes) / n
    avg_rt = sum(p['rt'] for p in processes) / n
    return avg_wt, avg_tat, avg_rt

def fcfs(processes):
    processes.sort(key=lambda x: x['at'])
    time = 0
    gantt = []

    for p in processes:
        p['st'] = max(time, p['at'])
        p['ct'] = p['st'] + p['bt']
        p['rt'] = p['st'] - p['at']
        p['tat'] = p['ct'] - p['at']
        p['wt'] = p['tat'] - p['bt']
        gantt.append({'pid': p['pid'], 'start': p['st'], 'end': p['ct']})
        time = p['ct']

    avg_wt, avg_tat, avg_rt = calculate_avg(processes)
    return processes, gantt, avg_wt, avg_tat, avg_rt

def sjf(processes):
    processes.sort(key=lambda x: (x['at'], x['bt']))
    completed = []
    gantt = []
    time = 0
    remaining = processes[:]

    while remaining:
        available = [p for p in remaining if p['at'] <= time]
        if not available:
            time += 1
            continue
        current = min(available, key=lambda x: x['bt'])
        current['st'] = time
        current['ct'] = time + current['bt']
        current['rt'] = time - current['at']
        current['tat'] = current['ct'] - current['at']
        current['wt'] = current['tat'] - current['bt']
        gantt.append({'pid': current['pid'], 'start': current['st'], 'end': current['ct']})
        time = current['ct']
        remaining.remove(current)
        completed.append(current)

    avg_wt, avg_tat, avg_rt = calculate_avg(completed)
    return completed, gantt, avg_wt, avg_tat, avg_rt

def priority_scheduling(processes, priority_type):
    reverse = True if priority_type == 2 else False
    processes.sort(key=lambda x: (x['at'], x['pr']), reverse=reverse)
    completed = []
    gantt = []
    time = 0
    remaining = processes[:]

    while remaining:
        available = [p for p in remaining if p['at'] <= time]
        if not available:
            time += 1
            continue
        current = sorted(available, key=lambda x: x['pr'], reverse=reverse)[0]
        current['st'] = time
        current['ct'] = time + current['bt']
        current['rt'] = time - current['at']
        current['tat'] = current['ct'] - current['at']
        current['wt'] = current['tat'] - current['bt']
        gantt.append({'pid': current['pid'], 'start': current['st'], 'end': current['ct']})
        time = current['ct']
        remaining.remove(current)
        completed.append(current)

    avg_wt, avg_tat, avg_rt = calculate_avg(completed)
    return completed, gantt, avg_wt, avg_tat, avg_rt

def round_robin(processes, quantum):
    from collections import deque

    queue = deque()
    gantt = []
    time = 0
    completed = []
    n = len(processes)
    remaining_bt = {p['pid']: p['bt'] for p in processes}
    arrival_map = {p['pid']: p['at'] for p in processes}
    st_map = {}
    visited = set()

    processes.sort(key=lambda x: x['at'])
    i = 0
    while i < n and processes[i]['at'] <= time:
        queue.append(processes[i])
        visited.add(processes[i]['pid'])
        i += 1

    while queue or i < n:
        if not queue:
            time = processes[i]['at']
            queue.append(processes[i])
            visited.add(processes[i]['pid'])
            i += 1
            continue

        p = queue.popleft()
        pid = p['pid']
        bt = remaining_bt[pid]
        exec_time = min(bt, quantum)

        if pid not in st_map:
            st_map[pid] = time

        gantt.append({'pid': pid, 'start': time, 'end': time + exec_time})
        time += exec_time
        remaining_bt[pid] -= exec_time

        while i < n and processes[i]['at'] <= time:
            if processes[i]['pid'] not in visited:
                queue.append(processes[i])
                visited.add(processes[i]['pid'])
            i += 1

        if remaining_bt[pid] > 0:
            queue.append(p)
        else:
            ct = time
            bt_original = p['bt']
            at = p['at']
            st = st_map[pid]
            rt = st - at
            tat = ct - at
            wt = tat - bt_original
            completed.append({
                'pid': pid, 'at': at, 'bt': bt_original,
                'st': st, 'ct': ct, 'rt': rt, 'tat': tat, 'wt': wt
            })

    avg_wt, avg_tat, avg_rt = calculate_avg(completed)
    return completed, gantt, avg_wt, avg_tat, avg_rt

def simulate_scheduling(processes, algorithm, quantum=None, priority_type=None):
    # Ensure clean copies
    procs = [dict(p) for p in processes]

    if algorithm == "fcfs":
        table, gantt, avg_wt, avg_tat, avg_rt = fcfs(procs)
    elif algorithm == "sjf":
        table, gantt, avg_wt, avg_tat, avg_rt = sjf(procs)
    elif algorithm == "priority":
        table, gantt, avg_wt, avg_tat, avg_rt = priority_scheduling(procs, priority_type)
    elif algorithm == "rr":
        table, gantt, avg_wt, avg_tat, avg_rt = round_robin(procs, quantum)
    else:
        return {"error": "Invalid algorithm"}

    return {
        "table": table,
        "gantt": gantt,
        "avg_wt": avg_wt,
        "avg_tat": avg_tat,
        "avg_rt": avg_rt
    }
