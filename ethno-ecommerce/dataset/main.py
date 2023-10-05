import pandas as pd

import json

# Sample DataFrame

with open('ratings.json', 'r') as file:
    data = json.load(file)
df = pd.DataFrame(data)


filtered_df = df[(df['ProductID'] >= 1) & (df['ProductID'] <= 80)]

print(len(filtered_df))
