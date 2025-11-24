import os

project_path = "uploads/ktor-main/ktor-main"

all_files = []
for root, dirs, files in os.walk(project_path):
    for f in files:
        full = os.path.join(root, f)
        all_files.append(full.lower())

basenames = [os.path.basename(f) for f in all_files]

print(f"Total files: {len(all_files)}")
print(f"'build.gradle' in basenames: {'build.gradle' in basenames}")
print(f"'build.gradle.kts' in basenames: {'build.gradle.kts' in basenames}")
print(f"\nFirst 10 basenames containing 'gradle':")
gradle_files = [b for b in basenames if 'gradle' in b][:10]
for gf in gradle_files:
    print(f"  - {gf}")
