from pathlib import Path
from collections import Counter
import yaml

root = Path(r"C:\Users\User\Desktop\Nexora-AI\training\ppe-4class")
names = yaml.safe_load((root / "data.yaml").read_text())["names"]
print("classes:", names)

for split in ["train", "valid", "test"]:
    c = Counter()
    for f in (root / split / "labels").glob("*.txt"):
        for line in f.read_text().splitlines():
            if line.strip():
                c[int(line.split()[0])] += 1
    print(split, {names[k]: v for k, v in sorted(c.items())})