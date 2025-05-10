
import subprocess
from aiopslab.generators.fault.base import FaultInjector
from aiopslab.service.kubectl import KubeCtl


class DNSResolutionFaultInjector(FaultInjector):
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.kubectl = KubeCtl()
        self.service_names = ["mongodb-rate", "mongodb-geo"]

    def _inject(self):
        """Prevent services from resolving domain names by modifying the resolv.conf file."""
        for service in self.service_names:
            pods = self.kubectl.list_pods(self.namespace)
            target_service_pods = [
                pod.metadata.name
                for pod in pods.items
                if service in pod.metadata.name
            ]

            if not target_service_pods:
                print(f"No pods found for service {service}")
                continue

            for pod in target_service_pods:
                print(f"Injecting DNS resolution failure into pod {pod}")

                # Backup the original resolv.conf
                backup_command = f"kubectl exec {pod} -n {self.namespace} -- cp /etc/resolv.conf /etc/resolv.conf.bak"
                self.kubectl.exec_command(backup_command)

                # Overwrite the resolv.conf with an empty file to prevent DNS resolution
                overwrite_command = f"kubectl exec {pod} -n {self.namespace} -- sh -c 'echo \"\" > /etc/resolv.conf'"
                result = self.kubectl.exec_command(overwrite_command)
                print(f"DNS resolution failure injected into {pod}: {result}")

    def _recover(self):
        """Recover DNS resolution by restoring the original resolv.conf file."""
        for service in self.service_names:
            pods = self.kubectl.list_pods(self.namespace)
            target_service_pods = [
                pod.metadata.name
                for pod in pods.items
                if service in pod.metadata.name
            ]

            if not target_service_pods:
                print(f"No pods found for service {service}")
                continue

            for pod in target_service_pods:
                print(f"Recovering DNS resolution for pod {pod}")

                # Restore the original resolv.conf from backup
                restore_command = f"kubectl exec {pod} -n {self.namespace} -- cp /etc/resolv.conf.bak /etc/resolv.conf"
                result = self.kubectl.exec_command(restore_command)
                print(f"DNS resolution failure recovered for {pod}: {result}")


def main():
    namespace = "your-namespace-here"
    services = ["example-service1", "example-service2"]
    injector = DNSResolutionFaultInjector(namespace)
    
    # Inject DNS resolution failure
    injector.inject_dns_resolution_failure(services)
    
    # Recover DNS resolution after some time
    # injector.recover_dns_resolution_failure(services)


if __name__ == "__main__":
    main()
