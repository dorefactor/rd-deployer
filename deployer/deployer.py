#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import json
from collections import defaultdict
import os
import subprocess
import sys
from pathlib import Path

# -----------------------------
# RegularOrchestratorClient
# -----------------------------


class RegularOrchestratorClient():

    def __init__(self, api_url):
        self.__api_url = api_url

    def get_deployment_order_by_id(self, id):

        api_resource = '{0}/deployment-orders/{1}'.format(
            self.__api_url, id)

        response = requests.get(api_resource)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

# -----------------------------
# File
# -----------------------------


class File():

    def write_json_file(self, filename, content):

        exists_file = os.path.isfile(filename)

        if exists_file:
            os.remove(filename)

        file = open(filename, "w+")
        file.write(json.dumps(content, indent=4))
        file.close()

# -----------------------------
# AnsibleInventory
# -----------------------------


class AnsibleInventory():

    api_url = None
    deployment_order_id = None

    def __init__(self):
        self.__inventory_filename = 'inventory.json'
        self.__extra_vars_filename = 'extra-vars.json'
        # self.__extra_vars_filename = '{0}/{1}'.format(str(Path.home()), '/cache/extra-vars.json')
        self.__file = File()

    def is_inventory_exists(self):
        return os.path.isfile(self.__inventory_filename)

    def write_inventory(self):
        inventory = self.__build_inventory()
        self.__file.write_json_file(self.__inventory_filename, inventory)

    def __build_inventory(self):
        regular_orchestrator_client = RegularOrchestratorClient(self.api_url)
        deployment_order = regular_orchestrator_client.get_deployment_order_by_id(
            self.deployment_order_id)

        inventory = {}
        group = {}
        hosts = []
        hosts_variables = {
            "ansible_port": 22,
            "ansible_python_interpreter": "/usr/bin/python3"
        }

        for host_setup in deployment_order['hostsSetup']:
            for host in host_setup['hosts']:
                hosts.append(host['ip'])
                hosts_variables['ansible_user'] = host['username']
                hosts_variables['ansible_ssh_pass'] = host['password']
                hosts_variables['ansible_sudo_pass'] = host['password']

        group['hosts'] = hosts
        group['vars'] = hosts_variables
        inventory[host_setup['tag']] = group

        self.__build_extra_variables(deployment_order)

        return inventory

    def __build_empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    def __build_extra_variables(self, deployment_order):
        application = deployment_order['application']
        application_setup = application['applicationSetup']

        ports = [('{0}:{1}'.format(key, value))
                 for key, value in application_setup['ports'].items()]
        environment_variables = [('{0}: {1}'.format(
            key, value)) for key, value in application_setup['environmentVariables'].items()]

        docker = {
            'container_name': application['name'],
            'image': application_setup['image'],
            'ports': ports,
            'environment_variables': environment_variables
        }

        extra_variables = {
            'application_name': application['name'],
            'docker': docker,
            'playbook_path': '../playbooks/docker-application/playbook.yml'
        }

        self.__file.write_json_file(
            self.__extra_vars_filename, extra_variables)

# -----------------------------
# Command
# -----------------------------


class Command():

    def __init__(self):
        self.__ansible_inventory = AnsibleInventory()
        self.__initialize_commands()

    def __initialize_commands(self):
        # read command line arguments
        arguments_parser = argparse.ArgumentParser()
        arguments_parser.add_argument('--build-inventory', action='store_true')
        arguments_parser.add_argument('--deployment-order-id')
        arguments_parser.add_argument('--api-url')
        arguments_parser.add_argument('--execute', action='store_true')
        self.__arguments = arguments_parser.parse_args()

    def run(self):
        if self.__arguments.build_inventory:
            self.__run_build_command()

        if self.__arguments.execute:
            self.__run_execute_command()

    def __run_build_command(self):
        if not self.__arguments.deployment_order_id:
            print("No argument `--deployment-order-id` was provided")
            return

        if not self.__arguments.api_url:
            print("No argument `--api-url` was provided")
            return

        # Set inventory properties
        self.__ansible_inventory.api_url = self.__arguments.api_url
        self.__ansible_inventory.deployment_order_id = self.__arguments.deployment_order_id

        self.__ansible_inventory.write_inventory()

        if not self.__ansible_inventory.is_inventory_exists():
            sys.exit(-1)

    def __run_execute_command(self):
        if self.__arguments.execute:

            if not self.__ansible_inventory.is_inventory_exists():
                sys.exit(-1)
                return

            process = subprocess.Popen(['ANSIBLE_CONFIG=deployer/ansible.cfg ansible-playbook -i deployer/inventory.py deployer/playbook.yml --extra-vars "@extra-vars.json"'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True)

            # -----------------------------------------------------------------------
            # Do not wait till process finish, start displaying output immediately
            # -----------------------------------------------------------------------
            while True:
                line = process.stdout.readline()
                if line == b'' and process.poll() != None:
                    break
                sys.stdout.write(line.decode('utf-8'))
                sys.stdout.flush()

            (output, error) = process.communicate()
            exit_code = process.returncode

            sys.exit(self.__build_exit_code(exit_code))

    def __build_exit_code(self, exit_code):
        # -----------------------------
        # Ansible Playbook Exit Codes
        # -----------------------------
        # *0* -- OK or no hosts matched
        # *1* -- Error
        # *2* -- One or more hosts failed
        # *3* -- One or more hosts were unreachable
        # *4* -- Parser error
        # *5* -- Bad or incomplete options
        # *99* -- User interrupted execution
        # *250* -- Unexpected error
        if (exit_code in [1, 2, 3, 4, 5, 99, 250]):
            return -1

        return 0

# -----------------------------
# Main
# -----------------------------


def main():
    # Read command line arguments
    command = Command()
    command.run()


if __name__ == '__main__':
    main()
