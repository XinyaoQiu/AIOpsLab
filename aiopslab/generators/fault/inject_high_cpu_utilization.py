
import subprocess
import time
from aiopslab.generators.fault.base import FaultInjector
from aiopslab.paths import BASE_DIR
from aiopslab.generators.fault.helpers import get_pids_by_name, hr_svc_process_names

class HighCPUUtilizationInjector(FaultInjector):
    def __init__(self, duration: int = 100):
        self.target_process_name = hr_svc_process_names
        self.duration = duration

    def _inject(self):
        pids = list()
        for proc_name in self.target_process_name:
            pids.extend(get_pids_by_name(proc_name))
        if not pids:
            print(f"No processes found with name {self.target_process_name}.")
            return

        print(f"Injecting high CPU utilization into processes with PIDs: {pids}")

        cpu_hog_command = f"for i in {{1..{100000 * self.duration}}}; do :; done"
        try:
            for pid in pids:
                command = f"nohup sudo nsenter -t {pid} -p -- sh -c '{cpu_hog_command}' &"
                subprocess.run(command, shell=True, check=True)
                print(f"Started CPU hog on PID {pid}.")
            
            print(f"High CPU utilization fault will run for {self.duration} seconds.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start CPU hogging process: {e}")

    def _recover(self):
        pids = get_pids_by_name(self.target_process_name)
        for pid in pids:
            try:
                command = f"pkill -P {pid}"
                subprocess.run(command, shell=True, check=True)
                print(f"Stopped high CPU utilization for PID {pid}.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to stop high CPU utilization for PID {pid}: {e}")

def main():
    injector = HighCPUUtilizationInjector(target_process_name="target_process", duration=60)
    injector.inject_high_cpu()
    injector.recover_high_cpu()

if __name__ == "__main__":
    main()
