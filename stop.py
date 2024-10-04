from constants import Colors

def stop(message : str) -> None:
    print(Colors.NEGATIVE + message + Colors.STD)
    exit(-1)