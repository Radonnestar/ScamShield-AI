import subprocess
import sys

for script in ["build_dataset.py", "make_banglish.py", "add_templates.py",
               "train_model.py", "score_reality.py"]:
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, script], check=True)