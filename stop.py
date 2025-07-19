from constants import Colors

def stop(message : str):
    print(Colors.NEGATIVE + message + Colors.STD)
    exit(-1)
