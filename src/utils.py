from variables import variables


def convert_pos(x):
    screen_size = variables.screen_size
    if isinstance(x, tuple):
        return (x[0] * screen_size, x[1] * screen_size)
    else:
        return x * screen_size
