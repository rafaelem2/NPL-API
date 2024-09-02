from fastapi import FastAPI, Query
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import uvicorn

app = FastAPI()

# Load the CSV and process it
df = pd.read_csv('../scripts/athletes_data.csv')
df = df.apply(lambda x: x.str.replace('\n', ' ').str.strip())
df['info'] = df.drop(columns=['Name']).apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
df = df.dropna()

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['info'])

@app.get("/query")
def query_route(query: str = Query(..., description="Search query")):
    query_vector = vectorizer.transform([query])
    scores = np.array(X.dot(query_vector.T).todense()).flatten()
    df['Relevance Score'] = scores

    threshold = 0.01
    filtered_df = df[df['Relevance Score'] >= threshold]
    sorted_df = filtered_df.sort_values(by='Relevance Score', ascending=False)

    # Prepare results
    results = []
    for _, row in sorted_df.iterrows():
        result = {
            'title': row['Name'],
            'relevance': row['Relevance Score']
        }
        results.append(result)
    
    return {"results": results[:5], "message": "OK"}

def run():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
