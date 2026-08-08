from .repositories import *


def search_lsas(*,skill,start_time,end_time):
    return find_available_lsas(
        skill=skill,
        start_time=start_time,
        end_time=end_time
    )