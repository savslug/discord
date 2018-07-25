import json
from pprint import pprint as print
j = []
with open("history.json", "r") as f:
    j = json.load(f)
winner = {"villager": 0, "wolf": 0, "wolf_comeback": 0}
for game in j:
    winner[game["winner"]] += 1

print(winner)


# print(len(j))
