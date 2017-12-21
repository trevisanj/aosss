from . import rainbow
import numpy as np

__all__ = ["spectrum_to_rgb"]

def spectrum_to_rgb(spectrum, visible_range=None, method=1):
    """Takes weighted average of rainbow colors RGB's using spectrum.y as weights

    Args:
        spectrum: f311.Spectrum object
        visible_range: (default: [4000, 7000]) (angstrom)
          if passed, affine-transforms the rainbow colors
        method --
          0: rainbow colors
          1: RGB (reproduces better the colors of the stars in the sky)

    Returns:
        np.array: [red, green, blue] where values range from 0 to 1
    """

    if visible_range is None:
        visible_range = [4000, 7000]

    if len(visible_range) < 2:
        raise RuntimeError("Invalid visible range: {0!s}".format(visible_range))
    if visible_range[1] <= visible_range[0]:
        raise RuntimeError(
            "Second element of visible range ({0!s}) must be greater than first element".format(
                visible_range))

    if method == 1:
        # new color system splitting visible range in three
        dl = float(visible_range[1] - visible_range[0]) / 3
        ranges = np.array(
            [[visible_range[0] + i * dl, visible_range[0] + (i + 1) * dl] for i in range(3)])
        colors = np.array([(0., 0., 1.), (0., 1., 0.), (1., 0., 0.)])  # blue, green, red

    elif method == 0:
        ll0 = rainbow.rainbow_colors[0].l0
        llf = rainbow.rainbow_colors[-1].lf
        ftrans = lambda lold: visible_range[0] + (visible_range[1] - visible_range[0]) / (
                              llf - ll0) * (lold - ll0)

        colors, ranges = [], []
        for color in rainbow.rainbow_colors:
            colors.append(color.rgb)
            ranges.append([ftrans(color.l0), ftrans(color.lf)])

    else:
        raise RuntimeError("Unknown method: {0!s}".format(method))

    n = len(ranges)
    weights = np.zeros(n)
    maxy = np.max(spectrum.y[np.logical_and(spectrum.x >= visible_range[0], spectrum.x <= visible_range[1])])
    for i, (color, range_) in enumerate(zip(colors, ranges)):
        bool_mask = np.logical_and(spectrum.x >= range_[0], spectrum.x <= range_[1])
        num_points = np.sum(bool_mask)
        weights[i] = 0 if num_points == 0 else np.sum(spectrum.y[bool_mask]) / (maxy * num_points)

    t = np.max(weights)
    if t > 0:
        weights /= t

    ret = np.zeros(3)
    for weight, color in zip(weights, colors):
        ret += weight*color

    m = np.max(ret)
    if m > 0:
        ret /= m

    return ret

