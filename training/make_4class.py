from pathlib import Path
import shutil
import yaml

src = Path(r"C:\Users\User\Desktop\Nexora-AI\training\ppe-workplace-v2")
dst = Path(r"C:\Users\User\Desktop\Nexora-AI\training\ppe-4class")

# old id -> new id: Boots 0->0, Helmet 4->1, Person 6->2, Vest 7->3
keep = {0: 0, 4: 1, 6: 2, 7: 3}
new_names = ["Boots", "Helmet", "Person", "Vest"]

for split in ["train", "valid", "test"]:
    (dst / split / "images").mkdir(parents=True, exist_ok=True)
    (dst / split / "labels").mkdir(parents=True, exist_ok=True)

    for img in (src / split / "images").iterdir():
        shutil.copy2(img, dst / split / "images" / img.name)

    for lbl in (src / split / "labels").glob("*.txt"):
        out = []
        for line in lbl.read_text().splitlines():
            parts = line.split()
            if parts and int(parts[0]) in keep:
                parts[0] = str(keep[int(parts[0])])
                out.append(" ".join(parts))
        (dst / split / "labels" / lbl.name).write_text(
            "\n".join(out) + ("\n" if out else "")
        )

data = {
    "path": dst.as_posix(),
    "train": "train/images",
    "val": "valid/images",
    "test": "test/images",
    "nc": 4,
    "names": new_names,
}
(dst / "data.yaml").write_text(yaml.dump(data, sort_keys=False))
print("done")