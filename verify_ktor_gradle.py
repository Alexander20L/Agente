import os

path = 'uploads/ktor-main/ktor-main'
gp = os.path.join(path, 'gradle.properties')
print(f'Path: {gp}')
print(f'Exists: {os.path.exists(gp)}')

if os.path.exists(gp):
    with open(gp, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    print(f'Contains "group=io.ktor": {"group=io.ktor" in content}')
    print(f'Contains "group = io.ktor": {"group = io.ktor" in content}')
    
    # Mostrar las primeras líneas
    with open(gp, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:15]
    print("\nFirst 15 lines:")
    for i, line in enumerate(lines, 1):
        print(f"  {i}: {line.rstrip()}")
