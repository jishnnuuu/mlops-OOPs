import sys
import os
import json

with open("params.json", "r") as f:
    params = json.load(f)

lr = params["lr"]

with open(os.path.join("dataset", "processed_data.txt"), "r") as f:
    data = f.read()

model = f"Model trained on data: {data} with lr={lr}"

with open("model.txt", "w") as f:
    f.write(model)
