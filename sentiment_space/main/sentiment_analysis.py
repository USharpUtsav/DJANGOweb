import pickle

# Load label encoder
with open(r"D:\7thsemproject\MAINPROJECTFOLDER\label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)
print("Label encoder loaded successfully:", type(label_encoder))
