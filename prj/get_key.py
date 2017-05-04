def _get():
    rf = open("key", "r")
    key = rf.read(45)
    rf.close()
    return key


def get():
    return _get()
