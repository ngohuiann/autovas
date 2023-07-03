import os
import subprocess, sys
import time
import xml.etree.ElementTree as ET
import requests

# useradd -m -g sudo -s /usr/bin/zsh test
# gvmd.sock possible location : /opt/gvm/var/run/gvmd.sock  /var/run/gvmd/gvmd.sock
# gvm-cli --gmp-username [redacted] --gmp-password [redacted] socket --socketpath /opt/gvm/var/run/gvmd.sock -X '<get_task/>'


# Set the gmp socket permission
command = "chmod 662 /var/run/gvmd/gvmd.sock"
subprocess.call(["sudo", "bash", "-c", command])
temp_filename = "/tmp/temp.txt"

# Set the GVM socket file path and command prefix
gvm_command_prefix = "gvm-cli --gmp-username [REDACTED] --gmp-password [REDACTED]"

# Build the GVM command to retrieve the task status
gvm_getTask = f"{gvm_command_prefix} socket -X '<get_tasks filter=\"apply_overrides=0 min_qod=70 sort=name first=1 rows=999\"/>'"


def NewTask():
    gvm_response = subprocess.check_output(gvm_getTask, shell=True)
    gvm_xml_response = ET.fromstring(gvm_response.decode("utf-8"))
    new_task = gvm_xml_response.find(".//task[status='New']")
    new_task_id = new_task.get('id')
    new_task_name = new_task.find('name').text
    gvm_newTask = f"{gvm_command_prefix} socket -X '<start_task task_id=\"{new_task_id}\"/>'"
    gvm_response_new = subprocess.check_output(gvm_newTask, shell=True)
    gvm_xml_response_new = ET.fromstring(gvm_response_new.decode("utf-8"))
    print(f"\033[1m\033[32mStarted new task: {new_task_name}\033[0m")

def GetTask():
    # Execute the GVM Get Tasks command and parse the response
    gvm_response = subprocess.check_output(gvm_getTask, shell=True)
    gvm_xml_response = ET.fromstring(gvm_response.decode("utf-8"))
    count_Running = len(gvm_xml_response.findall(".//task[status='Running']"))
    count_Done = len(gvm_xml_response.findall(".//task[status='Done']"))
    count_Requested = len(gvm_xml_response.findall(".//task[status='Requested']"))
    count_Queued = len(gvm_xml_response.findall(".//task[status='Queued']"))
    count_Interrupted = len(gvm_xml_response.findall(".//task[status='Interrupted']"))
    count_Stopped = len(gvm_xml_response.findall(".//task[status='Stopped']"))
    count_New = len(gvm_xml_response.findall(".//task[status='New']"))

    print(f"\033[1m\033[36mNew Task Count: {count_New}\033[0m")
    print(f"Running Task Count: {count_Running}")

    if count_Requested >= 1:
        for current_Requested in gvm_xml_response.findall(".//task[status='Requested']"):
            current_requested_id = current_Requested.get('id')
            current_requested_name = current_Requested.find('name').text
            print(f"Requested Task Count: {count_Requested}")
            print(f"Requested Task Name: {current_requested_name}")
            # print(f"Requested Task ID: {current_requested_id}")

    if count_Queued >= 1:
        for current_Queued in gvm_xml_response.findall(".//task[status='Queued']"):
            current_queued_id = current_Queued.get('id')
            current_queued_name = current_Queued.find('name').text
            print(f"Queued Task Count: {count_Queued}")
            print(f"Queued Task Name: {current_queued_name}")
            # print(f"Queued Task ID: {current_queued_id}")

    if count_Running >= 1:
        for current_Running in gvm_xml_response.findall(".//task[status='Running']"):
            current_running_id = current_Running.get('id')
            current_running_name = current_Running.find('name').text
            print(f"Running Task Name: {current_running_name}")
            # print(f"Running Task ID: {current_running_id}") 

    if count_Running == 0 and count_Requested == 0 and count_Queued == 0 and count_New >= 1:
        NewTask()
    # to run two task at once:
    # if count_Running <= 1 and count_Requested == 0 and count_Queued == 0 and count_New >= 1:
    #     NewTask()

    if count_Running == 0 and count_Queued == 0 and count_Requested == 0 and count_New == 0:
        print(f"\033[1m\033[31mStopped Task Count: {count_Stopped}\033[0m")
        print(f"\033[1m\033[31mInterrupted Task Count: {count_Interrupted}\033[0m")
        print("\033[1m\033[32mAll scans completed\033[0m")
        sys.exit()

while True:
    GetTask()
    time.sleep(60)
