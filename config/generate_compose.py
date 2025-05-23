import yaml
from pathlib import Path
from collections import defaultdict, deque
import os

CONFIG_PATH = "../config/homelab.yml"
SERVICES_PATH = "../services"
OUTPUT_PATH = "../services"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def topological_sort(services):
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    for svc in services:
        for dep in svc.get("depends_on", []):
            graph[dep].append(svc["name"])
            in_degree[svc["name"]] += 1

    queue = deque([s["name"] for s in services if in_degree[s["name"]] == 0])
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order


def generate_compose():
    config = load_config()
    services_config = config["services"]

    # Group services by VM
    vm_services = defaultdict(list)
    for svc in services_config:
        vm_services[svc["vm"]].append(svc["name"])

    # Load service templates
    service_templates = {}
    for svc in services_config:
        path = Path(SERVICES_PATH) / f"{svc['name']}.yml"
        if not path.exists():
            raise FileNotFoundError(f"Missing service config: {path}")
        with open(path, "r") as f:
            service_templates[svc["name"]] = yaml.safe_load(f)

    # Sort services globally
    sorted_services = topological_sort(services_config)

    # Create docker-compose.yml for each VM
    for vm, svcs in vm_services.items():
        compose = {"version": "3", "services": {}}
        for svc_name in sorted_services:
            if svc_name in svcs:
                compose["services"] = service_templates[svc_name]

        output_dir = Path(OUTPUT_PATH) / vm
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "docker-compose.yml", "w") as f:
            yaml.dump(compose, f, sort_keys=False)


if __name__ == "__main__":
    generate_compose()
