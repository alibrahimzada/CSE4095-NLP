import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer

WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

data_path = "cleaned_data_for_ctm.csv"
data = pd.read_csv(data_path).dropna()

# Loading the model
model_name = "dbmdz/bert-base-turkish-cased"
model = SentenceTransformer(model_name, device='cuda')

# creating embeddings
embeddings = model.encode([WHITESPACE_HANDLER(i) for i in data['text'].values.tolist()])

#saving embeddings
np.save('text_embeddings.npy', embeddings)