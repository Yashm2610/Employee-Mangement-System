import os
import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

for i in range(1, 21):
    with open('git_activity.txt', 'a') as f:
        f.write(f'Contribution {i}\n')
    run('git add git_activity.txt')
    run(f'git commit -m "Activity update {i}"')

run('git add .')
run('git commit -m "Update project files"')
run('git push origin main')
