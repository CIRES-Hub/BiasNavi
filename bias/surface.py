from bias import fairlens as fl


def draw_multi_dist_plot(data, target, attrs):
    figures = fl.plot.mult_distr_plot(data, target, attrs)
    return figures
