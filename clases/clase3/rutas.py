# %%
from pathlib import Path
p = Path('.')
print(p)

[x for x in p.iterdir() if x.is_dir()]
list(p.glob('**/*.py'))
