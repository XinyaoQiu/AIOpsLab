from cleanup_lambdas import delete_lambda
from deploy_lambdas import deploy_lambda
from invoke_client import invoke_function
from agent import Agent
from injectors.permission_misconf import _inject, _recover
from iam_role import recover_iam_role
import time

class PermissionMisconfFunction1:
    def __init__(self, mode):
        self.mode = mode
        self.fault_type = 'permission misconfiguration'
    
    def __string_grader(self, gt, pred) -> float:
        if gt == pred:
            return 1
        else:
            return 0

    def _confirm_running(self) -> bool:
        is_running = invoke_function("test_function_1", {"name": "Alice", "delay": 2, "load": 12})
        if is_running:
            print("[Result] Confirm_running: Service is correctly running!")
        else:
            print("[Result] Confirm_running: Service is NOT correctly running!")
        return is_running

    def _get_problem_description(self) -> str:
        return f"This is a serverless application with {self.fault_type} problem!"

    def start_workload(self):
        print("[LOG] start_workload started!")
        delete_lambda("test_function_1")
        recover_iam_role()
        deploy_lambda("test_function_1", "lambda_functions/test_function_1.py")
        for i in range(10):
            is_running = invoke_function("test_function_1", {"name": "Alice", "delay": 2, "load": 12})
            if is_running: 
                print("[LOG] start_workload completed!")
                return
            else:
                time.sleep(5)
        raise Exception("start_workload timeout!")
                
    
    def stop_workload(self):
        delete_lambda("test_function_1")

    def inject_fault(self):
        _inject()

    def detection(self):
        agent = Agent(self.mode)
        res = agent.ask(self._get_problem_description())
        if res == "Yes":
            return 1
        else:
            return 0
    
    def mitigation(self):
        agent = Agent(self.mode)
        res = agent.ask(self._get_problem_description())
        with open('problems/permission_misconf_function_1_mitigation.sh') as f:
            gt = f.read()
        return self.__string_grader(gt, res)