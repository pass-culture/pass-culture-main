def compose (*functions):
    def inner(arg):
        for f in reversed(functions):
            if f:
                arg = f(arg)
        return arg
    return inner
