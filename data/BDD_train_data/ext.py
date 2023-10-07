import json

with open('BDD-Instruct-v2-filtered.json', 'r') as f:
    data = json.load(f)

ls = []
with open('BDD-Instruct-v2-filtered-mov.json', 'w') as f:
    for d in data:
        d['video_id'] += '.mov'
        ls.append(d)
    json.dump(ls, f)
