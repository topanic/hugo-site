#!/home/czy/.conda/envs/normal/bin/python
import subprocess
import shutil
import fileinput
import os


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}\n{stderr.decode()}")
    else:
        print(stdout.decode())

# Run hugo command in current directory
run_command("hugo")

# Update bing sitemap.xml
## Define source and destination files
source_file = os.path.join('public', 'sitemap.xml')
destination_file = os.path.join('public', 'sitemap_bing.xml')

## Copy file
shutil.copy(source_file, destination_file)

## Replace text in file
with fileinput.FileInput(destination_file, inplace=True) as file:
    for line in file:
        print(line.replace('topanic.site', 'topanic.space'), end='')


# # Run git commands
run_command("cd public && git add .")
run_command('cd public && git commit -m "Automated commit"')
run_command("cd public && git push --set-upstream origin main")
