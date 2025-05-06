import asyncio

from utils.llm import GPT4Turbo
from utils.templates import DOCS_SHELL_ONLY
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from aiopslab.orchestrator import Orchestrator


class Agent:
    def __init__(self):
        self.history = []
        self.llm = GPT4Turbo()

    def init_context(self, problem_desc: str, instructions: str, apis: str):
        """Initialize the context for the agent."""

        self.shell_api = self._filter_dict(apis, lambda k, _: "exec_shell" in k)
        self.submit_api = self._filter_dict(apis, lambda k, _: "submit" in k)
        stringify_apis = lambda apis: "\n\n".join(
            [f"{k}\n{v}" for k, v in apis.items()]
        )

        self.system_message = DOCS_SHELL_ONLY.format(
            prob_desc=problem_desc,
            shell_api=stringify_apis(self.shell_api),
            submit_api=stringify_apis(self.submit_api),
        )

        self.task_message = instructions

        self.history.append({"role": "system", "content": self.system_message})
        self.history.append({"role": "user", "content": self.task_message})

    async def get_action(self, input) -> str:
        """Wrapper to interface the agent with OpsBench.

        Args:
            input (str): The input from the orchestrator/environment.

        Returns:
            str: The response from the agent.
        """
        self.history.append({"role": "user", "content": input})
        response = self.llm.run(self.history)
        self.history.append({"role": "assistant", "content": response[0]})
        return response[0]

    def _filter_dict(self, dictionary, filter_func):
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}


if __name__ == "__main__":
    
    print("test")
    
    agent = Agent()

    orchestrator = Orchestrator()
    orchestrator.register_agent(agent, name="gpt-w-shell")

    pids = [
        "k8s_target_port-misconfig-localization-1",
        "k8s_target_port-misconfig-localization-2",
        "k8s_target_port-misconfig-localization-3",
        "auth_miss_mongodb-localization-1",
        "revoke_auth_mongodb-localization-1",
        "revoke_auth_mongodb-localization-2",
        "user_unregistered_mongodb-localization-1",
        "user_unregistered_mongodb-localization-2",
        "misconfig_app_hotel_res-localization-1",
        "scale_pod_zero_social_net-localization-1",
        "assign_to_non_existent_node_social_net-localization-1",
        "container_kill-localization",
        "pod_failure_hotel_res-localization-1",
        "pod_kill_hotel_res-localization-1",
        "network_loss_hotel_res-localization-1",
        "network_delay_hotel_res-localization-1",
        "astronomy_shop_ad_service_failure-localization-1",
        "astronomy_shop_ad_service_high_cpu-localization-1",
        "astronomy_shop_ad_service_manual_gc-localization-1",
        "astronomy_shop_cart_service_failure-localization-1",
        "astronomy_shop_image_slow_load-localization-1",
        "astronomy_shop_kafka_queue_problems-localization-1",
        "astronomy_shop_loadgenerator_flood_homepage-localization-1",
        "astronomy_shop_payment_service_failure-localization-1",
        "astronomy_shop_payment_service_unreachable-localization-1",
        "astronomy_shop_product_catalog_service_failure-localization-1",
        "astronomy_shop_recommendation_service_cache_failure-localization-1",
        "wrong_bin_usage-localization-1",
        "operator_overload_replicas-localization-1",
        "operator_non_existent_storage-localization-1",
        "operator_invalid_affinity_toleration-localization-1",
        "operator_security_context_fault-localization-1",
        "operator_wrong_update_strategy-localization-1",
    ]
    scores = []
    for pid in pids:
        problem_desc, instructs, apis = orchestrator.init_problem(pid)
        agent.init_context(problem_desc, instructs, apis)
        problem_res = asyncio.run(orchestrator.start_problem(max_steps=10))
        results = problem_res["results"]
        scores.append(results["score"])
    
    print(sum(scores) / len(scores)) # score = 0.333


