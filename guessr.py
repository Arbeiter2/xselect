import numpy as np
import json
import cleanup

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            # 👇️ alternatively use str()
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

with open('/home/delano/of0.json') as fp:
    of0 = json.load(fp)
cnd = cleanup.candidates(of0)
with open('/home/delano/guesses.json', 'w') as fp:
    json.dump(cnd, fp, cls=NpEncoder, indent=4)
