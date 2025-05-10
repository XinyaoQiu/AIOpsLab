from problems.permission_misconf_function_1 import PermissionMisconfFunction1 as Problem

problem = Problem('shell')

problem.start_workload()
problem.inject_fault()

problem.detection()
problem.mitigation()

problem.stop_workload()
