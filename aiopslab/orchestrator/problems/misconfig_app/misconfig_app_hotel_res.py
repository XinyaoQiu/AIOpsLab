# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""MongoDB storage user unregistered problem in the HotelReservation application."""

from typing import Any

from aiopslab.orchestrator.tasks import *
from aiopslab.orchestrator.evaluators.quantitative import *
from aiopslab.service.kubectl import KubeCtl
from aiopslab.service.apps.hotelres import HotelReservation
from aiopslab.generators.workload.wrk import Wrk
from aiopslab.generators.fault.inject_app import ApplicationFaultInjector
from aiopslab.session import SessionItem
from aiopslab.paths import TARGET_MICROSERVICES

from .helpers import get_frontend_url

from math import log
from sentence_transformers import SentenceTransformer, util




class MisconfigAppHotelResBaseTask:
    def __init__(self):
        self.app = HotelReservation()
        self.kubectl = KubeCtl()
        self.namespace = self.app.namespace
        self.faulty_service = "geo"
        self.payload_script = (
            TARGET_MICROSERVICES
            / "hotelReservation/wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua"
        )
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def semantic_similarity(self, agent_answer: str, human_answer: str) -> float:
        emb1 = self.model.encode(agent_answer, convert_to_tensor=True)
        emb2 = self.model.encode(human_answer, convert_to_tensor=True)
        return float(util.pytorch_cos_sim(emb1, emb2)[0][0])  # returns value between 0 and 1

    def start_workload(self):
        print("== Start Workload ==")
        frontend_url = get_frontend_url(self.app)

        wrk = Wrk(rate=10, dist="exp", connections=2, duration=10, threads=2)
        wrk.start_workload(
            payload_script=self.payload_script,
            url=f"{frontend_url}",
        )

    def inject_fault(self):
        print("== Fault Injection ==")
        injector = ApplicationFaultInjector(namespace=self.namespace)
        injector._inject(
            fault_type="misconfig_app",
            microservices=[self.faulty_service],
        )
        print(f"Service: {self.faulty_service} | Namespace: {self.namespace}\n")

    def recover_fault(self):
        print("== Fault Recovery ==")
        injector = ApplicationFaultInjector(namespace=self.namespace)
        injector._recover(
            fault_type="misconfig_app",
            microservices=[self.faulty_service],
        )
        print(f"Service: {self.faulty_service} | Namespace: {self.namespace}\n")


################## Detection Problem ##################
class MisconfigAppHotelResDetection(MisconfigAppHotelResBaseTask, DetectionTask):
    def __init__(self):
        MisconfigAppHotelResBaseTask.__init__(self)
        DetectionTask.__init__(self, self.app)

    def eval(self, soln: Any, trace: list[SessionItem], duration: float):
        print("== Evaluation ==")
        expected_solution = "Yes"

        if isinstance(soln, str):
            if soln.strip().lower() == expected_solution.lower():
                print(f"Correct detection: {soln}")
                self.add_result("Detection Accuracy", "Correct")
            else:
                print(f"Incorrect detection: {soln}")
                self.add_result("Detection Accuracy", "Incorrect")
        else:
            print("Invalid solution format")
            self.add_result("Detection Accuracy", "Invalid Format")

        return super().eval(soln, trace, duration)


################## Localization Problem ##################
class MisconfigAppHotelResLocalization(MisconfigAppHotelResBaseTask, LocalizationTask):
    def __init__(self):
        MisconfigAppHotelResBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.app)

    def eval(self, soln: Any, trace: list[SessionItem], duration: float):
        print("== Evaluation ==")

        if soln is None:
            print("Solution is None")
            self.add_result("Localization Accuracy", 0.0)
            self.results["success"] = False
            self.results["is_subset"] = False
            super().eval(soln, trace, duration)
            return self.results

        # Calculate exact match and subset
        is_exact = is_exact_match(soln, self.faulty_service)
        is_sub = is_subset([self.faulty_service], soln)

        # Determine accuracy
        if is_exact:
            accuracy = 100.0
            print(f"Exact match: {soln} | Accuracy: {accuracy}%")
        elif is_sub:
            accuracy = (len([self.faulty_service]) / len(soln)) * 100.0
            print(f"Subset match: {soln} | Accuracy: {accuracy:.2f}%")
        else:
            accuracy = 0.0
            print(f"No match: {soln} | Accuracy: {accuracy}%")

        self.add_result("Localization Accuracy", accuracy)
        super().eval(soln, trace, duration)

        self.results["success"] = is_exact or (is_sub and len(soln) == 1)
        self.results["is_subset"] = is_sub

        CS = accuracy / 100.0 # Correctness Score
        ES = 1 / (log(self.results['TTL'] + 1) + log(self.results['steps'] + 1)) # Efficiency Score
        TCS = 1 / log(self.results['in_tokens'] + self.results['out_tokens'] + 1) # Token Cost Score

        self.results["score"] = 0.8 * CS + 0.1 * ES + 0.1 * TCS

        return self.results


################## Root cause analysis Problem ##################
class MisconfigAppHotelResAnalysis(MisconfigAppHotelResBaseTask, AnalysisTask):
    def __init__(self):
        MisconfigAppHotelResBaseTask.__init__(self)
        AnalysisTask.__init__(self, self.app)

    def eval(self, soln: Any, trace: list[SessionItem], duration: float):
        print("== Evaluation ==")

        if not isinstance(soln, dict):
            print("Solution is not a dictionary")
            self.results["system_level_correct"] = False
            self.results["fault_type_correct"] = False
            self.results["success"] = False
            super().eval(soln, trace, duration)
            return self.results

        is_sys_level_correct = is_exact_match_lower(
            soln.get("system_level", ""), "Application"
        )
        is_fault_type_correct = is_exact_match_lower(
            soln.get("fault_type", ""), "Misconfiguration"
        )

        self.results["system_level_correct"] = is_sys_level_correct
        self.results["fault_type_correct"] = is_fault_type_correct
        self.results["success"] = is_sys_level_correct and is_fault_type_correct
        self.results["similarity"] = self.semantic_similarity(soln.get("root_cause", ""), "configuration file syntax error")


        CS = 1.0 if self.results["success"] else 0.0 # Correctness Score
        SS = (self.results["similarity"] + 1) / 2.0 # Similarity Score
        ES = 1 / (log(self.results['TTA'] + 1) + log(self.results['steps'] + 1)) # Efficiency Score
        TCS = 1 / log(self.results['in_tokens'] + self.results['out_tokens'] + 1) # Token Cost Score

        self.results["score"] = 0.5 * CS + 0.3 * SS + 0.1 * ES + 0.1 * TCS

        super().eval(soln, trace, duration)

        return self.results


################## Mitigation Problem ##################
class MisconfigAppHotelResMitigation(MisconfigAppHotelResBaseTask, MitigationTask):
    def __init__(self):
        MisconfigAppHotelResBaseTask.__init__(self)
        MitigationTask.__init__(self, self.app)

    def eval(self, soln: Any, trace: list[SessionItem], duration: float) -> dict:
        print("== Evaluation ==")
        super().eval(soln, trace, duration)

        # Check if all services (not only faulty service) is back to normal (Running)
        pod_list = self.kubectl.list_pods(self.namespace)
        all_normal = True

        for pod in pod_list.items:
            # Check container statuses
            for container_status in pod.status.container_statuses:
                if (
                    container_status.state.waiting
                    and container_status.state.waiting.reason == "CrashLoopBackOff"
                ):
                    print(f"Container {container_status.name} is in CrashLoopBackOff")
                    all_normal = False
                elif (
                    container_status.state.terminated
                    and container_status.state.terminated.reason != "Completed"
                ):
                    print(
                        f"Container {container_status.name} is terminated with reason: {container_status.state.terminated.reason}"
                    )
                    all_normal = False
                elif not container_status.ready:
                    print(f"Container {container_status.name} is not ready")
                    all_normal = False

            if not all_normal:
                break

        self.results["success"] = all_normal
        return self.results
