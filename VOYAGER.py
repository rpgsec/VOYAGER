import os
import subprocess
import csv
import requests
import threading
import platform
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from tqdm import tqdm

os_name = platform.system()
print("Operating System: ", os_name)

if os_name == "Windows":
    path_wordlist_path = "C:\\auto\\wordlist\\yahoo.txt"
    vhost_wordlist_path = "C:\\auto\\Wordlist\\vhosts_wordlist_test.txt"
    base_directory = os.path.join("C:\\", "auto")

    print(r"""
      
              //-A-\\
        ___---=======---___
    (=__\\    /.. ..\    //__=)
           ---\__O__/---
              VOYAGER

    """)
else: 
    # Get the current working directory
    current_directory = os.getcwd()

    # Create the complete paths using the current directory and relative paths
    path_wordlist_path = os.path.join(current_directory, "Wordlist/wordlist.txt")
    vhost_wordlist_path = os.path.join(current_directory, 'Wordlist/vhosts_wordlist_test.txt')
    base_directory = os.path.join(current_directory)

    # path_wordlist_path = "/Users/rpuri/Desktop/Hackathon/Wordlist/wordlist.txt"
    # vhost_wordlist_path = '/Users/rpuri/Desktop/Hackathon/Wordlist/vhosts_wordlist_main.txt'
    # base_directory = '/Users/rpuri/Desktop/Hackathon' 

    print(r"""
      
              //-A-\\
        ___---=======---___
    (=__\\    /.. ..\    //__=)
           ---\__O__/---
              VOYAGER

    """)

def print_yellow(prompt_text):
    print("\033[93m" + prompt_text + "\033[0m", end='')

# Helper functions
def is_valid_domain(domain):
    if "://" not in domain:
        domain = "http://" + domain
    try:
        result = urlparse(domain)
        return bool(result.netloc)
    except ValueError:
        return False

def create_csv_output(output_file, csv_output_file):
    with open(output_file, 'r') as file:
        lines = file.readlines()

    with open(csv_output_file, 'w') as csvfile:
        fieldnames = ["Status", "Size", "Words", "URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        status_parts = {}

        for line in lines:
            # Remove unwanted characters
            stripped_line = line.replace('[2K', '').replace('[0m', '')

            if '[Status:' in stripped_line:
                # Split fields by ',' to extract information
                info_parts = stripped_line.replace('[', '').replace(']', '').split(',')
                status_parts = {part.split(':')[0].strip(): part.split(':')[1].strip() for part in info_parts}
            elif '| URL |' in stripped_line:
                # Extract URL
                url = stripped_line.replace('| URL |', '').strip()

                # Write to CSV only when all parts are available
                if status_parts:
                    writer.writerow({
                        "Status": status_parts.get('Status'),
                        "Size": status_parts.get('Size'),
                        "Words": status_parts.get('Words'),
                        "URL": url,
                    })
                    # Empty the dictionary for the next set of values
                    status_parts = {}

def remove_empty_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path): 
            if os.path.getsize(file_path) == 0:
                os.remove(file_path)
                #print(f"Deleted empty file: {file_path}")

def execute_command(cmd, tool_name, print_completed=True):   # Changed here
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if print_completed:
                tqdm.write(f"{tool_name} completed.")
            return True
        else:
            tqdm.write(f"Error occurred while running {tool_name}: {result.stderr}")
            return False
    except Exception as e:
        tqdm.write(f"Exception occurred while running {tool_name}: {str(e)}")
        return False

def run_subfinder(target_domain, output_dir):
    # tqdm.write("Starting Subfinder...")
    output_path = os.path.join(output_dir, 'subfinder_output.txt')
    cmd = f"subfinder -d {target_domain} -o {output_path}"
    return execute_command(cmd, "Subfinder")

def run_tool(input_path, output_dir, tool):
    tqdm.write(f"Starting {tool}...")
    if tool == 'naabu':
        output_file = "naabu_output.csv"
        cmd = f'naabu -l {input_path} -o {output_dir}/{output_file} -p 443,4443 -csv -rate 10000 -retries 1 -warm-up-time 0 -c 50'
    elif tool == 'httprobe':
        output_file = "httprobe_output.txt"
        cmd = f'cat {input_path} | httprobe -c 50 -t 500 -p 443,4443'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if not result.stdout:
            tqdm.write(f"No output from httprobe for {input_path}.")
        else:
            # Remove 'http://' and 'https://' from the output
            stripped_output = result.stdout.replace("http://", "").replace("https://", "")
            with open(os.path.join(output_dir, output_file), 'w') as outfile:
                outfile.write(stripped_output)
        return result.returncode == 0    
    else:
        raise ValueError('Invalid tool. Please select between "naabu" and "httprobe"')
    return execute_command(cmd, tool)

# the rest of your functions...
def run_ffuf(subdomain, path_wordlist_path, output_file):
    cmd = f'ffuf -mode clusterbomb -w "{path_wordlist_path}":WORD -u "https://{subdomain}/WORD" -v -r -mc 200,403,401 -of csv -t 100'
    #cmd = f'ffuf -mode clusterbomb -w "{path_wordlist_path}":WORD -u "https://{subdomain}/WORD" -r -mc 200,403,401 -t 100 | grep "| URL"'
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            with open(output_file, 'a') as file:
                file.write(result.stdout)
        else:
            tqdm.write(f"Error occurred while running ffuf for {subdomain}: {result.stderr}")
    except Exception as e:
        tqdm.write(f"Exception occurred while running ffuf for {subdomain}: {str(e)}")
    
    
def run_waybackurls_others(subdomain, output_dir):
    output_path = os.path.join(output_dir, f"waybackurls_{subdomain.replace('.', '_')}.txt")
    cmd = f'echo {subdomain} | waybackurls > {output_path}'
    result = execute_command(cmd, "Waybackurls", print_completed=False)
    
    return result

def run_waybackurls_windows(subdomain, output_dir):
    output_path = os.path.join(output_dir, f"waybackurls_{subdomain.replace('.', '_')}.txt")
    cmd = f"waybackurls {subdomain} > {output_path}"
    result = execute_command(cmd, "Waybackurls", print_completed=False)
    
    return result

# write_lock = threading.Lock()

# def run_waybackurls_windows(subdomain, output_dir):
#     with write_lock:
#         output_path = os.path.join(output_dir, f"waybackurls_{subdomain.replace('.', '_')}.json")
#         cmd = f"waybackurls {subdomain} > {output_path}"
#     result = execute_command(cmd, "Waybackurls", print_completed=False)
    
#     return result

def check_vhost(vhost, subdomain, results_file, results_file_lock):
    for host in [f"{vhost}.{subdomain}", f"{vhost}-{subdomain}"]:
        headers = {"Host": host}
        try:
            response = requests.get(f"https://{subdomain}", headers=headers, timeout=1)
            if response.status_code in [200, 302, 401, 403]:
                message = f"Status {response.status_code} from {host}. Needs investigation."
                with results_file_lock:
                    results_file.write(message + '\n')
        except (requests.ConnectionError, requests.Timeout, requests.TooManyRedirects):
            pass

def vhost_scan(naabu_output_path, vhost_output_dir):
    with open(vhost_wordlist_path, 'r') as file:
        vhosts = file.read().splitlines()
    with open(naabu_output_path, 'r') as naabu_file:
        naabu_lines = [line[0] for line in csv.reader(naabu_file)]
    vhost_subdomain_pairs = list(set((vhost, subdomain) for vhost in vhosts for subdomain in naabu_lines))
    results_output_file = os.path.join(vhost_output_dir, "vhost_scan_results.txt")
    results_file_lock = threading.Lock()
    num_requests = len(vhost_subdomain_pairs)
    with open(results_output_file, 'w') as results_file:
        with tqdm(total=num_requests, desc="Vhost Scanning", unit="req", dynamic_ncols=True) as progress_bar:
            for vhost, subdomain in vhost_subdomain_pairs:
                check_vhost(vhost, subdomain, results_file, results_file_lock)
                progress_bar.update(1)

# Main code
print_yellow("Please enter the target domain: ")
target_domain = input()
if not is_valid_domain(target_domain):
    print("Invalid domain")
    exit(1)

print_yellow("Please enter the name of the new folder: ")
directory_name = input()
print_yellow("Please enter the number of threads to use (e.g. 10): ")
num_threads = int(input())

print_yellow("Please enter the tool to use (naabu or httprobe): ")
chosen_tool = input()

print_yellow("Do you want to run the Waybackurls function? (yes or no): ")
include_waybackurls = input().lower() == 'yes'

# Create directories
dirs = ["", "subfinder_results", f"{chosen_tool}_results", "Vhost_results", "ffuf_results"]
if include_waybackurls:
    dirs.append("waybackurls_results")
for d in tqdm(dirs, desc="Creating directories"):
    os.makedirs(os.path.join(base_directory, directory_name, d), exist_ok=True)

if run_subfinder(target_domain, os.path.join(base_directory, directory_name, "subfinder_results")):
    tool_input = os.path.join(base_directory, directory_name, "subfinder_results", "subfinder_output.txt")
    if run_tool(tool_input, os.path.join(base_directory, directory_name, f"{chosen_tool}_results"), chosen_tool):
        #tool_output = os.path.join(base_directory, directory_name, f"{chosen_tool}_results", f"{chosen_tool}_output.csv") # Change extension for httprobe if necessary
        tool_output = os.path.join(base_directory, directory_name, f"{chosen_tool}_results", f"{chosen_tool}_output.{'csv' if chosen_tool == 'naabu' else 'txt'}") 
        ffuf_output_file = os.path.join(base_directory, directory_name, "ffuf_results", "ffuf_results.csv")
        with open(tool_output, 'r') as tool_output_file:
            if chosen_tool == 'naabu':
                subdomains = [line[0] for line in csv.reader(tool_output_file)]
            elif chosen_tool == 'httprobe':
                subdomains = [line.strip() for line in tool_output_file]

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            list(tqdm(executor.map(lambda subdomain: run_ffuf(subdomain, path_wordlist_path, ffuf_output_file), subdomains), total=len(subdomains), desc="Running ffuf"))
            if include_waybackurls:
                # tqdm.write("Starting waybackurls...")
                if os_name == "Windows":
                    list(tqdm(executor.map(lambda subdomain: run_waybackurls_windows(subdomain, os.path.join(base_directory, directory_name, "waybackurls_results")), subdomains), total=len(subdomains), desc="Running waybackurls"))
                else:
                    list(tqdm(executor.map(lambda subdomain: run_waybackurls_others(subdomain, os.path.join(base_directory, directory_name, "waybackurls_results")), subdomains), total=len(subdomains), desc="Running waybackurls"))
                remove_empty_files(os.path.join(base_directory, directory_name, "waybackurls_results"))
        

        csv_ffuf_output_file = ffuf_output_file.replace('.txt', '.csv') 
        create_csv_output(ffuf_output_file, csv_ffuf_output_file)
        vhost_scan(tool_output, os.path.join(base_directory, directory_name, "Vhost_results"))
else:
    tqdm.write("Error: Subfinder did not complete successfully. Exiting.")
