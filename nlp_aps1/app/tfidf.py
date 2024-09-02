import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


# Carregar o arquivo CSV
df = pd.read_csv('../scripts/athletes_data.csv')


# Remover quebras de linha e outros espaços indesejados de todas as colunas
df = df.apply(lambda x: x.str.replace('\n', ' ').str.strip())

df['info'] = df.drop(columns=['Name']).apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
df=df.dropna()

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['info'])

# Transform the query into the TF-IDF space
query = 'Patricia'
query_vector = vectorizer.transform([query])

# Calculate cosine similarity between the query and all entries in the TF-IDF matrix
scores = np.array(X.dot(query_vector.T).todense()).flatten()
df['Relevance Score'] = scores

threshold = 0.01
filtered_df = df[df['Relevance Score'] >= threshold]

# Sort the results by relevance score
sorted_df = filtered_df.sort_values(by='Relevance Score', ascending=False)

    # Collect and print the results
results = []
results.append(sorted_df['Name'].values)
results.append(sorted_df['Relevance Score'].values)
results = np.array(results).T
print(results[0])
