from typing import Any, List, Mapping, Tuple


def experiment0(screensize: Mapping[int, Any]) -> Tuple[list, List[int], bool]:  # Single aggregation site
    """

    :param screensize:
    :param screensize: Mapping[int:
    :param Any]:

    """
    area_loc1 = [screensize[0] / 2.0, screensize[1] / 2.0]

    scale1 = [110, 110]  # assuming a 1000 by 1000 screen

    big = False

    return area_loc1, scale1, big

def experiment1(screensize: Mapping[int, Any]) -> Tuple[list, List[int], bool]:  # Two assymetrical aggregation site
    """

    :param screensize:
    :param screensize: Mapping[int:
    :param Any]:

    """
    area_loc1 = [screensize[1] / 3.5, screensize[0] / 2.0]
    area_loc2 = [screensize[1] - screensize[1] / 3.5, screensize[0] / 2.0]

    scale1 = [110, 110]  # assuming a 1000 by 1000 screen
    scale2 = [90, 90]  # assuming a 1000 by 1000 screen

    big = True

    return area_loc1, area_loc2, scale1, scale2,big

def experiment2(screensize: Mapping[int, Any]) -> Tuple[list, List[int], bool]:  # Two assymetrical aggregation site
    """

    :param screensize:
    :param screensize: Mapping[int:
    :param Any]:

    """
    area_loc1 = [screensize[1] / 3.5, screensize[0] / 2.0]
    area_loc2 = [screensize[1] - screensize[1] / 3.5, screensize[0] / 2.0]

    scale1 = [90, 90]  # assuming a 1000 by 1000 screen
    scale2 = [90, 90]  # assuming a 1000 by 1000 screen

    big = False

    return area_loc1, area_loc2, scale1, scale2,big