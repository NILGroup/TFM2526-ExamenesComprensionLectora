import json
with open('gemma4_few_shot.ipynb', 'r') as f:
    notebook = json.load(f)
if 'widgets' in notebook.get('metadata', {}):
    del notebook['metadata']['widgets']
with open('gemma4_few_shot_cleaned.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)

with open('qwen35_fine_tuning.ipynb', 'r') as f:
    notebook = json.load(f)
if 'widgets' in notebook.get('metadata', {}):
    del notebook['metadata']['widgets']
with open('qwen35_fine_tuning_cleaned.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)   