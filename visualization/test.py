with open('ilya.csv', 'r', encoding='utf-8') as f:
    data = f.read().split('\n')
for s in data:
    if s.count(';') != 2:
        print(s, end='')
