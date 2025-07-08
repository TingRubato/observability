import re
from rich.console import Console
from rich.table import Table
from rich.progress import track, Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from datetime import datetime, timedelta
import time
import os
import glob
from collections import defaultdict

# Load log
LOG_PATH = "logs/execute-all.log"
DATA_PATHS = ["src/data/json/*.json", "src/data/xml/*.xml"]

# Initialize console
console = Console()

def scan_data_files():
    """Scan data files to determine hourly execution success"""
    hourly_success = defaultdict(set)
    
    for pattern in DATA_PATHS:
        files = glob.glob(pattern)
        for file in files:
            # Extract timestamp from filename like mazak-1-vtc-200_current_20250707_142835.json
            match = re.search(r'_(\d{8})_(\d{6})', file)
            if match:
                date_str, time_str = match.groups()
                try:
                    # Parse timestamp
                    dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                    hour_key = dt.strftime("%Y-%m-%d %H:00")
                    hourly_success[hour_key].add(os.path.basename(file))
                except ValueError:
                    continue
    
    return hourly_success

def parse_log(log_path):
    if not os.path.exists(log_path):
        return []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    job_entries = []
    current_job = {}

    for line in lines:
        line = line.strip()
        # Detect start of a job
        if line.startswith("Processing"):
            if current_job:
                job_entries.append(current_job)
                current_job = {}
            match = re.search(r'Processing (.*?) - (\w+)', line)
            if match:
                current_job = {
                    "job_id": match.group(1),
                    "mode": match.group(2),
                    "log": [],
                    "start_time": datetime.now()  # Approximate start time
                }
        elif line and current_job:
            current_job["log"].append(line)

    if current_job:
        job_entries.append(current_job)

    return job_entries

def make_hourly_timeline_table():
    """Create a table showing hourly execution success"""
    hourly_data = scan_data_files()
    
    table = Table(title="📊 Hourly Execution Timeline (Last 24 Hours)")
    table.add_column("Hour", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Files Generated", style="green")
    
    # Generate last 24 hours
    now = datetime.now()
    for i in range(24):
        hour_dt = now - timedelta(hours=i)
        hour_key = hour_dt.strftime("%Y-%m-%d %H:00")
        
        if hour_key in hourly_data:
            status = f"[green]✔ SUCCESS ({len(hourly_data[hour_key])} files)"
            files = ", ".join(list(hourly_data[hour_key])[:3])  # Show first 3 files
            if len(hourly_data[hour_key]) > 3:
                files += f" +{len(hourly_data[hour_key])-3} more"
        else:
            status = "[red]✖ NO DATA"
            files = "No files generated"
        
        table.add_row(hour_dt.strftime("%m-%d %H:00"), status, files)
    
    return table

def estimate_completion_time(jobs):
    """Estimate when current jobs will complete based on patterns"""
    running_jobs = [job for job in jobs if job.get("log") and not any(
        term in job["log"][-1].lower() for term in ["saved", "completed", "error", "failed"]
    )]
    
    if not running_jobs:
        return "No jobs currently running"
    
    # Estimate based on typical job duration (you can adjust this)
    typical_duration = timedelta(minutes=5)  # Adjust based on your job patterns
    
    estimates = []
    for job in running_jobs:
        if job.get("start_time"):
            elapsed = datetime.now() - job["start_time"]
            remaining = typical_duration - elapsed
            if remaining.total_seconds() > 0:
                estimates.append(f"{job['job_id']}: ~{remaining.seconds//60}m {remaining.seconds%60}s")
            else:
                estimates.append(f"{job['job_id']}: Should complete soon")
    
    return "\n".join(estimates) if estimates else "All jobs should complete soon"

def make_summary_table(jobs):
    table = Table(title="🕒 Crontab Execution Summary (Live)")
    table.add_column("Job ID", style="cyan", no_wrap=True)
    table.add_column("Mode", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("Progress", style="yellow")
    table.add_column("Last Log Line", style="green")

    for job in jobs:
        last_line = job["log"][-1] if job["log"] else "N/A"
        
        # Determine status
        if "completed" in last_line.lower() or "json data saved" in last_line.lower():
            status = "[green]✔ SUCCESS"
            progress = "[green]100% Complete"
        elif "warning" in last_line.lower():
            status = "[yellow]⚠ WARNING"
            progress = "[yellow]Check required"
        elif "processing" in last_line.lower() or "started" in last_line.lower():
            status = "[blue]🔄 RUNNING"
            # Estimate progress based on time elapsed
            if job.get("start_time"):
                elapsed = datetime.now() - job["start_time"]
                if elapsed.total_seconds() < 300:  # Less than 5 minutes
                    progress_pct = min(90, (elapsed.total_seconds() / 300) * 100)
                    progress = f"[blue]{progress_pct:.0f}% Running..."
                else:
                    progress = "[blue]Running (long job)"
            else:
                progress = "[blue]Running..."
        else:
            status = "[red]✖ ERROR"
            progress = "[red]Failed"
        
        table.add_row(
            job["job_id"], 
            job["mode"], 
            status, 
            progress, 
            last_line[:40]
        )
    
    return table

def make_status_panel(jobs):
    """Create a status panel with execution info"""
    completion_est = estimate_completion_time(jobs)
    running_count = len([j for j in jobs if "🔄 RUNNING" in str(j)])
    success_count = len([j for j in jobs if "json data saved" in str(j.get("log", [""])[-1]).lower()])
    
    status_text = f"""
[bold]Current Status:[/bold]
• Running Jobs: {running_count}
• Successful: {success_count}
• Last Update: {datetime.now().strftime('%H:%M:%S')}

[bold]Estimated Completion:[/bold]
{completion_est}

[dim]Press Ctrl+C to exit[/dim]
"""
    return Panel(status_text, title="📊 Execution Status", border_style="blue")

def main():
    console.print("[bold underline]🔍 Enhanced Real-time Crontab Monitor\n")
    try:
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                # Create layout
                layout = Layout()
                layout.split_column(
                    Layout(make_status_panel(parse_log(LOG_PATH)), size=8),
                    Layout(make_summary_table(parse_log(LOG_PATH))),
                    Layout(make_hourly_timeline_table(), size=12)
                )
                
                live.update(layout)
                time.sleep(1)
                
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting real-time monitor.")

if __name__ == "__main__":
    main()