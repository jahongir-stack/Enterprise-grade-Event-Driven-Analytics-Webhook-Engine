from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for project in sorted(root.iterdir()):
    if not project.is_dir() or not (project/'test_core.py').exists(): continue
    print(f'\n=== {project.name} ===',flush=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s',str(project),'-p','test_core.py','-v'],cwd=project,check=True)
print('All project tests passed.')
