import json
import torch

def translate_model_to_json(w):
    for entry in w:
            w[entry] = w[entry].cpu().data.numpy().tolist()
    return json.dumps(w_glob)

def translate_json_to_model(text):
    w = json.loads(text)
    for entry in w:
        w[entry] = torch.Tensor(w[entry])
    return w