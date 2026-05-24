import requests

url = "https://www.formula1.com/en/results/2026/races"

r = requests.get(url)

print(r.status_code)
print(len(r.text))
print(r.text[:500])