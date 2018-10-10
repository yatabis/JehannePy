from base64 import b64encode
import json


def json_update(fp, key, value):
    with open(fp, 'r') as j:
        d = json.load(j)
    d[key] = value
    with open(fp, 'w') as j:
        json.dump(d, j)


def state_change(f):
    def wrapper(obj, *args, **kwargs):
        rtn = f(obj, *args, **kwargs)
        file_path = "Jehanne_states.json"
        with open(file_path, 'w') as j:
            json.dump(vars(obj), j)
        return rtn
    return wrapper


def basic_header(usr, pwd):
    """make header of Basic Authorization."""
    token = str(b64encode(f"{usr}:{pwd}".encode('utf-8')))[2:-1]
    return {'Authorization': f"Basic {token}"}
