def print_to_log(log_text):
    with open("log", "a") as wf:
        wf.write(str(log_text))
    return
