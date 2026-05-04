import json
with open('gemma4_fine_tuning.ipynb', 'r') as f:
    notebook = json.load(f)
if 'widgets' in notebook.get('metadata', {}):
    del notebook['metadata']['widgets']
with open('gemma4_fine_tuning_cleaned.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)   