import json
import os

import docker
import yaml
from django.conf import settings
from django.utils import timezone

from projects.models import BuildResultE, EnvironmentVariable


class CIRunner:

    def __init__(self, project, build):
        self.project = project
        self.build = build
        self.configuration = None
        self.load_configuration()
        self.client = docker.from_env()
        self.container = None

    def load_configuration(self):
        with open(os.path.join(self.project.local_path, settings.CICD_MIMIC_FILE)) as f:
            self.configuration = yaml.safe_load(f)

    def start_container(self, variables):
        self.container = self.client.containers.run(
            self.configuration["image"], "sleep infinity", detach=True,
            volume_driver='local',
            volumes={self.project.local_path: {"bind": "/home/app", "mode": "ro"}},
            working_dir='/home/app',
            environment=variables
        )

    def stop_container(self):
        self.container.stop()
        self.container.remove()

    def run_pipeline(self):
        data = {}
        results = []
        for command in self.configuration['steps']:
            output = self.container.exec_run(command)
            results.append(output.exit_code)
            data[command] = output.output.decode()
        return data, not any(results)  # exit_code == 0 means that there is no error;

    def run_ci(self):
        # before running the main container - run all services
        services = self.configuration['services']
        service_containers = []
        for service in services:
            container = self.client.containers.run(
                service["image"],
                detach=True,
                environment=service["env"],
                ports={'5432/tcp': 5432}
            )
            service_containers.append(container)
        self.build.started_at = timezone.now()
        self.build.save(update_fields=['started_at'])
        variables = self.find_env_variables()
        self.start_container(variables=variables)
        data, result = self.run_pipeline()
        self.stop_container()
        self.build.output = json.dumps(data)
        self.build.result = BuildResultE.SUCCESS.value if result else BuildResultE.FAILURE.value
        self.build.finished_at = timezone.now()
        self.build.save(update_fields=['output', 'result', 'finished_at'])
        for container in service_containers:
            container.stop()
            container.remove()

    def find_env_variables(self):
        # the ones from the yaml file
        variables = self.configuration.get('env')
        project_variables = EnvironmentVariable.objects.filter(project=self.project).all()
        for var in project_variables:
            variables.append({var.name: var.value})
        # we have a list of dict here - let's transform it to one dict (expected input for docker.run)
        # clashes possible here - but leave it for now;
        transformed_variables = {}
        for var in variables:
            transformed_variables.update(var)
        return transformed_variables
