from bias.sampler import Sampler


def adapt_data(df, attr, op):
    sampler = Sampler(df, attr)
    new_data = []
    if op == "smote":
        new_data = sampler.smote()

    elif op == "oversample":
        new_data = sampler.oversample()

    elif op == "undersample":
        new_data = sampler.undersample()

    return new_data
